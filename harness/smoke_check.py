"""
Smoke Check — Traumtänzer Evidence Harness

Minimal start/stop/health verification.
Exit code 0 = harness is locally operational.
Exit code 1 = at least one precondition failed.

Checks performed:
  1. SQLite event store opens and accepts a write.
  2. Kernel can be instantiated and transitions out of ENTRY on opt-in.
  3. InputGuard blocks a safeword correctly.
  4. OutputGuard blocks a known violation correctly.
  5. FaultInjector passes guard-error fault to Kernel → fail-closed EXIT.
  6. No forbidden content field reaches the event store.
  7. Event store closes cleanly (WAL checkpoint).

This is NOT a full test run. Use run_session.py for scenario coverage.

HARNESS-ONLY. Not for live user sessions.

Usage:
  python -m harness.smoke_check [--db PATH]
"""

import argparse
import logging
import sys
import uuid
from pathlib import Path

from .event_store import EventStore, DEFAULT_DB_PATH
from .fault_injection import FaultInjector
from .guards import InputGuard, OutputGuard, InputDecision, OutputDecision
from .kernel import Kernel, S
from .llm_adapter import StubLLMAdapter, StubMode

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

CHECKS: list[tuple[str, str]] = []


def _check(name: str):
    """Decorator to register a check function."""
    def decorator(fn):
        CHECKS.append((name, fn))
        return fn
    return decorator


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

@_check("event_store_open_write")
def check_event_store(store: EventStore) -> None:
    sid = f"smoke-{uuid.uuid4().hex[:8]}"
    store.write(sid, "SESSION_STARTED")
    store.write(sid, "SESSION_ENDED", end_type="NORMAL", last_state="ENTRY")


@_check("kernel_entry_to_check_in")
def check_kernel_entry(store: EventStore) -> None:
    k = Kernel(f"smoke-{uuid.uuid4().hex[:8]}", store)
    assert k.state == S.ENTRY
    k.process_input("ja")
    assert k.state == S.CHECK_IN, f"Expected CHECK_IN, got {k.state}"


@_check("input_guard_safeword_block")
def check_input_guard(store: EventStore) -> None:
    g = InputGuard()
    result = g.check("stopp bitte", 0)
    assert result.decision == InputDecision.BLOCK_EXIT, (
        f"Expected BLOCK_EXIT for safeword, got {result.decision}"
    )


@_check("output_guard_diagnosis_block")
def check_output_guard(store: EventStore) -> None:
    g = OutputGuard()
    result = g.check("Du hast Anzeichen einer Dissoziation.")
    assert result.decision == OutputDecision.BLOCK, (
        f"Expected BLOCK for diagnosis output, got {result.decision}"
    )


@_check("fault_injection_guard_error_fail_closed")
def check_fault_injection(store: EventStore) -> None:
    fi = FaultInjector.guard_error()
    k = Kernel(f"smoke-{uuid.uuid4().hex[:8]}", store, fault_injector=fi)
    k.process_input("hallo")
    assert k.state == S.EXIT, f"Expected EXIT on fault injection, got {k.state}"
    assert k.is_terminal()


@_check("event_store_content_violation_raises")
def check_content_violation(store: EventStore) -> None:
    sid = f"smoke-{uuid.uuid4().hex[:8]}"
    raised = False
    try:
        store.write(sid, "TEST_EVENT", user_text="should raise")
    except ValueError:
        raised = True
    assert raised, "EventStore must raise ValueError on forbidden content field"


@_check("stub_adapter_safe_returns_string")
def check_stub_adapter(store: EventStore) -> None:
    adapter = StubLLMAdapter(StubMode.SAFE)
    result = adapter.generate("[harness-context session=smoke001]")
    assert isinstance(result, str) and result.strip(), (
        f"Expected non-empty string from SAFE adapter, got {result!r}"
    )


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Traumtänzer Evidence Harness — Smoke Check")
    parser.add_argument("--db", metavar="PATH", default=str(DEFAULT_DB_PATH),
                        help=f"SQLite DB path (default: {DEFAULT_DB_PATH})")
    args = parser.parse_args(argv)

    db_path = Path(args.db)
    store = EventStore(db_path)

    failed: list[str] = []
    for name, fn in CHECKS:
        try:
            fn(store)
            logger.info("CHECK %-45s OK", name)
        except Exception as exc:
            logger.error("CHECK %-45s FAILED — %s: %s", name, type(exc).__name__, exc)
            failed.append(name)

    store.close()

    if failed:
        logger.error("Smoke check FAILED (%d/%d): %s", len(failed), len(CHECKS), failed)
        return 1

    logger.info("Smoke check PASSED (%d/%d checks).", len(CHECKS), len(CHECKS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
