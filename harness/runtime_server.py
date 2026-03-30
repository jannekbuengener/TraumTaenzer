"""
Minimal Runtime Server — Traumtänzer Harness Bootstrap

Smallest deployable mono-process based on the existing harness components.

Goals:
  - explicit SQLite DB path (no fallback to harness/data/events.db)
  - explicit log path (no fallback to workdir logs)
  - simple reachability via HTTP /health
  - clean shutdown with EventStore.close()
  - fail-closed when no adapter/provider is configured
  - content-free app logs (no user text, no LLM output, no raw payload)

Non-goals:
  - no production readiness claim
  - no real provider integration
  - no Hetzner evidence by itself
  - no Docker / Compose / systemd

Usage:
  python -m harness.runtime_server --db /abs/path/events.db --log /abs/path/runtime.log
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import logging
import signal
import sys
import threading
import uuid
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .event_store import EventStore
from .kernel import Kernel
from .llm_adapter import StubLLMAdapter, StubMode

logger = logging.getLogger(__name__)

_MAX_JSON_BYTES = 8 * 1024


def _absolute_path_arg(value: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        raise argparse.ArgumentTypeError("Path must be absolute.")
    return path


def _port_arg(value: str) -> int:
    try:
        port = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Port must be an integer.") from exc
    if port < 1 or port > 65535:
        raise argparse.ArgumentTypeError("Port must be between 1 and 65535.")
    return port


def _configure_logging(log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    for handler in list(root.handlers):
        root.removeHandler(handler)
        handler.close()

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(formatter)

    root.setLevel(logging.INFO)
    root.addHandler(file_handler)
    root.addHandler(stderr_handler)


@dataclass(frozen=True)
class RuntimeConfig:
    db_path: Path
    log_path: Path
    host: str
    port: int
    stub_mode: StubMode | None


class RequestError(Exception):
    def __init__(self, status: HTTPStatus, code: str) -> None:
        super().__init__(code)
        self.status = status
        self.code = code


class RuntimeApp:
    """
    Session registry around the existing Harness Kernel.

    Keeps session state RAM-only. Runtime events remain content-free because the
    underlying EventStore rejects free-text fields and the Kernel never logs
    user content.
    """

    def __init__(self, config: RuntimeConfig) -> None:
        self._config = config
        self._store = EventStore(config.db_path)
        self._sessions: dict[str, Kernel] = {}
        logger.info(
            "runtime_app_init bind=%s:%s adapter=%s",
            config.host,
            config.port,
            self.adapter_mode,
        )

    @property
    def adapter_mode(self) -> str:
        return self._config.stub_mode.value if self._config.stub_mode else "NONE"

    def health(self) -> dict[str, Any]:
        return {
            "status": "ok",
            "adapter_mode": self.adapter_mode,
            "session_count": len(self._sessions),
        }

    def start_session(self) -> dict[str, Any]:
        session_id = f"runtime-{uuid.uuid4().hex[:12]}"
        kernel = Kernel(
            session_id=session_id,
            event_store=self._store,
            llm_adapter=self._build_adapter(),
        )
        self._sessions[session_id] = kernel
        logger.info("runtime_session_started session=%s", session_id[:8])
        return {
            "session_id": session_id,
            "state": kernel.state,
            "terminal": kernel.is_terminal(),
            "response": kernel.entry_text(),
        }

    def process_turn(self, session_id: str, user_text: str) -> dict[str, Any]:
        kernel = self._sessions.get(session_id)
        if kernel is None:
            raise RequestError(HTTPStatus.NOT_FOUND, "SESSION_NOT_FOUND")

        response = kernel.process_input(user_text)
        logger.info(
            "runtime_turn_processed session=%s state=%s terminal=%s",
            session_id[:8],
            kernel.state,
            kernel.is_terminal(),
        )
        return {
            "session_id": session_id,
            "state": kernel.state,
            "terminal": kernel.is_terminal(),
            "response": response,
        }

    def close(self) -> None:
        self._store.close()
        logger.info("runtime_app_closed sessions=%s", len(self._sessions))

    def _build_adapter(self) -> StubLLMAdapter | None:
        if self._config.stub_mode is None:
            return None
        return StubLLMAdapter(self._config.stub_mode)


class RuntimeHTTPServer(HTTPServer):
    allow_reuse_address = True

    def __init__(self, server_address: tuple[str, int], app: RuntimeApp) -> None:
        self.app = app
        super().__init__(server_address, RuntimeRequestHandler)

    def close_runtime(self) -> None:
        try:
            self.server_close()
        finally:
            self.app.close()


class RuntimeRequestHandler(BaseHTTPRequestHandler):
    server_version = "TraumtaenzerRuntime/0.1"
    sys_version = ""

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/health":
            self._send_json(HTTPStatus.OK, self.server.app.health())
            return
        self._send_json(HTTPStatus.NOT_FOUND, {"error": "NOT_FOUND"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        try:
            if path == "/shutdown":
                payload = self._read_json_body(allow_empty=True)
                if payload:
                    raise RequestError(HTTPStatus.BAD_REQUEST, "UNEXPECTED_FIELDS")
                if not self._client_is_loopback():
                    raise RequestError(HTTPStatus.FORBIDDEN, "LOCALHOST_ONLY")
                logger.info("runtime_shutdown_requested client=%s", self.client_address[0])
                self._send_json(HTTPStatus.ACCEPTED, {"status": "shutdown_requested"})
                threading.Thread(target=self.server.shutdown, daemon=True).start()
                return

            if path == "/v1/sessions":
                payload = self._read_json_body(allow_empty=True)
                if payload:
                    raise RequestError(HTTPStatus.BAD_REQUEST, "UNEXPECTED_FIELDS")
                self._send_json(HTTPStatus.CREATED, self.server.app.start_session())
                return

            if path == "/v1/turns":
                payload = self._read_json_body()
                session_id = payload.get("session_id")
                user_text = payload.get("user_text")
                if not isinstance(session_id, str) or not session_id.strip():
                    raise RequestError(HTTPStatus.BAD_REQUEST, "INVALID_SESSION_ID")
                if not isinstance(user_text, str):
                    raise RequestError(HTTPStatus.BAD_REQUEST, "INVALID_USER_TEXT")
                self._send_json(
                    HTTPStatus.OK,
                    self.server.app.process_turn(session_id, user_text),
                )
                return

            self._send_json(HTTPStatus.NOT_FOUND, {"error": "NOT_FOUND"})
        except RequestError as exc:
            self._send_json(exc.status, {"error": exc.code})
        except Exception as exc:
            logger.error("runtime_request_failed err=%s", type(exc).__name__)
            self._send_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {"error": "INTERNAL_RUNTIME_ERROR"},
            )

    def log_message(self, fmt: str, *args: Any) -> None:
        # Suppress BaseHTTPRequestHandler request logging to avoid accidentally
        # logging raw request lines or user payloads.
        return

    def _client_is_loopback(self) -> bool:
        try:
            return ipaddress.ip_address(self.client_address[0]).is_loopback
        except ValueError:
            return self.client_address[0] in {"localhost"}

    def _read_json_body(self, allow_empty: bool = False) -> dict[str, Any]:
        raw_len = self.headers.get("Content-Length")
        if raw_len is None:
            if allow_empty:
                return {}
            raise RequestError(HTTPStatus.BAD_REQUEST, "MISSING_CONTENT_LENGTH")

        try:
            content_length = int(raw_len)
        except ValueError as exc:
            raise RequestError(HTTPStatus.BAD_REQUEST, "INVALID_CONTENT_LENGTH") from exc

        if content_length < 0:
            raise RequestError(HTTPStatus.BAD_REQUEST, "INVALID_CONTENT_LENGTH")
        if content_length == 0:
            if allow_empty:
                return {}
            raise RequestError(HTTPStatus.BAD_REQUEST, "EMPTY_BODY")
        if content_length > _MAX_JSON_BYTES:
            raise RequestError(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "PAYLOAD_TOO_LARGE")

        raw = self.rfile.read(content_length)
        try:
            data = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RequestError(HTTPStatus.BAD_REQUEST, "INVALID_JSON") from exc

        if not isinstance(data, dict):
            raise RequestError(HTTPStatus.BAD_REQUEST, "INVALID_JSON_OBJECT")
        return data

    def _send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        response_body = json.dumps(payload, ensure_ascii=True).encode("utf-8")
        self.send_response(int(status))
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_body)))
        self.end_headers()
        self.wfile.write(response_body)


def create_runtime_server(config: RuntimeConfig) -> RuntimeHTTPServer:
    app = RuntimeApp(config)
    try:
        return RuntimeHTTPServer((config.host, config.port), app)
    except Exception:
        app.close()
        raise


def _install_signal_handlers(server: RuntimeHTTPServer) -> None:
    def _request_shutdown(signum: int, _frame: Any) -> None:
        try:
            signal_name = signal.Signals(signum).name
        except ValueError:
            signal_name = str(signum)
        logger.info("runtime_shutdown_signal signal=%s", signal_name)
        threading.Thread(target=server.shutdown, daemon=True).start()

    for sig_name in ("SIGINT", "SIGTERM"):
        sig = getattr(signal, sig_name, None)
        if sig is not None:
            signal.signal(sig, _request_shutdown)


def _stub_mode_arg(value: str) -> StubMode | None:
    if value.upper() == "NONE":
        return None
    try:
        return StubMode(value.upper())
    except ValueError as exc:
        allowed = ", ".join(["NONE", *[mode.value for mode in StubMode]])
        raise argparse.ArgumentTypeError(
            f"Invalid stub mode. Allowed: {allowed}"
        ) from exc


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Traumtänzer Harness Bootstrap Runtime Server"
    )
    parser.add_argument(
        "--db",
        required=True,
        type=_absolute_path_arg,
        help="Absolute SQLite DB path. Required; no default fallback.",
    )
    parser.add_argument(
        "--log",
        required=True,
        type=_absolute_path_arg,
        help="Absolute log file path. Required; no default fallback.",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Bind host (default: 127.0.0.1).",
    )
    parser.add_argument(
        "--port",
        type=_port_arg,
        default=8080,
        help="Bind port (default: 8080).",
    )
    parser.add_argument(
        "--stub-mode",
        default="NONE",
        type=_stub_mode_arg,
        metavar="MODE",
        help="Optional StubLLMAdapter mode. Default: NONE (missing provider -> fail-closed).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.db == args.log:
        parser.error("--db and --log must point to different files.")

    config = RuntimeConfig(
        db_path=args.db,
        log_path=args.log,
        host=args.host,
        port=args.port,
        stub_mode=args.stub_mode,
    )

    _configure_logging(config.log_path)
    logger.info(
        "runtime_bootstrap_start bind=%s:%s adapter=%s db_path=%s log_path=%s",
        config.host,
        config.port,
        "NONE" if config.stub_mode is None else config.stub_mode.value,
        config.db_path,
        config.log_path,
    )

    server: RuntimeHTTPServer | None = None
    try:
        server = create_runtime_server(config)
        _install_signal_handlers(server)
        logger.info("runtime_server_ready bind=%s:%s", config.host, config.port)
        server.serve_forever(poll_interval=0.5)
        return 0
    except KeyboardInterrupt:
        logger.info("runtime_keyboard_interrupt")
        return 0
    except Exception as exc:
        logger.error("runtime_bootstrap_failed err=%s", type(exc).__name__)
        return 1
    finally:
        if server is not None:
            server.close_runtime()
        logger.info("runtime_bootstrap_stopped")


if __name__ == "__main__":
    sys.exit(main())
