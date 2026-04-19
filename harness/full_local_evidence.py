"""
Full Local Evidence Runner — Traumtänzer Evidence Harness

Composite one-command runner for the complete local evidence path:
    local_evidence (smoke_check + run_session + inspect_events)
    runtime_evidence (start + health + session-smoke + stop + inspect-*)

Creates a shared run folder under harness/data/evidence_runs/<run_id>/,
writes individual sub-run artifacts there, and produces a single manifest.json
that summarises the complete run.

Fail-closed: both sub-runs always execute; overall_status is FAILED if either fails.
This ensures the manifest always reflects the complete picture.

Exit code 0 = all sub-runs PASSED.
Exit code 1 = at least one sub-run FAILED, or --fresh cleanup failed.

HARNESS-ONLY. Not for live user sessions.
No external provider. No network beyond localhost. No cloud. No pilot claim.

Usage:
    python -m harness.full_local_evidence [--fresh] [--port PORT]

    --fresh  Passes --fresh to both sub-runners (cleans their respective
             DB/log/PID files before running). Recommended for reproducible runs.
    --port   Port for the runtime server (default: 8081).
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

# Configure logging BEFORE sub-module imports so this basicConfig call wins
# the "first call" race; both local_evidence and runtime_evidence have their
# own module-level basicConfig calls that will become no-ops after this.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

from . import local_evidence as _le    # noqa: E402 — after basicConfig intentionally
from . import runtime_evidence as _re  # noqa: E402

_DATA_DIR = Path(__file__).resolve().parent / "data"
_RUNS_DIR = _DATA_DIR / "evidence_runs"
_DEFAULT_PORT = 8081
_DISCLAIMER = (
    "Kein Pilot-Nachweis. Kein Live-Go. Kein Provider-Go. "
    "Lokal und harness-only."
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Traumtänzer Evidence Harness — Full Local Evidence Runner"
    )
    parser.add_argument(
        "--fresh",
        action="store_true",
        help=(
            "Pass --fresh to both sub-runners (cleans their DB/log/PID files). "
            "Recommended for reproducible evidence runs."
        ),
    )
    parser.add_argument(
        "--port",
        type=int,
        default=_DEFAULT_PORT,
        help=f"Port for the runtime server (default: {_DEFAULT_PORT}).",
    )
    args = parser.parse_args(argv)

    ts = datetime.now(timezone.utc)
    run_id = ts.strftime("%Y%m%d_%H%M%S_%f")
    run_dir = _RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Run folder: %s", run_dir)

    sub_runs: list[dict] = []
    overall_failed = False

    # --- Sub-run 1: local_evidence ---
    logger.info("=== Sub-run: local_evidence ===")
    le_argv = ["--out-dir", str(run_dir)]
    if args.fresh:
        le_argv.append("--fresh")
    le_rc = _le.main(le_argv)
    le_status = "PASSED" if le_rc == 0 else "FAILED"
    sub_runs.append({
        "name": "local_evidence",
        "status": le_status,
        "exit_code": le_rc,
    })
    if le_rc != 0:
        overall_failed = True
        logger.warning("local_evidence FAILED (exit %s); continuing to runtime_evidence.", le_rc)

    # --- Sub-run 2: runtime_evidence ---
    # Always runs regardless of local_evidence result: full picture wanted.
    logger.info("=== Sub-run: runtime_evidence ===")
    re_argv = ["--out-dir", str(run_dir), "--port", str(args.port)]
    if args.fresh:
        re_argv.append("--fresh")
    re_rc = _re.main(re_argv)
    re_status = "PASSED" if re_rc == 0 else "FAILED"
    sub_runs.append({
        "name": "runtime_evidence",
        "status": re_status,
        "exit_code": re_rc,
    })
    if re_rc != 0:
        overall_failed = True

    # --- Manifest ---
    overall = "FAILED" if overall_failed else "PASSED"
    # Collect artifact filenames written into the run folder by the sub-runners.
    artifacts = sorted(
        p.name for p in run_dir.glob("*.json") if p.name != "manifest.json"
    )
    manifest = {
        "runner": "harness.full_local_evidence",
        "runner_version": "1.0",
        "run_id": run_id,
        "timestamp_utc": ts.isoformat(),
        "fresh_start": args.fresh,
        "run_dir": str(run_dir),
        "sub_runs": sub_runs,
        "artifacts": artifacts,
        "overall_status": overall,
        "disclaimer": _DISCLAIMER,
    }
    manifest_path = run_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    logger.info("Manifest written: %s", manifest_path)

    if overall_failed:
        logger.error("Full local evidence run FAILED.")
        return 1
    logger.info("Full local evidence run PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
