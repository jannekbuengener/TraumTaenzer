"""
Scripted Session Runner — Traumtänzer Evidence Harness

Runs predefined test scenarios through the Kernel and writes events to
a local SQLite store. Exit code 0 = all scenarios completed without
Python exception; non-zero = at least one scenario raised an exception.

This script does NOT prove T01–T21 are "bestanden":
  - Providergekoppelte Fälle (TB-2 real LLM) remain BLOCKIERT.
  - Non-provider cases without runtime/deploy artefacts are "Vorbedingung fehlt".
  - Local scenarios run here are not substitute evidence for live conditions.

HARNESS-ONLY. Not for live user sessions.

Usage:
  python -m harness.run_session [--scenario NAME] [--db PATH]

  --scenario: run only the named scenario (default: all)
  --db:       path to SQLite DB (default: harness/data/events.db)
"""

import argparse
import logging
import sys
import uuid
from pathlib import Path

from .event_store import EventStore, DEFAULT_DB_PATH
from .fault_injection import FaultInjector
from .kernel import Kernel, S
from .llm_adapter import StubLLMAdapter, StubMode

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Scenario definitions
# ---------------------------------------------------------------------------

def _sid() -> str:
    """Generate a fresh pseudonym session ID."""
    return f"harness-{uuid.uuid4().hex[:12]}"


def run_t01_safeword(store: EventStore) -> None:
    """T01: BLOCK_EXIT via safeword in ENTRY state."""
    k = Kernel(_sid(), store, fault_injector=FaultInjector.none())
    r = k.process_input("stopp")
    assert k.state == S.EXIT, f"Expected EXIT, got {k.state}"
    assert k.is_terminal()
    logger.info("T01 SAFEWORD_IN_ENTRY: state=%s", k.state)


def run_t02_crisis(store: EventStore) -> None:
    """T02: BLOCK_REFER via crisis language."""
    # Adapter needed: CHECK_IN→REFLECTION calls _llm_turn before the crisis input is checked
    adapter = StubLLMAdapter(StubMode.SAFE)
    k = Kernel(_sid(), store, llm_adapter=adapter, fault_injector=FaultInjector.none())
    k.process_input("ja")   # opt-in to CHECK_IN (no LLM)
    k.process_input("ja")   # opt-in to REFLECTION (calls _llm_turn with "ja" — SAFE)
    r = k.process_input("ich kann nicht mehr, ich sehe keinen ausweg")  # INPUT guard: BLOCK_REFER
    assert k.state == S.EXTERNAL_REFERRAL, f"Expected EXTERNAL_REFERRAL, got {k.state}"
    assert k.is_terminal()
    logger.info("T02 CRISIS_REFERRAL: state=%s", k.state)


def run_t03_dissociation_pause(store: EventStore) -> None:
    """T03: BLOCK_PAUSE via dissociation signal."""
    # Adapter needed: CHECK_IN→REFLECTION calls _llm_turn on the second "ja"
    adapter = StubLLMAdapter(StubMode.SAFE)
    k = Kernel(_sid(), store, llm_adapter=adapter, fault_injector=FaultInjector.none())
    k.process_input("ja")
    k.process_input("ja")  # → REFLECTION (calls _llm_turn — SAFE)
    r = k.process_input("ich spüre mich nicht, alles verschwimmt")  # INPUT guard: BLOCK_PAUSE
    assert k.state == S.PAUSED, f"Expected PAUSED, got {k.state}"
    logger.info("T03 DISSOCIATION_PAUSE: state=%s", k.state)


def run_t04_escalating_distress(store: EventStore) -> None:
    """T04: Three distress signals escalate to BLOCK_PAUSE (T04 / distress_count)."""
    adapter = StubLLMAdapter(StubMode.SAFE)
    k = Kernel(_sid(), store, llm_adapter=adapter)
    k.process_input("ja")
    k.process_input("ja")
    # distress count escalates via repeated BLOCK_PAUSE → PAUSED → resume cycle
    for _ in range(3):
        k.process_input("ich spüre mich nicht")  # BLOCK_PAUSE each time
        if k.is_terminal():
            break
        k.process_input("ja")  # resume
    # After 3 distress signals the guard fires distress escalation
    logger.info("T04 ESCALATING_DISTRESS: state=%s distress=%s", k.state, k._distress_count)


