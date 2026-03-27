"""
Kernel — Traumtänzer Evidence Harness

Session state machine and orchestrator per KERNEL_GUARD_CONTRACTS §3–§10.

Responsibilities:
  - Hold session state (RAM only, never persisted)
  - Call Input Guard before any LLM-Adapter call
  - Call Output Guard before any output reaches the caller
  - Trigger Safe-State transitions
  - Write redacted events to EventStore
  - Never expose user content in logs or events

Fail-closed invariant: any unresolvable state → EXIT immediately.
No auto-re-entry after EXIT or EXTERNAL_REFERRAL.
No auto-phase-transition without explicit user opt-in.

HARNESS-ONLY. Not for live user sessions.
"""

import logging
from typing import Optional

from .guards import (
    InputGuard, OutputGuard,
    InputDecision, OutputDecision, GuardCategory,
)
from .event_store import EventStore
from .llm_adapter import StubLLMAdapter
from .responses import RESPONSES
from .fault_injection import FaultInjector

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# State constants — per KERNEL_GUARD_CONTRACTS §3
# ---------------------------------------------------------------------------

class S:
    ENTRY = "ENTRY"
    CHECK_IN = "CHECK_IN"
    REFLECTION = "REFLECTION"
    PAUSED = "PAUSED"
    EXIT = "EXIT"
    EXTERNAL_REFERRAL = "EXTERNAL_REFERRAL"
    GUARD_BLOCK = "GUARD_BLOCK"


_TERMINAL = frozenset({S.EXIT, S.EXTERNAL_REFERRAL})


# ---------------------------------------------------------------------------
# Opt-in / exit-signal helpers
# ---------------------------------------------------------------------------

def _is_opt_in(text: str) -> bool:
    """Explicit opt-in detection. Silence / ambiguity is NOT opt-in (T15)."""
    t = text.strip().lower()
    _OPT_IN_TOKENS = {
        "ja", "yes", "ok", "okay", "weiter", "los",
        "bereit", "starten", "weitermachen", "ich möchte", "ich will",
    }
    return any(t == token or t.startswith(token + " ") or t.startswith(token + ",")
               for token in _OPT_IN_TOKENS)


def _is_exit_signal(text: str) -> bool:
    t = text.strip().lower()
    return any(sig in t for sig in ["stopp", "nein", "exit", "aufhören", "ende", "beenden"])


# ---------------------------------------------------------------------------
# Kernel
# ---------------------------------------------------------------------------

