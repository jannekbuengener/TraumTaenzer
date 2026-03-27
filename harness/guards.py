"""
Input and Output Guards — Traumtänzer Evidence Harness

Deterministic, rule-based guards per KERNEL_GUARD_CONTRACTS §5–§6,
GUARDRAILS_CONTENT_POLICY §3–§4.

NO LLM calls. NO inference. Pattern lists are intentionally visible for review.

Input Guard: checks user input before any LLM call.
Output Guard: checks LLM output before it reaches the UI.

Priority order (KERNEL_GUARD_CONTRACTS §10):
  BLOCK_EXIT > BLOCK_REFER > BLOCK_PAUSE > BLOCK_BOUNDARY > RESTRICT_OUTPUT > ALLOW

HARNESS-ONLY. Not for live user sessions.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .fault_injection import FaultInjector, FaultType

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Decision enums — must match KERNEL_GUARD_CONTRACTS §5
# ---------------------------------------------------------------------------

class InputDecision(str, Enum):
    ALLOW = "ALLOW"
    BLOCK_EXIT = "BLOCK_EXIT"
    BLOCK_REFER = "BLOCK_REFER"
    BLOCK_PAUSE = "BLOCK_PAUSE"
    BLOCK_BOUNDARY = "BLOCK_BOUNDARY"
    RESTRICT_OUTPUT = "RESTRICT_OUTPUT"
    ERROR_FAIL_CLOSED = "ERROR_FAIL_CLOSED"


class GuardCategory(str, Enum):
    SAFEWORD = "SAFEWORD"
    CRISIS = "CRISIS"
    DISTRESS = "DISTRESS"
    DISSOCIATION = "DISSOCIATION"
    BOUNDARY_REQUEST = "BOUNDARY_REQUEST"
    INTERPRETATION_REQUEST = "INTERPRETATION_REQUEST"
    ALLOW = "ALLOW"
    ERROR = "ERROR"


class OutputDecision(str, Enum):
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    ERROR_FAIL_CLOSED = "ERROR_FAIL_CLOSED"


class ViolationType(str, Enum):
    DIAGNOSIS = "DIAGNOSIS"
    COMPANION = "COMPANION"
    EFFICACY_CLAIM = "EFFICACY_CLAIM"
    REFRAME_AFTER_EXIT = "REFRAME_AFTER_EXIT"
    DEEPENING_ON_DISTRESS = "DEEPENING_ON_DISTRESS"
    TRUTH_CLAIM = "TRUTH_CLAIM"
    OTHER = "OTHER"


@dataclass
class InputGuardResult:
    decision: InputDecision
    guard_category: GuardCategory


@dataclass
class OutputGuardResult:
    decision: OutputDecision
    violation_type: Optional[ViolationType] = None


# ---------------------------------------------------------------------------
# Input guard pattern lists (all lowercase; matched via substring)
# Per GUARDRAILS_CONTENT_POLICY §3
# ---------------------------------------------------------------------------

# BLOCK_EXIT: Safeword + explicit abort
_SAFEWORD_PATTERNS = ["stopp"]
_EXPLICIT_ABORT_PATTERNS = [
    "ich will aufhören", "ich möchte aufhören",
    "ich will stoppen", "ich möchte stoppen",
    "aufhören", "beenden", "abbrechen",
]

# BLOCK_REFER: Crisis language / acute risk
_CRISIS_PATTERNS = [
    "suizid", "selbstmord", "umbringen",
    "nicht mehr leben", "kein ausweg", "keinen ausweg",
    "mir etwas antun", "töten", "sterben wollen",
    "ich denke daran zu sterben", "ich möchte tot sein",
    "alles sinnlos", "ich kann nicht mehr",
    "ich sehe keinen ausweg", "keinen sinn mehr",
]

# BLOCK_PAUSE: Dissociation / disorientation
_DISSOCIATION_PATTERNS = [
    "wo bin ich", "ich bin weg", "alles verschwimmt",
    "ich spüre mich nicht", "ich bin nicht hier",
    "ich fühle mich nicht", "alles dreht sich",
    "ich verliere den boden", "völlig überwältigt und weiß nicht mehr",
]

# BLOCK_BOUNDARY: Diagnosis or therapy request
_BOUNDARY_PATTERNS = [
    "bin ich traumatisiert", "was ist mit mir",
    "welche diagnose", "welche therapie", "therapieform",
    "therapeut empfehlen", "klinische einschätzung",
    "analysiere mein muster", "analysiere mich",
    "psychologische analyse",
    "stell dir vor du bist ein therapeut",
    "sei ein therapeut", "spiel einen therapeuten",
]

# RESTRICT_OUTPUT: Interpretation request (LLM allowed, Output Guard elevated)
_INTERPRETATION_PATTERNS = [
    "was bedeutet", "was symbolisiert",
    "bedeutung von", "interpretier",
    "deutung", "wirklich bedeutet",
    "was könnte", "was steht für",
]


# ---------------------------------------------------------------------------
# Output guard pattern lists (all lowercase; matched via substring)
# Per GUARDRAILS_CONTENT_POLICY §4, §8
# ---------------------------------------------------------------------------

_OUT_DIAGNOSIS_PATTERNS = [
    "du hast anzeichen", "das klingt wie eine traumareaktion",
    "du leidest", "das ist eine reaktion auf",
    "du zeigst symptome", "traumatisiert bist",
]

_OUT_TRUTH_CLAIM_PATTERNS = [
    "dein traum zeigt", "dein traum bedeutet",
    "das zeigt dass du", "das bedeutet",
    "das ist ein zeichen für", "dein muster ist",
    "du trägst unverarbeitete", "dein unbewusstes",
]

_OUT_COMPANION_PATTERNS = [
    "ich bin für dich da", "ich begleite dich",
    "egal was kommt", "immer für dich da",
    "ich bin immer", "du kannst mir immer",
]

_OUT_EFFICACY_PATTERNS = [
    "das wird dir helfen", "du wirst dich besser fühlen",
    "du wirst heilen", "wird dich heilen",
    "hilft dir beim heilen",
]

_OUT_DEEPENING_PATTERNS = [
    "lass uns tiefer", "gehen wir tiefer",
    "vertiefen wir", "tauchen wir tiefer ein",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _contains_any(text: str, patterns: list[str]) -> bool:
    t = text.lower()
    return any(p in t for p in patterns)


# ---------------------------------------------------------------------------
# Guards
# ---------------------------------------------------------------------------

class InputGuard:
    """
    Deterministic input guard.
    Per KERNEL_GUARD_CONTRACTS §5: no LLM, no inference.
    """

    def __init__(self, fault_injector: Optional[FaultInjector] = None) -> None:
        self._fault = fault_injector or FaultInjector.none()

    def check(self, text: str, distress_count: int = 0) -> InputGuardResult:
        """Check user input. text is RAM-only — never logged here."""
        if self._fault.active(FaultType.GUARD_ERROR):
            logger.warning("input_guard_fault_injected type=GUARD_ERROR")
            return InputGuardResult(InputDecision.ERROR_FAIL_CLOSED, GuardCategory.ERROR)

        try:
            return self._evaluate(text, distress_count)
        except Exception as exc:
            logger.error("input_guard_exception err=%s", type(exc).__name__)
            return InputGuardResult(InputDecision.ERROR_FAIL_CLOSED, GuardCategory.ERROR)

    def _evaluate(self, text: str, distress_count: int) -> InputGuardResult:
        # Priority: BLOCK_EXIT > BLOCK_REFER > BLOCK_PAUSE > BLOCK_BOUNDARY > RESTRICT_OUTPUT > ALLOW

        if _contains_any(text, _SAFEWORD_PATTERNS) or _contains_any(text, _EXPLICIT_ABORT_PATTERNS):
            return InputGuardResult(InputDecision.BLOCK_EXIT, GuardCategory.SAFEWORD)

        if _contains_any(text, _CRISIS_PATTERNS):
            return InputGuardResult(InputDecision.BLOCK_REFER, GuardCategory.CRISIS)

        if _contains_any(text, _DISSOCIATION_PATTERNS):
            return InputGuardResult(InputDecision.BLOCK_PAUSE, GuardCategory.DISSOCIATION)

        # Escalating distress: 3+ signals without exit → BLOCK_PAUSE
        if distress_count >= 3:
            return InputGuardResult(InputDecision.BLOCK_PAUSE, GuardCategory.DISTRESS)

        if _contains_any(text, _BOUNDARY_PATTERNS):
            return InputGuardResult(InputDecision.BLOCK_BOUNDARY, GuardCategory.BOUNDARY_REQUEST)

        if _contains_any(text, _INTERPRETATION_PATTERNS):
            return InputGuardResult(
                InputDecision.RESTRICT_OUTPUT, GuardCategory.INTERPRETATION_REQUEST
            )

        return InputGuardResult(InputDecision.ALLOW, GuardCategory.ALLOW)


class OutputGuard:
    """
    Deterministic output guard.
    Per KERNEL_GUARD_CONTRACTS §5: no LLM, no inference.
    """

    def __init__(self, fault_injector: Optional[FaultInjector] = None) -> None:
        self._fault = fault_injector or FaultInjector.none()

    def check(
        self,
        text: str,
        distress_context_active: bool = False,
        interpretation_request_active: bool = False,
    ) -> OutputGuardResult:
        """Check LLM output. text is RAM-only — never logged here."""
        if self._fault.active(FaultType.OUTPUT_GUARD_ERROR):
            logger.warning("output_guard_fault_injected type=OUTPUT_GUARD_ERROR")
            return OutputGuardResult(OutputDecision.ERROR_FAIL_CLOSED)

        try:
            return self._evaluate(text, distress_context_active, interpretation_request_active)
        except Exception as exc:
            logger.error("output_guard_exception err=%s", type(exc).__name__)
            return OutputGuardResult(OutputDecision.ERROR_FAIL_CLOSED)

    def _evaluate(
        self,
        text: str,
        distress_context_active: bool,
        interpretation_request_active: bool,
    ) -> OutputGuardResult:
        if _contains_any(text, _OUT_DIAGNOSIS_PATTERNS):
            return OutputGuardResult(OutputDecision.BLOCK, ViolationType.DIAGNOSIS)

        if _contains_any(text, _OUT_TRUTH_CLAIM_PATTERNS):
            return OutputGuardResult(OutputDecision.BLOCK, ViolationType.TRUTH_CLAIM)

        if _contains_any(text, _OUT_COMPANION_PATTERNS):
            return OutputGuardResult(OutputDecision.BLOCK, ViolationType.COMPANION)

        if _contains_any(text, _OUT_EFFICACY_PATTERNS):
            return OutputGuardResult(OutputDecision.BLOCK, ViolationType.EFFICACY_CLAIM)

        if distress_context_active and _contains_any(text, _OUT_DEEPENING_PATTERNS):
            return OutputGuardResult(OutputDecision.BLOCK, ViolationType.DEEPENING_ON_DISTRESS)

        return OutputGuardResult(OutputDecision.ALLOW)
