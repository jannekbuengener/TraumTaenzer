"""
Event Store Inspector — Traumtänzer Evidence Harness

Reads the local SQLite event store and prints a structured summary.
Also performs schema and row-value audits for redacted runtime events.

Exit code 0 = store readable, no DB audit violations found.
Exit code 1 = store not found, unreadable, or DB audit violation detected.

HARNESS-ONLY. Not for live user sessions.

Usage:
  python -m harness.inspect_events [--db PATH] [--session SESSION_ID_PREFIX]
  python -m harness.inspect_events --check-only
"""

import argparse
import logging
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

from .event_store import DEFAULT_DB_PATH, _FORBIDDEN_FIELDS, _ALLOWED_FIELDS
from .guards import GuardCategory, InputDecision, OutputDecision, ViolationType
from .kernel import S

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

_BASE_EVENT_COLUMNS = frozenset({"id", "session_id", "event_type", "timestamp"})
_KNOWN_EVENT_TYPES = frozenset({
    "SESSION_STARTED",
    "SESSION_ENDED",
    "INPUT_GUARD_RESULT",
    "OUTPUT_GUARD_RESULT",
    "SAFE_STATE_TRANSITION",
    "SYSTEM_ERROR",
})
_STATE_VALUES = frozenset({
    S.ENTRY,
    S.CHECK_IN,
    S.REFLECTION,
    S.PAUSED,
    S.EXIT,
    S.EXTERNAL_REFERRAL,
    S.GUARD_BLOCK,
})
_INPUT_DECISION_VALUES = frozenset(decision.value for decision in InputDecision)
_OUTPUT_DECISION_VALUES = frozenset(decision.value for decision in OutputDecision)
_GUARD_CATEGORY_VALUES = frozenset(category.value for category in GuardCategory)
_VIOLATION_TYPE_VALUES = frozenset(violation.value for violation in ViolationType)
_TRIGGER_EVENT_VALUES = frozenset({
    "USER_OPT_IN",
    "USER_CONFIRMED",
    "USER_GO",
    "USER_RETRY",
    "BLOCK_EXIT",
    "BLOCK_REFER",
    "BLOCK_PAUSE",
    "BLOCK_BOUNDARY",
    "OUTPUT_GUARD_RESULT",
    "ERROR_FAIL_CLOSED",
})
_END_TYPE_VALUES = frozenset({
    "NORMAL",
    "SAFEWORD",
    "GUARD_ABORT",
    "REFERRAL",
    "SYSTEM_ERROR",
})
_ERROR_CODE_VALUES = frozenset({
    "GUARD_ERROR",
    "OUTPUT_GUARD_ERROR",
    "NO_ADAPTER_CONFIGURED",
    "ADAPTER_EXCEPTION",
    "EMPTY_OR_INVALID_PROVIDER_OUTPUT",
    "UNKNOWN_STATE",
})
_COMPONENT_VALUES = frozenset({"GUARD", "KERNEL", "LLM_ADAPTER"})
_EVENT_ALLOWED_FIELDS: dict[str, frozenset[str]] = {
    "SESSION_STARTED": frozenset(),
    "SESSION_ENDED": frozenset({"end_type", "last_state"}),
    "INPUT_GUARD_RESULT": frozenset({"decision", "guard_category"}),
    "OUTPUT_GUARD_RESULT": frozenset({"decision", "violation_type"}),
    "SAFE_STATE_TRANSITION": frozenset({"from_state", "to_state", "trigger_event"}),
    "SYSTEM_ERROR": frozenset({"error_code", "component"}),
}
_EVENT_REQUIRED_FIELDS: dict[str, frozenset[str]] = {
    "SESSION_STARTED": frozenset(),
    "SESSION_ENDED": frozenset({"end_type", "last_state"}),
    "INPUT_GUARD_RESULT": frozenset({"decision", "guard_category"}),
    "OUTPUT_GUARD_RESULT": frozenset({"decision"}),
    "SAFE_STATE_TRANSITION": frozenset({"from_state", "to_state", "trigger_event"}),
    "SYSTEM_ERROR": frozenset({"error_code", "component"}),
}
_EVENT_FIELD_ALLOWED_VALUES: dict[tuple[str, str], frozenset[str]] = {
    ("SESSION_ENDED", "end_type"): _END_TYPE_VALUES,
    ("SESSION_ENDED", "last_state"): _STATE_VALUES,
    ("INPUT_GUARD_RESULT", "decision"): _INPUT_DECISION_VALUES,
    ("INPUT_GUARD_RESULT", "guard_category"): _GUARD_CATEGORY_VALUES,
    ("OUTPUT_GUARD_RESULT", "decision"): _OUTPUT_DECISION_VALUES,
    ("OUTPUT_GUARD_RESULT", "violation_type"): _VIOLATION_TYPE_VALUES,
    ("SAFE_STATE_TRANSITION", "from_state"): _STATE_VALUES,
    ("SAFE_STATE_TRANSITION", "to_state"): _STATE_VALUES,
    ("SAFE_STATE_TRANSITION", "trigger_event"): _TRIGGER_EVENT_VALUES,
    ("SYSTEM_ERROR", "error_code"): _ERROR_CODE_VALUES,
    ("SYSTEM_ERROR", "component"): _COMPONENT_VALUES,
}
_SIDEPATH_SUFFIXES = frozenset({".log", ".jsonl", ".txt", ".ndjson", ".dump"})
_SIDEPATH_NAME_MARKERS = (
    "debug",
    "dump",
    "payload",
    "prompt",
    "transcript",
    "shadow",
    "sidepath",
    "export",
)
_SIDEPATH_SKIP_DIRS = frozenset({".git", "__pycache__", ".venv", "node_modules", "build", "dist"})


