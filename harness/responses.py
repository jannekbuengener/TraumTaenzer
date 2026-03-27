"""
Predefined Kernel Response Bank — Traumtänzer Evidence Harness

Per KERNEL_GUARD_CONTRACTS §3, TEXT_FIRST_RUNTIME_FLOW §2–§6,
GUARDRAILS_CONTENT_POLICY §6.

These are the only outputs the Kernel generates for Safe States and errors.
No LLM involvement. No content improvisation.

HARNESS-ONLY. Not for live user sessions.
"""

RESPONSES: dict[str, str] = {
    # ENTRY: KI-Transparenz, Safeword-Einführung, Opt-in-Frage
    # Per UX_CORE_SEQUENCE §4, KERNEL_GUARD_CONTRACTS §3
    "ENTRY_TEXT": (
        "Dieses System ist ein KI-gestütztes Reflexionsformat — kein Therapeut, "
        "keine Krisenhilfe, kein Notfallangebot.\n"
        "Du kannst jederzeit mit dem Wort 'Stopp' die Session beenden.\n"
        "Möchtest du beginnen? (ja / nein)"
    ),

    # CHECK_IN: Offene Bereitschaftsfrage, kein Druck
    # Per UX_CORE_SEQUENCE §5, KERNEL_GUARD_CONTRACTS §3
    "CHECK_IN_TEXT": (
        "Wie geht es dir gerade? Bist du bereit, ein bisschen Zeit für dich zu nehmen?"
    ),

    # Safe-State-Antworten: vordefiniert, kein LLM
    "NEUTRAL_EXIT_CONFIRMATION": (
        "Ich stoppe. Du kannst jederzeit neu beginnen."
    ),
    "NEUTRAL_REFERRAL_RESPONSE": (
        "Notruf 112 · TelefonSeelsorge 0800 111 0 111\n"
        "Die Session wurde beendet."
    ),
    "NEUTRAL_PAUSE_RESPONSE": (
        "Ich mache eine Pause. "
        "Du kannst jederzeit weitermachen oder mit 'Stopp' beenden."
    ),
    "NEUTRAL_GUARD_BLOCK_RESPONSE": (
        "Diese Antwort kann ich nicht ausgeben. "
        "Möchtest du weitermachen oder stoppen?"
    ),
    "NEUTRAL_ERROR_FAIL_CLOSED_RESPONSE": (
        "Ein Fehler ist aufgetreten. Die Session wurde beendet."
    ),
    "NEUTRAL_BOUNDARY_RESPONSE": (
        "Das liegt außerhalb meines Bereichs. "
        "Für fachliche Unterstützung wende dich bitte an eine Fachstelle."
    ),
}