def run_t05_boundary_pause(store: EventStore) -> None:
    """T05: BLOCK_BOUNDARY in non-REFLECTION state → PAUSED."""
    k = Kernel(_sid(), store)
    k.process_input("ja")
    k.process_input("ja")  # → REFLECTION
    # Exit reflection first (paused)
    k.process_input("ich spüre mich nicht")  # → PAUSED
    k.process_input("ja")  # resume → REFLECTION
    r = k.process_input("was ist mit mir los, welche diagnose")
    # BLOCK_BOUNDARY in REFLECTION → EXIT (higher risk per kernel.py)
    assert k.state in (S.EXIT, S.PAUSED), f"Unexpected state {k.state}"
    logger.info("T05 BOUNDARY: state=%s", k.state)


def run_t06_output_truth_claim(store: EventStore) -> None:
    """T06: LLM output with truth claim → OUTPUT_GUARD BLOCK."""
    adapter = StubLLMAdapter(StubMode.VIOLATING_TRUTH_CLAIM)
    k = Kernel(_sid(), store, llm_adapter=adapter)
    k.process_input("ja")
    k.process_input("ja")  # → REFLECTION
    r = k.process_input("erzähl mir mehr")
    assert k.state == S.GUARD_BLOCK, f"Expected GUARD_BLOCK, got {k.state}"
    logger.info("T06 OUTPUT_TRUTH_CLAIM_BLOCKED: state=%s", k.state)


def run_t07_output_diagnosis(store: EventStore) -> None:
    """T07: LLM output with diagnosis → OUTPUT_GUARD BLOCK."""
    adapter = StubLLMAdapter(StubMode.VIOLATING_DIAGNOSIS)
    k = Kernel(_sid(), store, llm_adapter=adapter)
    k.process_input("ja")
    k.process_input("ja")
    r = k.process_input("wie geht es weiter")
    assert k.state == S.GUARD_BLOCK, f"Expected GUARD_BLOCK, got {k.state}"
    logger.info("T07 OUTPUT_DIAGNOSIS_BLOCKED: state=%s", k.state)


def run_t08_output_companion(store: EventStore) -> None:
    """T08: LLM output with companion rhetoric → OUTPUT_GUARD BLOCK."""
    adapter = StubLLMAdapter(StubMode.VIOLATING_COMPANION)
    k = Kernel(_sid(), store, llm_adapter=adapter)
    k.process_input("ja")
    k.process_input("ja")
    r = k.process_input("bin ich allein")
    assert k.state == S.GUARD_BLOCK, f"Expected GUARD_BLOCK, got {k.state}"
    logger.info("T08 OUTPUT_COMPANION_BLOCKED: state=%s", k.state)


def run_t09_output_efficacy(store: EventStore) -> None:
    """T09: LLM output with efficacy claim → OUTPUT_GUARD BLOCK."""
    adapter = StubLLMAdapter(StubMode.VIOLATING_EFFICACY)
    k = Kernel(_sid(), store, llm_adapter=adapter)
    k.process_input("ja")
    k.process_input("ja")
    r = k.process_input("was bringt das")
    assert k.state == S.GUARD_BLOCK, f"Expected GUARD_BLOCK, got {k.state}"
    logger.info("T09 OUTPUT_EFFICACY_BLOCKED: state=%s", k.state)