# ---------------------------------------------------------------------------
# Schema / leak checks
# ---------------------------------------------------------------------------

def check_schema(conn: sqlite3.Connection) -> list[str]:
    """Returns list of violations (empty = clean)."""
    violations: list[str] = []
    cols = [row[1] for row in conn.execute("PRAGMA table_info(events)").fetchall()]
    for col in cols:
        if col in _FORBIDDEN_FIELDS:
            violations.append(f"Forbidden column in schema: {col!r}")
    return violations


def check_sidepath_columns(conn: sqlite3.Connection) -> list[str]:
    """
    Sidepath check: any column not in the known allowed set
    (excluding id, session_id, event_type, timestamp) is unexpected.
    """
    known = _ALLOWED_FIELDS | _BASE_EVENT_COLUMNS
    violations: list[str] = []
    cols = [row[1] for row in conn.execute("PRAGMA table_info(events)").fetchall()]
    for col in cols:
        if col not in known:
            violations.append(f"Unexpected column (possible sidepath): {col!r}")
    return violations


def _select_event_rows(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    conn.row_factory = sqlite3.Row
    return conn.execute(
        """SELECT id, session_id, event_type, timestamp,
                  decision, guard_category, violation_type,
                  from_state, to_state, trigger_event,
                  end_type, last_state, error_code, component
           FROM events
           ORDER BY id"""
    ).fetchall()


def _valid_session_id(value: object) -> bool:
    if not isinstance(value, str):
        return False
    if not (4 <= len(value) <= 128):
        return False
    if any(ch.isspace() for ch in value):
        return False
    return all(ch.isalnum() or ch in "-_:.@" for ch in value)


def _valid_timestamp(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        datetime.fromisoformat(value)
    except ValueError:
        return False
    return True


def check_row_values(conn: sqlite3.Connection) -> list[str]:
    violations: list[str] = []
    rows = _select_event_rows(conn)

    for row in rows:
        row_id = row["id"]
        event_type = row["event_type"]
        if event_type not in _KNOWN_EVENT_TYPES:
            violations.append(f"Row {row_id}: unknown event_type={event_type!r}")
            continue

        if not _valid_session_id(row["session_id"]):
            violations.append(f"Row {row_id}: invalid session_id format")

        if not _valid_timestamp(row["timestamp"]):
            violations.append(f"Row {row_id}: invalid timestamp format")

        allowed_fields = _EVENT_ALLOWED_FIELDS[event_type]
        required_fields = _EVENT_REQUIRED_FIELDS[event_type]

        for field in _ALLOWED_FIELDS:
            value = row[field]
            if field in required_fields and (value is None or str(value).strip() == ""):
                violations.append(f"Row {row_id}: missing required field {field!r} for {event_type}")
                continue

            if value is None:
                continue

            if field not in allowed_fields:
                violations.append(
                    f"Row {row_id}: unexpected non-null field {field!r} for {event_type}"
                )
                continue

            allowed_values = _EVENT_FIELD_ALLOWED_VALUES.get((event_type, field))
            if allowed_values and str(value) not in allowed_values:
                violations.append(
                    f"Row {row_id}: invalid {field}={value!r} for {event_type}"
                )

        if event_type == "OUTPUT_GUARD_RESULT":
            decision = row["decision"]
            violation_type = row["violation_type"]
            if decision == OutputDecision.BLOCK.value and violation_type is None:
                violations.append(f"Row {row_id}: BLOCK output decision without violation_type")
            if decision != OutputDecision.BLOCK.value and violation_type is not None:
                violations.append(
                    f"Row {row_id}: non-BLOCK output decision with violation_type present"
                )

    return violations


def collect_db_audit_violations(conn: sqlite3.Connection) -> list[str]:
    return check_schema(conn) + check_sidepath_columns(conn) + check_row_values(conn)


def scan_sidepaths(
    roots: list[Path],
    *,
    allowed_paths: set[Path] | None = None,
) -> list[str]:
    violations: list[str] = []
    allowed = {path.resolve(strict=False) for path in (allowed_paths or set())}
    seen_roots: set[Path] = set()

    for root in roots:
        resolved_root = root.resolve(strict=False)
        if resolved_root in seen_roots:
            continue
        seen_roots.add(resolved_root)

        if not resolved_root.exists():
            violations.append(f"Scan root missing: {resolved_root}")
            continue
        if not resolved_root.is_dir():
            violations.append(f"Scan root is not a directory: {resolved_root}")
            continue

        for current, dirnames, filenames in os.walk(resolved_root):
            dirnames[:] = [
                name for name in dirnames
                if name not in _SIDEPATH_SKIP_DIRS
            ]
            current_path = Path(current)
            for filename in filenames:
                candidate = (current_path / filename).resolve(strict=False)
                if candidate in allowed:
                    continue

                lower_name = candidate.name.lower()
                suffix = candidate.suffix.lower()
                if suffix not in _SIDEPATH_SUFFIXES and not any(
                    marker in lower_name for marker in _SIDEPATH_NAME_MARKERS
                ):
                    continue

                try:
                    rel_path = candidate.relative_to(resolved_root)
                except ValueError:
                    rel_path = candidate
                violations.append(
                    f"Suspicious sidepath in {resolved_root}: {rel_path}"
                )

    return violations


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def _col_names(conn: sqlite3.Connection) -> list[str]:
    return [row[1] for row in conn.execute("PRAGMA table_info(events)").fetchall()]


def print_summary(conn: sqlite3.Connection, session_prefix: str | None = None) -> None:
    total = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    print(f"\nTotal events: {total}")

    # Per event_type counts
    rows = conn.execute(
        "SELECT event_type, COUNT(*) as n FROM events GROUP BY event_type ORDER BY n DESC"
    ).fetchall()
    print("\nEvent type distribution:")
    for event_type, count in rows:
        print(f"  {event_type:<40} {count}")

    # Per session summary
    sessions = conn.execute(
        "SELECT DISTINCT session_id FROM events ORDER BY session_id"
    ).fetchall()
    print(f"\nSessions: {len(sessions)}")
    if session_prefix:
        sessions = [s for s in sessions if s[0].startswith(session_prefix)]
        print(f"(filtered to prefix {session_prefix!r}: {len(sessions)} sessions)")

    for (sid,) in sessions[:20]:  # cap display at 20 sessions
        count = conn.execute(
            "SELECT COUNT(*) FROM events WHERE session_id = ?", (sid,)
        ).fetchone()[0]
        last = conn.execute(
            "SELECT event_type, timestamp FROM events WHERE session_id = ? ORDER BY id DESC LIMIT 1",
            (sid,),
        ).fetchone()
        last_type, last_ts = last if last else ("-", "-")
        print(f"  {sid[:20]:<22} {count:>4} events  last={last_type} @ {last_ts[:19]}")

    if len(sessions) > 20:
        print(f"  ... and {len(sessions) - 20} more sessions (use --session to filter)")


def print_session_detail(conn: sqlite3.Connection, session_prefix: str) -> None:
    rows = conn.execute(
        """SELECT id, session_id, event_type, timestamp,
                  decision, guard_category, violation_type,
                  from_state, to_state, trigger_event,
                  end_type, last_state, error_code, component
           FROM events
           WHERE session_id LIKE ?
           ORDER BY id""",
        (session_prefix + "%",),
    ).fetchall()
    if not rows:
        print(f"\nNo events found for prefix {session_prefix!r}")
        return

    print(f"\nEvents for session prefix {session_prefix!r} ({len(rows)} rows):")
    for row in rows:
        (eid, sid, etype, ts, decision, gcat, vtype, frm, to, trigger,
         end_type, last_state, error_code, component) = row
        parts = [f"  [{eid:>4}] {ts[11:19]} {etype:<35}"]
        details = []
        if decision:
            details.append(f"decision={decision}")
        if gcat:
            details.append(f"category={gcat}")
        if vtype:
            details.append(f"violation={vtype}")
        if frm or to:
            details.append(f"{frm}->{to}")
        if trigger:
            details.append(f"trigger={trigger}")
        if end_type:
            details.append(f"end={end_type}")
        if error_code:
            details.append(f"err={error_code}")
        if component:
            details.append(f"comp={component}")
        if details:
            parts.append(" ".join(details))
        print("".join(parts))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Traumtänzer Evidence Harness — Event Inspector")
    parser.add_argument("--db", metavar="PATH", default=str(DEFAULT_DB_PATH),
                        help=f"SQLite DB path (default: {DEFAULT_DB_PATH})")
    parser.add_argument("--session", metavar="PREFIX",
                        help="Filter by session_id prefix")
    parser.add_argument("--check-only", action="store_true",
                        help="Only perform DB audit, no display output")
    args = parser.parse_args(argv)

    db_path = Path(args.db)
    if not db_path.exists():
        logger.error("DB not found: %s", db_path)
        return 1

    try:
        conn = sqlite3.connect(str(db_path), check_same_thread=False)
    except Exception as exc:
        logger.error("Cannot open DB: %s", exc)
        return 1

    violations: list[str] = []

    # Schema checks
    violations += collect_db_audit_violations(conn)

    if violations:
        for v in violations:
            logger.error("LEAK/SIDEPATH VIOLATION: %s", v)
        conn.close()
        return 1

    if args.check_only:
        logger.info("DB audit PASSED — no schema or row-value violations.")
        conn.close()
        return 0

    # Display
    print_summary(conn, session_prefix=args.session)
    if args.session:
        print_session_detail(conn, args.session)

    conn.close()
    logger.info("Inspection complete. No DB audit violations detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
