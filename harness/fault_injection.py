"""
Fault Injection Controls — Traumtänzer Evidence Harness

Enables local simulation of guard errors and adapter failures for
evidence runs of T18, T19 (and local variant of T20) per PROMPT_TEST_BASELINE.

Usage: pass a FaultInjector instance to Kernel, InputGuard, OutputGuard.
At most one FaultType is active per run.

T18 — Guard fault:      FaultInjector.guard_error()
T19 — Malformed output: FaultInjector.malformed_output()
T20 — Adapter error:    FaultInjector.adapter_error()
        (local variant only; real network/transport errors remain provider-coupled)

HARNESS-ONLY. Not for live use.
"""

from enum import Enum
from typing import Optional


class FaultType(str, Enum):
    GUARD_ERROR = "GUARD_ERROR"
    # Input guard or output guard raises / returns error → ERROR_FAIL_CLOSED → EXIT
    # Maps to PROMPT_TEST_BASELINE T18

    OUTPUT_GUARD_ERROR = "OUTPUT_GUARD_ERROR"
    # Output guard specifically fails — variant of T18

    MALFORMED_OUTPUT = "MALFORMED_OUTPUT"
    # LLM adapter returns empty or non-string response
    # Maps to PROMPT_TEST_BASELINE T19

    ADAPTER_ERROR = "ADAPTER_ERROR"
    # LLM adapter raises an exception
    # Maps to PROMPT_TEST_BASELINE T20 (local variant; real network errors are provider-coupled)


class FaultInjector:
    """
    Carries exactly one active fault type, or none.
    Passed to Kernel, InputGuard, OutputGuard, StubLLMAdapter.
    """

    def __init__(self, fault: Optional[FaultType] = None) -> None:
        self._fault = fault

    def active(self, fault_type: FaultType) -> bool:
        return self._fault == fault_type

    # --- Named constructors ---

    @classmethod
    def none(cls) -> "FaultInjector":
        """No fault injection — normal operation."""
        return cls(None)

    @classmethod
    def guard_error(cls) -> "FaultInjector":
        """T18: Input guard timeout / error → ERROR_FAIL_CLOSED → EXIT."""
        return cls(FaultType.GUARD_ERROR)

    @classmethod
    def output_guard_error(cls) -> "FaultInjector":
        """T18 variant: Output guard error → ERROR_FAIL_CLOSED → EXIT."""
        return cls(FaultType.OUTPUT_GUARD_ERROR)

    @classmethod
    def malformed_output(cls) -> "FaultInjector":
        """T19: Adapter returns empty / invalid output → fail-closed."""
        return cls(FaultType.MALFORMED_OUTPUT)

    @classmethod
    def adapter_error(cls) -> "FaultInjector":
        """T20 local variant: Adapter raises exception → fail-closed."""
        return cls(FaultType.ADAPTER_ERROR)