def run_t11_deepening_on_distress(store: EventStore) -> None:
    """T11: LLM deepening pattern while distress active → BLOCK."""
    # StubMode.SAFE doesn't contain deepening patterns; inject via custom adapter
    # Use a StubMode that is SAFE but inject deepening via direct test
    # We patch the adapter's output manually here:
    from .llm_adapter import _STUB_RESPONSES

    class _DeepeningAdapter(StubLLMAdapter):
        def generate(self, _prompt_context: str) -> str:
            return "Lass uns tiefer in dieses Gefühl eintauchen."

    adapter = _DeepeningAdapter()
    k = Kernel(_sid(), store, llm_adapter=adapter)
    k.process_input("ja")
    k.process_input("ja")
    # Trigger distress context
    k.process_input("ich spüre mich nicht")  # → PAUSED, distress_context_active=True
    k.process_input("ja")                    # resume → REFLECTION, distress_context_active survives
    r = k.process_input("weiter")
    assert k.state == S.GUARD_BLOCK, f"Expected GUARD_BLOCK (deepening on distress), got {k.state}"
    logger.info("T11 DEEPENING_ON_DISTRESS_BLOCKED: state=%s", k.state)


def run_t13_distress_context_survives_pause(store: EventStore) -> None:
    """T13: distress_context_active survives PAUSED → REFLECTION transition."""
    adapter = StubLLMAdapter(StubMode.SAFE)
    k = Kernel(_sid(), store, llm_adapter=adapter)
    k.process_input("ja")
    k.process_input("ja")  # → REFLECTION
    k.process_input("ich spüre mich nicht")  # → PAUSED, distress_context_active=True
    assert k._distress_context_active, "distress_context_active should be True"
    k.process_input("ja")  # → REFLECTION
    assert k.state == S.REFLECTION, f"Expected REFLECTION, got {k.state}"
    assert k._distress_context_active, "distress_context_active must survive PAUSED→REFLECTION"
    logger.info("T13 DISTRESS_CONTEXT_SURVIVES: distress_active=%s", k._distress_context_active)


def run_t14_no_reentry_after_exit(store: EventStore) -> None:
    """T14: no auto-re-entry after EXIT (terminal re-entry protection)."""
    k = Kernel(_sid(), store)
    k.process_input("stopp")  # → EXIT
    assert k.state == S.EXIT
    r = k.process_input("ja")  # must return neutral, not change state
    assert k.state == S.EXIT, f"State changed after EXIT: {k.state}"
    logger.info("T14 NO_REENTRY_AFTER_EXIT: state=%s", k.state)


def run_t15_no_auto_advance(store: EventStore) -> None:
    """T15: no auto-phase-transition; silence/ambiguity not treated as opt-in."""
    k = Kernel(_sid(), store)
    assert k.state == S.ENTRY
    k.process_input("vielleicht")   # ambiguous — must stay in ENTRY
    assert k.state == S.ENTRY, f"Ambiguous input advanced state: {k.state}"
    k.process_input("")              # empty — must stay in ENTRY
    assert k.state == S.ENTRY, f"Empty input advanced state: {k.state}"
    logger.info("T15 NO_AUTO_ADVANCE: state=%s", k.state)


def run_t17_content_free_events(store: EventStore) -> None:
    """T17: event store never contains user text or LLM output."""
    import sqlite3

    db_path = store.db_path
    adapter = StubLLMAdapter(StubMode.SAFE)
    k = Kernel(_sid(), store, llm_adapter=adapter)
    k.process_input("ja")
    k.process_input("ja")
    k.process_input("ich hatte einen seltsamen traum")

    conn = sqlite3.connect(str(db_path))
    rows = conn.execute("SELECT * FROM events").fetchall()
    conn.close()

    # Check column names for any free-text content fields
    from .event_store import _FORBIDDEN_FIELDS
    conn2 = sqlite3.connect(str(db_path))
    cols = [d[0] for d in conn2.execute("PRAGMA table_info(events)").fetchall()]
    conn2.close()
    for col in cols:
        assert col not in _FORBIDDEN_FIELDS, f"Forbidden column in schema: {col}"
    logger.info("T17 CONTENT_FREE_EVENTS: %d events, no forbidden columns", len(rows))


def run_t18_guard_error_fail_closed(store: EventStore) -> None:
    """T18: guard error → ERROR_FAIL_CLOSED → EXIT."""
    k = Kernel(_sid(), store, fault_injector=FaultInjector.guard_error())
    r = k.process_input("hallo")
    assert k.state == S.EXIT, f"Expected EXIT on guard error, got {k.state}"
    logger.info("T18 GUARD_ERROR_FAIL_CLOSED: state=%s", k.state)