class Kernel:
    """
    Orchestrates a single session. One instance per session.
    session_id is externally provided (pseudonym, opaque).
    """

    def __init__(
        self,
        session_id: str,
        event_store: EventStore,
        llm_adapter: Optional[StubLLMAdapter] = None,
        fault_injector: Optional[FaultInjector] = None,
    ) -> None:
        self._session_id = session_id
        self._store = event_store
        self._adapter = llm_adapter
        self._fault = fault_injector or FaultInjector.none()

        # Session state — RAM only, never persisted
        self._state: str = S.ENTRY
        self._distress_count: int = 0
        self._distress_context_active: bool = False
        self._interpretation_request_active: bool = False

        # Guards share the same FaultInjector instance
        self._input_guard = InputGuard(self._fault)
        self._output_guard = OutputGuard(self._fault)

        # Session start events
        self._store.write(session_id, "SESSION_STARTED")
        logger.info("kernel_init session=%s state=%s", session_id[:8], self._state)

    # --- Public interface ---

    @property
    def state(self) -> str:
        return self._state

    def is_terminal(self) -> bool:
        return self._state in _TERMINAL

    def entry_text(self) -> str:
        """Predefined ENTRY text. No LLM."""
        return RESPONSES["ENTRY_TEXT"]

    def process_input(self, user_text: str) -> str:
        """
        Process one user input turn. Returns system response text.
        user_text is NEVER written to event store or app logs.
        """
        # Re-entry protection after terminal state (T14)
        if self.is_terminal():
            return RESPONSES["NEUTRAL_EXIT_CONFIRMATION"]

        # --- Input Guard ---
        guard_result = self._input_guard.check(user_text, self._distress_count)

        self._store.write(
            self._session_id,
            "INPUT_GUARD_RESULT",
            decision=guard_result.decision,
            guard_category=guard_result.guard_category,
        )

        # --- Route by Input Guard decision ---

        if guard_result.decision == InputDecision.ERROR_FAIL_CLOSED:
            return self._fail_closed("GUARD", "GUARD_ERROR")

        if guard_result.decision == InputDecision.BLOCK_EXIT:
            end = (
                "SAFEWORD"
                if guard_result.guard_category == GuardCategory.SAFEWORD
                else "GUARD_ABORT"
            )
            return self._to_exit(end)

        if guard_result.decision == InputDecision.BLOCK_REFER:
            return self._to_referral()

        if guard_result.decision == InputDecision.BLOCK_PAUSE:
            self._distress_count += 1
            self._distress_context_active = True
            return self._to_paused("BLOCK_PAUSE")

        if guard_result.decision == InputDecision.BLOCK_BOUNDARY:
            # Kernel decides severity: EXIT in REFLECTION (higher risk), else PAUSED
            if self._state == S.REFLECTION:
                return self._to_exit("GUARD_ABORT")
            return self._to_paused("BLOCK_BOUNDARY")

        # ALLOW or RESTRICT_OUTPUT
        if guard_result.decision == InputDecision.RESTRICT_OUTPUT:
            self._interpretation_request_active = True

        return self._handle_allowed_input(user_text)

    # --- State-specific handlers ---

    def _handle_allowed_input(self, user_text: str) -> str:
        state = self._state

        if state == S.ENTRY:
            # No auto-advance — explicit opt-in required (T15)
            if _is_opt_in(user_text):
                self._transition(S.ENTRY, S.CHECK_IN, "USER_OPT_IN")
                return RESPONSES["CHECK_IN_TEXT"]
            return RESPONSES["ENTRY_TEXT"]

        if state == S.CHECK_IN:
            if _is_opt_in(user_text):
                self._transition(S.CHECK_IN, S.REFLECTION, "USER_CONFIRMED")
                return self._llm_turn(user_text)
            return RESPONSES["CHECK_IN_TEXT"]

        if state == S.REFLECTION:
            return self._llm_turn(user_text)

        if state == S.PAUSED:
            # DISTRESS_CONTEXT_ACTIVE survives PAUSED → REFLECTION (T13)
            if _is_opt_in(user_text):
                self._transition(S.PAUSED, S.REFLECTION, "USER_GO")
                return self._llm_turn(user_text)
            return RESPONSES["NEUTRAL_PAUSE_RESPONSE"]

        if state == S.GUARD_BLOCK:
            if _is_exit_signal(user_text):
                return self._to_exit("NORMAL")
            # Kernel releases for one retry
            self._transition(S.GUARD_BLOCK, S.REFLECTION, "USER_RETRY")
            return self._llm_turn(user_text)

        # Unknown state — fail-closed
        return self._fail_closed("KERNEL", "UNKNOWN_STATE")

    # --- LLM turn ---

    def _llm_turn(self, user_text: str) -> str:
        """
        Call LLM adapter (stub), run Output Guard, return result.
        user_text is passed to the stub contract but never logged.
        """
        if self._adapter is None:
            return self._fail_closed("LLM_ADAPTER", "NO_ADAPTER_CONFIGURED")

        # Adapter call
        try:
            # Prompt context is minimal: session id prefix only (per DEPLOYMENT_ENVELOPE §4 TB-2)
            llm_output = self._adapter.generate(
                f"[harness-context session={self._session_id[:8]}]"
            )
        except Exception as exc:
            logger.error("llm_adapter_exception err=%s", type(exc).__name__)
            self._store.write(
                self._session_id, "SYSTEM_ERROR",
                error_code="ADAPTER_EXCEPTION",
                component="LLM_ADAPTER",
            )
            return self._fail_closed("LLM_ADAPTER", "ADAPTER_EXCEPTION")

        # Empty / malformed output (T19)
        if not llm_output or not isinstance(llm_output, str) or not llm_output.strip():
            self._store.write(
                self._session_id, "SYSTEM_ERROR",
                error_code="EMPTY_OR_INVALID_PROVIDER_OUTPUT",
                component="LLM_ADAPTER",
            )
            return self._fail_closed("LLM_ADAPTER", "EMPTY_OR_INVALID_PROVIDER_OUTPUT")

        # --- Output Guard ---
        out_result = self._output_guard.check(
            llm_output,
            distress_context_active=self._distress_context_active,
            interpretation_request_active=self._interpretation_request_active,
        )

        self._store.write(
            self._session_id,
            "OUTPUT_GUARD_RESULT",
            decision=out_result.decision,
            violation_type=out_result.violation_type,
        )

        if out_result.decision == OutputDecision.ERROR_FAIL_CLOSED:
            return self._fail_closed("GUARD", "OUTPUT_GUARD_ERROR")

        if out_result.decision == OutputDecision.BLOCK:
            # llm_output discarded — never reaches caller, never logged (T06–T09, T11)
            prev = self._state
            self._transition(prev, S.GUARD_BLOCK, "OUTPUT_GUARD_RESULT")
            return RESPONSES["NEUTRAL_GUARD_BLOCK_RESPONSE"]

        # ALLOW — reset interpretation flag, return output
        self._interpretation_request_active = False
        return llm_output

    # --- Transition helpers ---

    def _to_exit(self, end_type: str = "NORMAL") -> str:
        prev = self._state
        self._transition(prev, S.EXIT, "BLOCK_EXIT")
        self._store.write(
            self._session_id, "SESSION_ENDED",
            end_type=end_type,
            last_state=prev,
        )
        return RESPONSES["NEUTRAL_EXIT_CONFIRMATION"]

    def _to_referral(self) -> str:
        prev = self._state
        self._transition(prev, S.EXTERNAL_REFERRAL, "BLOCK_REFER")
        self._store.write(
            self._session_id, "SESSION_ENDED",
            end_type="REFERRAL",
            last_state=prev,
        )
        return RESPONSES["NEUTRAL_REFERRAL_RESPONSE"]

    def _to_paused(self, trigger: str = "BLOCK_PAUSE") -> str:
        prev = self._state
        self._transition(prev, S.PAUSED, trigger)
        return RESPONSES["NEUTRAL_PAUSE_RESPONSE"]

    def _fail_closed(self, component: str, error_code: str) -> str:
        """
        Fail-closed handler: log error, transition to EXIT.
        Logging failures must not prevent fail-closed behavior.
        """
        prev = self._state
        try:
            self._store.write(
                self._session_id, "SYSTEM_ERROR",
                error_code=error_code,
                component=component,
            )
        except Exception:
            pass
        self._transition(prev, S.EXIT, "ERROR_FAIL_CLOSED")
        try:
            self._store.write(
                self._session_id, "SESSION_ENDED",
                end_type="SYSTEM_ERROR",
                last_state=prev,
            )
        except Exception:
            pass
        return RESPONSES["NEUTRAL_ERROR_FAIL_CLOSED_RESPONSE"]

    def _transition(self, from_state: str, to_state: str, trigger: str) -> None:
        self._store.write(
            self._session_id,
            "SAFE_STATE_TRANSITION",
            from_state=from_state,
            to_state=to_state,
            trigger_event=trigger,
        )
        self._state = to_state
        logger.info(
            "state_transition session=%s %s→%s trigger=%s",
            self._session_id[:8], from_state, to_state, trigger,
        )
