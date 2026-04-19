"""
Local Evidence Runner — Traumtänzer Evidence Harness

Composite one-command runner for the local harness checks:
    smoke_check → run_session → inspect_events --check-only

Writes a content-free JSON artifact to harness/data/.
Fail-closed: if a step fails, all subsequent steps are skipped.

Exit code 0 = all steps PASSED.
Exit code 1 = at least one step FAILED or SKIPPED, or --fresh deletion failed.

HARNESS-ONLY. Not for live user sessions.
No external provider. No network. No cloud. No pilot claim. No live claim.

Usage:
    python -m harness.local_evidence [--fresh] [--db PATH]

    --fresh  Delete events.db (and WAL sidecars) before running.
             Recommended for reproducible evidence runs.
    --db     SQLite DB path (default: harness/data/events.db)
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

# Configure logging before sub-module imports so this call wins the
# basicConfig "first call" race; sub-module calls become no-ops.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

from .event_store import DEFAULT_DB_PATH  # noqa: E402
from . import smoke_check as _smoke      # noqa: E402
from . import run_session as _run        # noqa: E402
from . import inspect_events as _inspect # noqa: E402

_DISCLAIMER = (
    "Kein Pilot-Nachweis. Kein Live-Go. Kein Provider-Go. "
    "Lokal und harness-only."
)

# SQLite WAL sidecars that must be removed together with the main DB file.
_WAL_SUFFIXES = ("-wal", "-shm")


def _delete_db(db_path: Path) -> bool:
    """Delete the DB file and any WAL sidecars. Returns False on OSError."""
    for suffix in ("", *_WAL_SUFFIXES):
        candidate = Path(str(db_path) + suffix)
        try:
            candidate.unlink(missing_ok=True)
            if suffix == "":
                logger.info("--fresh: deleted %s", db_path)
            elif candidate.exists():  # only log if it actually existed
                logger.info("--fresh: deleted sidecar %s", candidate.name)
        except OSError as exc:
            logger.error("--fresh: cannot delete %s: %s", candidate, exc)
            return False
    return True


def _run_step(name: str, main_fn, argv: list[str]) -> dict:
    """Run one harness step and return a content-free result record."""
    logger.info("--- Step: %s ---", name)
    try:
        rc = main_fn(argv)
    except SystemExit as exc:
        rc = exc.code if isinstance(exc.code, int) else 1
    except Exception as exc:
        logger.error("Step %s raised: %s: %s", name, type(exc).__name__, exc)
        rc = 1
    status = "PASSED" if rc == 0 else "FAILED"
    logger.info("Step %-20s → %s (exit %s)", name, status, rc)
    return {"name": name, "status": status, "exit_code": rc}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Traumtänzer Evidence Harness — Local Evidence Runner"
    )
    parser.add_argument(
        "--fresh",
        action="store_true",
        help=(
            "Delete events.db and WAL sidecars before running. "
            "Produces a clean, reproducible evidence run."
        ),
    )
    parser.add_argument(
        "--db",
        metavar="PATH",
        default=str(DEFAULT_DB_PATH),
        help=f"SQLite DB path (default: {DEFAULT_DB_PATH})",
    )
    args = parser.parse_args(argv)

    db_path = Path(args.db)
    out_dir = db_path.parent

    if args.fresh:
        if not _delete_db(db_path):
            logger.error("--fresh: DB deletion failed; aborting.")
            return 1

    db_argv = ["--db", str(db_path)]

    steps = [
        ("smoke_check",    _smoke.main,   db_argv),
        ("run_session",    _run.main,     db_argv),
        ("inspect_events", _inspect.main, db_argv + ["--check-only"]),
    ]

    results: list[dict] = []
    failed = False

    for name, fn, step_argv in steps:
        if failed:
            logger.warning("Skipping %s (fail-closed).", name)
            results.append({"name": name, "status": "SKIPPED", "exit_code": None})
            continue
        record = _run_step(name, fn, step_argv)
        results.append(record)
        if record["exit_code"] != 0:
            failed = True

    overall = "FAILED" if failed else "PASSED"
    ts = datetime.now(timezone.utc)

    artifact = {
        "runner": "harness.local_evidence",
        "runner_version": "1.0",
        "timestamp_utc": ts.isoformat(),
        "fresh_start": args.fresh,
        "db_path": str(db_path.resolve()),
        "steps": results,
        "overall_status": overall,
        "disclaimer": _DISCLAIMER,
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    artifact_name = f"local_evidence_{ts.strftime('%Y%m%d_%H%M%S_%f')}.json"
    artifact_path = out_dir / artifact_name
    artifact_path.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    logger.info("Artifact written: %s", artifact_path)

    if failed:
        logger.error("Local evidence run FAILED.")
        return 1

    logger.info("Local evidence run PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