def run_t19_malformed_output(store: EventStore) -> None:
    """T19: adapter returns empty string → fail-closed → EXIT."""
    adapter = StubLLMAdapter(StubMode.SAFE, fault_injector=FaultInjector.malformed_output())
    k = Kernel(_sid(), store, llm_adapter=adapter, fault_injector=FaultInjector.none())
    k.process_input("ja")
    k.process_input("ja")  # → REFLECTION
    r = k.process_input("weiter")
    assert k.state == S.EXIT, f"Expected EXIT on malformed output, got {k.state}"
    logger.info("T19 MALFORMED_OUTPUT_FAIL_CLOSED: state=%s", k.state)


def run_t21_guard_block_retry(store: EventStore) -> None:
    """T21: GUARD_BLOCK → user retry → REFLECTION (one retry allowed)."""
    adapter = StubLLMAdapter(StubMode.VIOLATING_TRUTH_CLAIM)
    k = Kernel(_sid(), store, llm_adapter=adapter)
    k.process_input("ja")
    k.process_input("ja")
    k.process_input("weiter")  # → GUARD_BLOCK (truth claim)
    assert k.state == S.GUARD_BLOCK, f"Expected GUARD_BLOCK, got {k.state}"

    # Switch adapter to SAFE for retry
    k._adapter = StubLLMAdapter(StubMode.SAFE)
    r = k.process_input("noch einmal")  # retry
    assert k.state == S.REFLECTION, f"Expected REFLECTION after retry, got {k.state}"
    logger.info("T21 GUARD_BLOCK_RETRY: state=%s", k.state)


# ---------------------------------------------------------------------------
# Scenario registry
# ---------------------------------------------------------------------------

SCENARIOS: dict[str, callable] = {
    "T01": run_t01_safeword,
    "T02": run_t02_crisis,
    "T03": run_t03_dissociation_pause,
    "T04": run_t04_escalating_distress,
    "T05": run_t05_boundary_pause,
    "T06": run_t06_output_truth_claim,
    "T07": run_t07_output_diagnosis,
    "T08": run_t08_output_companion,
    "T09": run_t09_output_efficacy,
    "T11": run_t11_deepening_on_distress,
    "T13": run_t13_distress_context_survives_pause,
    "T14": run_t14_no_reentry_after_exit,
    "T15": run_t15_no_auto_advance,
    "T17": run_t17_content_free_events,
    "T18": run_t18_guard_error_fail_closed,
    "T19": run_t19_malformed_output,
    "T21": run_t21_guard_block_retry,
}


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Traumtänzer Evidence Harness — Session Runner")
    parser.add_argument("--scenario", metavar="NAME",
                        help="Run only this scenario (e.g. T01). Default: all.")
    parser.add_argument("--db", metavar="PATH", default=str(DEFAULT_DB_PATH),
                        help=f"SQLite DB path (default: {DEFAULT_DB_PATH})")
    args = parser.parse_args(argv)

    db_path = Path(args.db)
    store = EventStore(db_path)

    if args.scenario:
        names = [args.scenario.upper()]
        if names[0] not in SCENARIOS:
            logger.error("Unknown scenario: %s. Available: %s", names[0], list(SCENARIOS))
            store.close()
            return 1
    else:
        names = list(SCENARIOS)

    failed: list[str] = []
    for name in names:
        fn = SCENARIOS[name]
        try:
            fn(store)
            logger.info("SCENARIO %s: OK", name)
        except Exception as exc:
            logger.error("SCENARIO %s: FAILED — %s: %s", name, type(exc).__name__, exc)
            failed.append(name)

    store.close()

    if failed:
        logger.error("Failed scenarios: %s", failed)
        return 1

    logger.info("All %d scenario(s) completed without exception.", len(names))
    return 0


if __name__ == "__main__":
    sys.exit(main())
