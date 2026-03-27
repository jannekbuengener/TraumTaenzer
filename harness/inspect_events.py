"""
Event Store Inspector — Traumtänzer Evidence Harness

Reads the local SQLite event store and prints a structured summary.
Also performs a leak/sidepath check: verifies no forbidden content
field is present in the schema or any row.

Exit code 0 = store readable, no schema violations found.
Exit code 1 = store not found, unreadable, or schema violation detected.

HARNESS-ONLY. Not for live user sessions.

Usage:
  python -m harness.inspect_events [--db PATH] [--session SESSION_ID_PREFIX]
  python -m harness.inspect_events --check-only
"""

import argparse
import logging
import sqlite3
import sys
from pathlib import Path

from .event_store import DEFAULT_DB_PATH, _FORBIDDEN_FIELDS, _ALLOWED_FIELDS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


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
    known = _ALLOWED_FIELDS | {"id", "session_id", "event_type", "timestamp"}
    violations: list[str] = []
    cols = [row[1] for row in conn.execute("PRAGMA table_info(events)").fetchall()]
    for col in cols:
        if col not in known:
            violations.append(f"Unexpected column (possible sidepath): {col!r}")
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
        last_type, last_ts = last if last else ("—", "—")
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
            details.append(f"{frm}→{to}")
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
                        help="Only perform leak/schema check, no display output")
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
    violations += check_schema(conn)
    violations += check_sidepath_columns(conn)

    if violations:
        for v in violations:
            logger.error("LEAK/SIDEPATH VIOLATION: %s", v)
        conn.close()
        return 1

    if args.check_only:
        logger.info("Schema check PASSED — no forbidden or unexpected columns.")
        conn.close()
        return 0

    # Display
    print_summary(conn, session_prefix=args.session)
    if args.session:
        print_session_detail(conn, args.session)

    conn.close()
    logger.info("Inspection complete. No schema violations detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
