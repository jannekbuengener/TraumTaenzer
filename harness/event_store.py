"""
SQLite Event Store — Traumtänzer Evidence Harness

Content-free, append-only event log per KERNEL_GUARD_CONTRACTS §4, §9.

WHAT IS LOGGED:   session_id (pseudonym), timestamp, event_type, enum fields.
WHAT IS NEVER LOGGED: user text, LLM output, trigger text, user identity.
Any attempt to write a forbidden content field raises ValueError immediately.

Database location: harness/data/events.db
The data/ directory is gitignored; the path is documented for inspection.

HARNESS-ONLY. Not for live user sessions.
"""

import sqlite3
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_DATA_DIR = Path(__file__).parent / "data"
DEFAULT_DB_PATH = _DATA_DIR / "events.db"

# Schema: enum-only columns, no free-text content columns permitted.
_SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id       TEXT    NOT NULL,
    event_type       TEXT    NOT NULL,
    timestamp        TEXT    NOT NULL,
    decision         TEXT,
    guard_category   TEXT,
    violation_type   TEXT,
    from_state       TEXT,
    to_state         TEXT,
    trigger_event    TEXT,
    end_type         TEXT,
    last_state       TEXT,
    error_code       TEXT,
    component        TEXT
);
"""

# Fields that must never carry free-text content
_FORBIDDEN_FIELDS = frozenset({
    "user_text", "input_text", "output_text", "llm_output",
    "prompt", "trigger_text", "content", "text", "message",
    "raw_input", "raw_output",
})

# Fields the store will accept
_ALLOWED_FIELDS = frozenset({
    "decision", "guard_category", "violation_type",
    "from_state", "to_state", "trigger_event",
    "end_type", "last_state", "error_code", "component",
})


class EventStore:
    """
    Append-only, content-free SQLite event store.
    Thread-safety: single-threaded only (harness use case).
    """

    def __init__(self, db_path: Path = DEFAULT_DB_PATH) -> None:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.execute(_SCHEMA)
        self._conn.commit()
        logger.info("event_store_opened path=%s", db_path)

    def write(self, session_id: str, event_type: str, **kwargs: Any) -> None:
        """
        Write a redacted event. kwargs must be enum-valued fields only.
        Raises ValueError if a forbidden content field is passed.
        """
        for key in kwargs:
            if key in _FORBIDDEN_FIELDS:
                msg = f"Forbidden content field in event: field={key} event_type={event_type}"
                logger.error("event_store_content_violation field=%s event_type=%s", key, event_type)
                raise ValueError(msg)

        ts = datetime.now(timezone.utc).isoformat()
        row: dict[str, Any] = {
            "session_id": session_id,
            "event_type": event_type,
            "timestamp": ts,
        }
        for key, val in kwargs.items():
            if key in _ALLOWED_FIELDS and val is not None:
                # Persist canonical enum values instead of Enum repr strings.
                row[key] = str(val.value) if hasattr(val, "value") else str(val)

        cols = ", ".join(row.keys())
        placeholders = ", ".join(["?"] * len(row))
        self._conn.execute(
            f"INSERT INTO events ({cols}) VALUES ({placeholders})",
            list(row.values()),
        )
        self._conn.commit()
        logger.info("event_written session=%s type=%s", session_id[:8], event_type)

    def close(self) -> None:
        self._conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        self._conn.close()
        logger.info("event_store_closed path=%s", self.db_path)
