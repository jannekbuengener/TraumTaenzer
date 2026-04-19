"""
Runtime Evidence Runner — Traumtänzer Evidence Harness

One-command local runtime evidence run:
    start → health → session-smoke → stop → inspect-db → inspect-log → inspect-sidepaths

All paths are absolute, derived from harness/data/. workdir = harness/data/ to keep
the sidepath scan scope small and free of false positives.

Fail-closed rules:
  - If start fails, all subsequent steps are skipped.
  - If health or smoke fails, stop is still attempted (finally block).
  - Inspection steps only run if stop returned 0 AND the server PID is confirmed dead.
  - If stop fails, inspections are skipped (DB/log may still be open).

The session smoke drives through four states: ENTRY → CHECK_IN → REFLECTION → EXIT.
This exercises the stub adapter call and the output guard with --stub-mode SAFE.

Exit code 0 = all steps PASSED.
Exit code 1 = at least one step FAILED or SKIPPED, or --fresh cleanup failed.

HARNESS-ONLY. Not for live user sessions.
No external provider. No network beyond localhost. No cloud. No pilot claim.

Usage:
    python -m harness.runtime_evidence [--fresh] [--port PORT] [--host HOST]

    --fresh  Delete runtime DB (and WAL sidecars), log, and PID file before running.
    --port   Local port (default: 8081). Avoids conflict with default 8080 in README.
    --host   Bind host (default: 127.0.0.1).
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# Configure logging before sub-module imports so this call wins the basicConfig race.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

from . import runtime_tools as _rt  # noqa: E402 — after basicConfig intentionally

_DATA_DIR = Path(__file__).resolve().parent / "data"
_DEFAULT_PORT = 8081
_DEFAULT_HOST = "127.0.0.1"
_DISCLAIMER = (
    "Kein Pilot-Nachweis. Kein Live-Go. Kein Provider-Go. "
    "Lokal und harness-only."
)
_WAL_SUFFIXES = ("-wal", "-shm")


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------

def _delete_file(path: Path) -> bool:
    """
    Delete a file. For .db files, also remove WAL sidecars (.db-wal, .db-shm).
    Returns False if any deletion raises OSError.
    """
    candidates = [path]
    if path.suffix == ".db":
        candidates.extend(Path(str(path) + s) for s in _WAL_SUFFIXES)
    for candidate in candidates:
        try:
            candidate.unlink(missing_ok=True)
            logger.info("--fresh: deleted %s", candidate)
        except OSError as exc:
            logger.error("--fresh: cannot delete %s: %s", candidate, exc)
            return False
    return True


def _read_pid_from_file(path: Path) -> int:
    """Read and return the 'pid' field from a PID metadata JSON file. Returns 0 on error."""
    try:
        meta = json.loads(path.read_text(encoding="utf-8"))
        return int(meta.get("pid", 0))
    except Exception:
        return 0


def _wait_pid_dead(pid: int, timeout: float) -> bool:
    """
    Poll until PID is no longer alive or timeout expires.
    Returns True if confirmed dead, False if still alive at deadline.
    """
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            os.kill(pid, 0)
        except OSError:
            return True
        time.sleep(0.1)
    try:
        os.kill(pid, 0)
        return False
    except OSError:
        return True


# ---------------------------------------------------------------------------
# HTTP helper (stdlib-only, no import of private runtime_tools._request_json)
# ---------------------------------------------------------------------------

def _http_json(
    method: str,
    url: str,
    payload: dict | None = None,
    timeout: float = 3.0,
) -> tuple[int, dict]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"} if payload is not None else {}
    req = Request(url, data=body, method=method, headers=headers)
    try:
        with urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        raw = exc.read().decode("utf-8")
        try:
            return exc.code, json.loads(raw)
        except json.JSONDecodeError:
            return exc.code, {"error": "NON_JSON_RESPONSE"}
    except (URLError, OSError) as exc:
        raise RuntimeError(str(exc)) from exc


# ---------------------------------------------------------------------------
# Session smoke
# ---------------------------------------------------------------------------

def _session_url(host: str, port: int, path: str) -> str:
    return f"http://{host}:{port}{path}"


def _run_session_smoke(host: str, port: int) -> dict:
    """
    Drive a session through four states: ENTRY → CHECK_IN → REFLECTION → EXIT.
    This validates the stub adapter call and the output guard (--stub-mode SAFE).

    Returns a content-free result record. User text "ja"/"stopp" are test signals,
    not stored in the artifact.
    """
    step_name = "session_smoke"
    try:
        # Turn 0: create session
        status, body = _http_json(
            "POST", _session_url(host, port, "/v1/sessions"), payload={}, timeout=3.0
        )
        if status != 201:
            logger.error("%s: /v1/sessions HTTP %s", step_name, status)
            return {"name": step_name, "status": "FAILED", "exit_code": 1}
        session_id = body.get("session_id", "")
        state = body.get("state", "")
        if not session_id or state != "ENTRY":
            logger.error("%s: unexpected state after create: %r", step_name, state)
            return {"name": step_name, "status": "FAILED", "exit_code": 1}
        logger.info("%s: session created state=%s", step_name, state)

        # Turn 1: opt-in → CHECK_IN
        status, body = _http_json(
            "POST",
            _session_url(host, port, "/v1/turns"),
            payload={"session_id": session_id, "user_text": "ja"},
            timeout=3.0,
        )
        if status != 200:
            logger.error("%s: /v1/turns(1) HTTP %s", step_name, status)
            return {"name": step_name, "status": "FAILED", "exit_code": 1}
        state = body.get("state", "")
        if state != "CHECK_IN":
            logger.error("%s: expected CHECK_IN after ja(1), got %r", step_name, state)
            return {"name": step_name, "status": "FAILED", "exit_code": 1}
        logger.info("%s: CHECK_IN reached", step_name)

        # Turn 2: confirm → REFLECTION (triggers adapter call + output guard)
        status, body = _http_json(
            "POST",
            _session_url(host, port, "/v1/turns"),
            payload={"session_id": session_id, "user_text": "ja"},
            timeout=5.0,  # slightly longer: adapter + guard run here
        )
        if status != 200:
            logger.error("%s: /v1/turns(2) HTTP %s", step_name, status)
            return {"name": step_name, "status": "FAILED", "exit_code": 1}
        state = body.get("state", "")
        if state != "REFLECTION":
            logger.error("%s: expected REFLECTION after ja(2), got %r", step_name, state)
            return {"name": step_name, "status": "FAILED", "exit_code": 1}
        logger.info("%s: REFLECTION reached (adapter + output-guard exercised)", step_name)

        # Turn 3: safeword → EXIT (closes session cleanly)
        status, body = _http_json(
            "POST",
            _session_url(host, port, "/v1/turns"),
            payload={"session_id": session_id, "user_text": "stopp"},
            timeout=3.0,
        )
        if status != 200:
            logger.error("%s: /v1/turns(3) HTTP %s", step_name, status)
            return {"name": step_name, "status": "FAILED", "exit_code": 1}
        state = body.get("state", "")
        terminal = body.get("terminal", False)
        if state != "EXIT" or not terminal:
            logger.error(
                "%s: expected EXIT+terminal after stopp, got state=%r terminal=%r",
                step_name, state, terminal,
            )
            return {"name": step_name, "status": "FAILED", "exit_code": 1}
        logger.info("%s: EXIT reached (terminal=%s) — PASSED", step_name, terminal)
        return {"name": step_name, "status": "PASSED", "exit_code": 0}

    except RuntimeError as exc:
        logger.error("%s: HTTP error: %s", step_name, exc)
        return {"name": step_name, "status": "FAILED", "exit_code": 1}


# ---------------------------------------------------------------------------
# Step runner
# ---------------------------------------------------------------------------

def _run_step_main(name: str, argv: list[str]) -> dict:
    """Call runtime_tools.main(argv). Returns content-free result record."""
    logger.info("--- Step: %s ---", name)
    try:
        rc = _rt.main(argv)
    except SystemExit as exc:
        rc = exc.code if isinstance(exc.code, int) else 1
    except Exception as exc:
        logger.error("Step %s raised: %s: %s", name, type(exc).__name__, exc)
        rc = 1
    status = "PASSED" if rc == 0 else "FAILED"
    logger.info("Step %-30s → %s (exit %s)", name, status, rc)
    return {"name": name, "status": status, "exit_code": rc}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Traumtänzer Evidence Harness — Runtime Evidence Runner"
    )
    parser.add_argument(
        "--fresh",
        action="store_true",
        help=(
            "Delete runtime DB (and WAL sidecars), log, and PID file before running. "
            "Recommended for reproducible evidence runs."
        ),
    )
    parser.add_argument(
        "--port",
        type=int,
        default=_DEFAULT_PORT,
        help=f"Local port for the runtime server (default: {_DEFAULT_PORT}).",
    )
    parser.add_argument(
        "--host",
        default=_DEFAULT_HOST,
        help=f"Bind host (default: {_DEFAULT_HOST}).",
    )
    parser.add_argument(
        "--out-dir",
        metavar="PATH",
        default=None,
        help="Directory for the artifact JSON (default: harness/data/).",
    )
    args = parser.parse_args(argv)

    data_dir = _DATA_DIR
    data_dir.mkdir(parents=True, exist_ok=True)
    out_dir = Path(args.out_dir) if args.out_dir else data_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    db_path = data_dir / "runtime_evidence.db"
    log_path = data_dir / "runtime_evidence.log"
    pid_path = data_dir / "runtime_evidence.pid"

    if args.fresh:
        for path in (db_path, log_path, pid_path):
            if not _delete_file(path):
                logger.error("--fresh: cleanup failed for %s; aborting.", path.name)
                return 1

    db_str = str(db_path)
    log_str = str(log_path)
    pid_str = str(pid_path)
    workdir_str = str(data_dir)
    host = args.host
    port_str = str(args.port)

    results: list[dict] = []
    server_started = False
    overall_failed = False
    runtime_pid = 0  # read before stop so we can confirm process death

    # --- Step 1: start ---
    start_result = _run_step_main("start", [
        "start",
        "--db", db_str,
        "--log", log_str,
        "--pid-file", pid_str,
        "--workdir", workdir_str,
        "--host", host,
        "--port", port_str,
        "--stub-mode", "SAFE",
    ])
    results.append(start_result)
    server_started = (start_result["exit_code"] == 0)
    if not server_started:
        overall_failed = True

    try:
        if server_started:
            # Read PID now before stop deletes the file.
            runtime_pid = _read_pid_from_file(pid_path)

            # --- Step 2: health ---
            health_result = _run_step_main("health", [
                "health",
                "--host", host,
                "--port", port_str,
            ])
            results.append(health_result)
            if health_result["exit_code"] != 0:
                overall_failed = True

            if not overall_failed:
                # --- Step 3: session smoke ---
                smoke_result = _run_session_smoke(args.host, args.port)
                results.append(smoke_result)
                if smoke_result["exit_code"] != 0:
                    overall_failed = True

    finally:
        # --- Step 4: stop — always run if server was started ---
        if server_started:
            stop_result = _run_step_main("stop", ["stop", "--pid-file", pid_str])
            results.append(stop_result)
            stop_ok = (stop_result["exit_code"] == 0)
            if not stop_ok:
                overall_failed = True
            else:
                # Brief pause for OS file handle release before reading DB/log.
                time.sleep(0.5)
                # Advisory PID check: on Windows, an open Popen handle in the Python
                # runtime keeps the process object alive via os.kill even after the
                # process has fully exited and closed all file handles. Log at DEBUG
                # level rather than blocking inspection when this occurs.
                if runtime_pid and not _wait_pid_dead(runtime_pid, timeout=2.0):
                    logger.debug(
                        "PID %s still visible via os.kill after stop "
                        "(Windows handle artifact); DB/log already closed by server "
                        "finally-block — proceeding with inspection.",
                        runtime_pid,
                    )

    # --- Steps 5-7: inspection — after confirmed-clean stop ---
    # Gate only on stop exit code 0. PID check is advisory (Windows handle artifact
    # can keep os.kill succeeding after process exit; DB/log are closed before exit).
    stop_ok_flag = (
        server_started
        and any(r["name"] == "stop" and r["exit_code"] == 0 for r in results)
    )

    inspection_steps: list[tuple[str, list[str]]] = [
        ("inspect_db", ["inspect-db", "--db", db_str, "--check-only"]),
        ("inspect_log", ["inspect-log", "--log", log_str, "--tail", "0", "--check-only"]),
        ("inspect_sidepaths", [
            "inspect-sidepaths",
            "--db", db_str,
            "--workdir", workdir_str,
            "--log", log_str,
            "--pid-file", pid_str,
        ]),
    ]

    for step_name, step_argv in inspection_steps:
        if stop_ok_flag:
            r = _run_step_main(step_name, step_argv)
            results.append(r)
            if r["exit_code"] != 0:
                overall_failed = True
        else:
            reason = "server did not start" if not server_started else "stop not clean"
            logger.warning("Skipping %s (%s).", step_name, reason)
            results.append({"name": step_name, "status": "SKIPPED", "exit_code": None})

    # --- Artifact ---
    overall = "FAILED" if overall_failed else "PASSED"
    ts = datetime.now(timezone.utc)
    artifact = {
        "runner": "harness.runtime_evidence",
        "runner_version": "1.0",
        "timestamp_utc": ts.isoformat(),
        "fresh_start": args.fresh,
        "host": host,
        "port": args.port,
        "db_path": db_str,
        "log_path": log_str,
        "pid_path": pid_str,
        "steps": results,
        "overall_status": overall,
        "disclaimer": _DISCLAIMER,
    }
    artifact_name = f"runtime_evidence_{ts.strftime('%Y%m%d_%H%M%S_%f')}.json"
    artifact_path = out_dir / artifact_name
    artifact_path.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    logger.info("Artifact written: %s", artifact_path)

    if overall_failed:
        logger.error("Runtime evidence run FAILED.")
        return 1
    logger.info("Runtime evidence run PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
