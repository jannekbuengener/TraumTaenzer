"""
Runtime Tooling — start / stop / health / inspect

Minimal operational paths for the bootstrap runtime server.

Commands:
  start       Launch runtime_server in background and verify /health
  stop        Request clean shutdown and verify process exit
  health      Check /health reachability
  inspect-db  Inspect explicit SQLite DB path
  inspect-log Inspect explicit runtime log path
  inspect-sidepaths Scan explicit roots for shadow stores / sidepaths
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import signal
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .event_store import _FORBIDDEN_FIELDS
from .inspect_events import (
    collect_db_audit_violations,
    print_session_detail,
    print_summary,
    scan_sidepaths,
)
from .llm_adapter import _STUB_RESPONSES
from .responses import RESPONSES
from .runtime_server import _absolute_path_arg, _port_arg, _stub_mode_arg

logger = logging.getLogger(__name__)

_MAX_LOG_LINES = 200


def _configure_cli_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _read_pid_meta(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"PID file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid PID file: {path}") from exc

    if not isinstance(data, dict):
        raise RuntimeError(f"Invalid PID file structure: {path}")
    return data


def _write_pid_meta(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _request_json(method: str, url: str, payload: dict[str, Any] | None = None, timeout: float = 3.0) -> tuple[int, dict[str, Any]]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    request = Request(url, data=body, method=method, headers=headers)
    try:
        with urlopen(request, timeout=timeout) as response:
            status = response.status
            raw = response.read().decode("utf-8")
    except HTTPError as exc:
        raw = exc.read().decode("utf-8")
        try:
            return exc.code, json.loads(raw)
        except json.JSONDecodeError:
            return exc.code, {"error": "NON_JSON_ERROR_RESPONSE"}
    except (URLError, OSError) as exc:
        raise RuntimeError(type(exc).__name__) from exc

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Invalid JSON response") from exc
    if not isinstance(data, dict):
        raise RuntimeError("Invalid JSON object response")
    return status, data


def _health_url(host: str, port: int) -> str:
    return f"http://{host}:{port}/health"


def _shutdown_url(host: str, port: int) -> str:
    return f"http://{host}:{port}/shutdown"


def _runtime_command(args: argparse.Namespace) -> list[str]:
    return [
        sys.executable,
        "-m",
        "harness.runtime_server",
        "--db",
        str(args.db),
        "--log",
        str(args.log),
        "--host",
        args.host,
        "--port",
        str(args.port),
        "--stub-mode",
        "NONE" if args.stub_mode is None else args.stub_mode.value,
    ]


def _health_available(host: str, port: int, timeout: float = 1.0) -> bool:
    try:
        status, _payload = _request_json("GET", _health_url(host, port), timeout=timeout)
    except RuntimeError:
        return False
    return status == 200


def _wait_for_health(host: str, port: int, timeout_seconds: float, process: subprocess.Popen[Any]) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    last_error = "HEALTH_TIMEOUT"
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError("RUNTIME_PROCESS_EXITED_DURING_STARTUP")
        try:
            status, data = _request_json("GET", _health_url(host, port), timeout=1.0)
            if status == 200:
                return data
            last_error = data.get("error", f"HTTP_{status}")
        except RuntimeError as exc:
            last_error = str(exc)
        time.sleep(0.2)
    raise RuntimeError(last_error)


def _wait_for_exit(pid: int, timeout_seconds: float) -> bool:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if not _pid_alive(pid):
            return True
        time.sleep(0.2)
    return not _pid_alive(pid)


def _cleanup_wal_shm(db_path: Path) -> list[str]:
    violations: list[str] = []
    wal_path = Path(str(db_path) + "-wal")
    shm_path = Path(str(db_path) + "-shm")
    if wal_path.exists():
        violations.append(str(wal_path))
    if shm_path.exists():
        violations.append(str(shm_path))
    return violations


def _stop_signal() -> int:
    return signal.SIGTERM


def _extract_forbidden_log_patterns() -> list[str]:
    patterns = set(_FORBIDDEN_FIELDS)
    patterns.update({"raw_payload", "request_body", "response_body", "user_text=", "llm_output="})
    patterns.update(RESPONSES.values())
    patterns.update(_STUB_RESPONSES.values())
    return sorted(patterns)


def cmd_start(args: argparse.Namespace) -> int:
    if len({args.db, args.log, args.pid_file}) != 3:
        raise RuntimeError("--db, --log and --pid-file must be different paths.")

    if args.pid_file.exists():
        meta = _read_pid_meta(args.pid_file)
        existing_host = str(meta.get("host", args.host))
        existing_port = int(meta.get("port", args.port))
        if existing_port and _health_available(existing_host, existing_port):
            raise RuntimeError(f"Runtime already running under PID file: {args.pid_file}")
        args.pid_file.unlink()

    kwargs: dict[str, Any] = {
        "cwd": str(_repo_root()),
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }
    if os.name == "nt":
        kwargs["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200)
    else:
        kwargs["start_new_session"] = True

    process = subprocess.Popen(_runtime_command(args), **kwargs)

    try:
        health = _wait_for_health(args.host, args.port, args.startup_timeout, process)
    except Exception:
        if process.poll() is None:
            try:
                os.kill(process.pid, _stop_signal())
            except OSError:
                pass
        raise

    meta = {
        "pid": process.pid,
        "host": args.host,
        "port": args.port,
        "db_path": str(args.db),
        "log_path": str(args.log),
        "stub_mode": "NONE" if args.stub_mode is None else args.stub_mode.value,
    }
    _write_pid_meta(args.pid_file, meta)
    print(json.dumps({"status": "started", **meta, "health": health}, ensure_ascii=True))
    return 0


def cmd_stop(args: argparse.Namespace) -> int:
    meta = _read_pid_meta(args.pid_file)
    pid = int(meta.get("pid", 0))
    host = str(meta.get("host", "127.0.0.1"))
    port = int(meta.get("port", 0))
    db_path = _absolute_path_arg(str(meta.get("db_path", "")))

    if not pid:
        raise RuntimeError(f"PID file has no pid: {args.pid_file}")

    if not _health_available(host, port):
        if args.pid_file.exists():
            args.pid_file.unlink()
        print(json.dumps({"status": "already_stopped", "pid": pid}, ensure_ascii=True))
        return 0

    shutdown_requested = False
    if port:
        try:
            status, _data = _request_json("POST", _shutdown_url(host, port), payload={}, timeout=2.0)
            shutdown_requested = status == 202
        except RuntimeError:
            shutdown_requested = False

    if not shutdown_requested:
        os.kill(pid, _stop_signal())

    deadline = time.monotonic() + args.stop_timeout
    while time.monotonic() < deadline:
        if not _health_available(host, port, timeout=0.5):
            break
        time.sleep(0.2)
    else:
        raise RuntimeError("Runtime did not stop cleanly within timeout.")

    if args.pid_file.exists():
        args.pid_file.unlink()

    wal_violations = _cleanup_wal_shm(db_path)
    if wal_violations:
        raise RuntimeError(f"WAL/SHM files remain after clean stop: {wal_violations}")

    print(json.dumps({"status": "stopped", "pid": pid, "db_path": str(db_path)}, ensure_ascii=True))
    return 0


def cmd_health(args: argparse.Namespace) -> int:
    status, payload = _request_json("GET", _health_url(args.host, args.port), timeout=args.timeout)
    if status != 200:
        raise RuntimeError(payload.get("error", f"HTTP_{status}"))
    print(json.dumps(payload, ensure_ascii=True))
    return 0


def cmd_inspect_db(args: argparse.Namespace) -> int:
    if not args.db.exists():
        raise RuntimeError(f"DB not found: {args.db}")

    conn = sqlite3.connect(str(args.db), check_same_thread=False)
    try:
        violations = collect_db_audit_violations(conn)
        if violations:
            for violation in violations:
                logger.error("DB_INSPECT_VIOLATION %s", violation)
            return 1

        if args.check_only:
            print(json.dumps({"status": "ok", "db_path": str(args.db)}, ensure_ascii=True))
            return 0

        print_summary(conn, session_prefix=args.session)
        if args.session:
            print_session_detail(conn, args.session)
        return 0
    finally:
        conn.close()


def _tail_lines(path: Path, count: int) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if count <= 0:
        return lines
    return lines[-count:]


def _stdout_safe(text: str) -> str:
    encoding = sys.stdout.encoding or "utf-8"
    return text.encode(encoding, errors="replace").decode(encoding, errors="replace")


def cmd_inspect_log(args: argparse.Namespace) -> int:
    if not args.log.exists():
        raise RuntimeError(f"Log not found: {args.log}")

    tail_count = min(args.tail, _MAX_LOG_LINES)
    lines = _tail_lines(args.log, tail_count)
    text = "\n".join(lines)

    violations: list[str] = []
    for pattern in _extract_forbidden_log_patterns():
        if pattern and pattern in text:
            violations.append(pattern)

    if violations:
        for pattern in violations:
            logger.error("LOG_INSPECT_VIOLATION forbidden_pattern=%r", pattern)
        return 1

    if args.check_only:
        print(json.dumps({"status": "ok", "log_path": str(args.log), "tail_lines": len(lines)}, ensure_ascii=True))
        return 0

    print(f"Log tail from {args.log} ({len(lines)} lines):")
    for line in lines:
        print(_stdout_safe(line))
    return 0


def cmd_inspect_sidepaths(args: argparse.Namespace) -> int:
    scan_roots = [args.db.parent, args.workdir]
    if args.log is not None:
        scan_roots.append(args.log.parent)

    allowed_paths = {args.db}
    if args.log is not None:
        allowed_paths.add(args.log)
    if args.pid_file is not None:
        allowed_paths.add(args.pid_file)

    resolved_roots: list[Path] = []
    seen_roots: set[Path] = set()
    for path in scan_roots:
        resolved = path.resolve(strict=False)
        if resolved in seen_roots:
            continue
        seen_roots.add(resolved)
        resolved_roots.append(path)

    violations = scan_sidepaths(resolved_roots, allowed_paths=allowed_paths)
    if violations:
        for violation in violations:
            logger.error("SIDEPATH_VIOLATION %s", violation)
        return 1

    payload = {
        "status": "ok",
        "scan_roots": [str(path.resolve(strict=False)) for path in resolved_roots],
        "allowed_paths": [
            str(path.resolve(strict=False))
            for path in sorted(allowed_paths, key=lambda item: str(item.resolve(strict=False)))
        ],
    }
    print(json.dumps(payload, ensure_ascii=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Traumtänzer Runtime Tooling")
    subparsers = parser.add_subparsers(dest="command", required=True)

    start = subparsers.add_parser("start", help="Start runtime server in background")
    start.add_argument("--db", required=True, type=_absolute_path_arg, help="Absolute SQLite DB path.")
    start.add_argument("--log", required=True, type=_absolute_path_arg, help="Absolute runtime log path.")
    start.add_argument("--pid-file", required=True, type=_absolute_path_arg, help="Absolute PID metadata path.")
    start.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1).")
    start.add_argument("--port", type=_port_arg, default=8080, help="Bind port (default: 8080).")
    start.add_argument("--stub-mode", default="NONE", type=_stub_mode_arg, metavar="MODE")
    start.add_argument("--startup-timeout", type=float, default=10.0, help="Seconds to wait for /health (default: 10).")
    start.set_defaults(func=cmd_start)

    stop = subparsers.add_parser("stop", help="Stop runtime server via local shutdown path")
    stop.add_argument("--pid-file", required=True, type=_absolute_path_arg, help="Absolute PID metadata path.")
    stop.add_argument("--stop-timeout", type=float, default=10.0, help="Seconds to wait for clean exit (default: 10).")
    stop.set_defaults(func=cmd_stop)

    health = subparsers.add_parser("health", help="Check runtime /health")
    health.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1).")
    health.add_argument("--port", type=_port_arg, default=8080, help="Bind port (default: 8080).")
    health.add_argument("--timeout", type=float, default=3.0, help="Request timeout seconds (default: 3).")
    health.set_defaults(func=cmd_health)

    inspect_db = subparsers.add_parser("inspect-db", help="Inspect explicit SQLite DB path")
    inspect_db.add_argument("--db", required=True, type=_absolute_path_arg, help="Absolute SQLite DB path.")
    inspect_db.add_argument("--session", metavar="PREFIX", help="Optional session prefix filter.")
    inspect_db.add_argument("--check-only", action="store_true", help="Only run DB audit, no display output.")
    inspect_db.set_defaults(func=cmd_inspect_db)

    inspect_log = subparsers.add_parser("inspect-log", help="Inspect explicit runtime log path")
    inspect_log.add_argument("--log", required=True, type=_absolute_path_arg, help="Absolute runtime log path.")
    inspect_log.add_argument("--tail", type=int, default=40, help="How many trailing lines to inspect (max 200).")
    inspect_log.add_argument("--check-only", action="store_true", help="Only validate, no line output.")
    inspect_log.set_defaults(func=cmd_inspect_log)

    inspect_sidepaths = subparsers.add_parser(
        "inspect-sidepaths",
        help="Scan target directory and workdir for shadow stores / sidepaths",
    )
    inspect_sidepaths.add_argument("--db", required=True, type=_absolute_path_arg, help="Absolute SQLite DB path.")
    inspect_sidepaths.add_argument("--workdir", required=True, type=_absolute_path_arg, help="Absolute workdir root to scan.")
    inspect_sidepaths.add_argument("--log", type=_absolute_path_arg, help="Optional absolute runtime log path to allow.")
    inspect_sidepaths.add_argument("--pid-file", type=_absolute_path_arg, help="Optional absolute pid metadata path to allow.")
    inspect_sidepaths.set_defaults(func=cmd_inspect_sidepaths)

    return parser


def main(argv: list[str] | None = None) -> int:
    _configure_cli_logging()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except RuntimeError as exc:
        logger.error("%s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
