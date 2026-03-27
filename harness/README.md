# Traumtänzer Evidence Harness

**HARNESS-ONLY. Not for live user sessions.**

---

## Was das ist

Minimale lokale Runtime-Substanz für deterministische Evidence-Läufe.
Kein externer LLM-Provider. Keine echten Nutzer. Kein Netzwerk. Kein Deployment.

Implementiert:
- Kanonische Kernel-Zustandsmaschine (ENTRY → CHECK_IN → REFLECTION → … → EXIT)
- Deterministische Guards (Input + Output) per KERNEL_GUARD_CONTRACTS §5–§6
- Content-freier SQLite-Event-Store (session_id + Enums, niemals User-Text oder LLM-Output)
- Stub-LLM-Adapter mit konfigurierbarem StubMode (SAFE + vier verbotene Muster)
- Fault-Injection für T18 (Guard-Error), T19 (Malformed Output), T20 lokal (Adapter-Exception)

---

## Was das NICHT ist

- Kein Ersatz für reale Provider-gekoppelte Evidence (T01–T21 mit echtem LLM)
- Kein Pilot-Scope und kein degraded-Mode-Ersatz
- Kein Beweis, dass die Guards in einer Live-Runtime korrekt verhalten
- Keine produktionsreife Komponente

Provider-gekoppelte Testfälle (TB-2) bleiben `blockiert` bis ein freigegebener
externer LLM-Pfad vorliegt. Nicht-provider-gekoppelte Fälle ohne
Runtime-/Deploy-/Runbook-Artefakte sind `Vorbedingung fehlt`, nicht `bestanden`.
Dieser Harness ist ein Schritt in Richtung operative Ausführbarkeit — nicht mehr.

---

## Voraussetzungen

- Python 3.11+
- Nur Python-Stdlib (sqlite3, logging, uuid, pathlib, argparse) — keine weiteren Pakete

---

## Ausführen

```bash
# Smoke-Check (Start/Stop/Health)
python -m harness.smoke_check

# Alle Szenarien laufen lassen
python -m harness.run_session

# Einzelnes Szenario
python -m harness.run_session --scenario T01

# Event-Store inspizieren
python -m harness.inspect_events

# Nur Schema-/Leak-Check (kein Output)
python -m harness.inspect_events --check-only

# Bestimmte Session
python -m harness.inspect_events --session harness-abc123
```

Alle Skripte schreiben in `harness/data/events.db` (gitignored).
Exit-Code 0 = ohne Ausnahme abgeschlossen; 1 = mindestens ein Fehler.

---

## Testfall-Abdeckung

| ID  | Beschreibung                                 | Typ                  | Status hier        |
|-----|----------------------------------------------|----------------------|--------------------|
| T01 | BLOCK_EXIT via Safeword                      | lokal                | ausführbar         |
| T02 | BLOCK_REFER via Krisensprache                | lokal                | ausführbar         |
| T03 | BLOCK_PAUSE via Dissoziationssignal          | lokal                | ausführbar         |
| T04 | Eskalierender Distress (3× Signal)           | lokal                | ausführbar         |
| T05 | BLOCK_BOUNDARY (Diagnose-/Therapie-Anfrage)  | lokal                | ausführbar         |
| T06 | Output-Guard: Truth-Claim blockiert          | Stub-Adapter         | ausführbar         |
| T07 | Output-Guard: Diagnose blockiert             | Stub-Adapter         | ausführbar         |
| T08 | Output-Guard: Companion-Rhetorik blockiert   | Stub-Adapter         | ausführbar         |
| T09 | Output-Guard: Efficacy-Claim blockiert       | Stub-Adapter         | ausführbar         |
| T10 | Reframe-after-Exit                           | provider-gekoppelt   | blockiert (TB-2)   |
| T11 | Deepening-on-Distress blockiert              | Stub-Adapter         | ausführbar         |
| T12 | Mehrfachsignale keine Auto-Eskalation        | provider-gekoppelt   | blockiert (TB-2)   |
| T13 | distress_context_active überlebt PAUSED→REFLECTION | lokal          | ausführbar         |
| T14 | Kein Re-Entry nach EXIT                      | lokal                | ausführbar         |
| T15 | Kein Auto-Phase-Übergang ohne Opt-In         | lokal                | ausführbar         |
| T16 | Opt-In-Erkennung (Tokenprüfung)              | lokal                | ausführbar (in T15)|
| T17 | Content-freie Events (kein User-Text)        | lokal                | ausführbar         |
| T18 | Guard-Error → ERROR_FAIL_CLOSED → EXIT       | Fault-Injection      | ausführbar         |
| T19 | Malformed Output → fail-closed → EXIT        | Fault-Injection      | ausführbar         |
| T20 | Adapter-Exception → fail-closed → EXIT       | Fault-Injection lok. | ausführbar (lokal) |
| T21 | GUARD_BLOCK → User-Retry → REFLECTION        | Stub-Adapter         | ausführbar         |

Providergekoppelte Fälle (T10, T12) bleiben `blockiert` bis TB-2 freigegeben ist.

---

## Dateistruktur

```
harness/
  __init__.py           Package-Marker
  responses.py          Predefined Kernel-Texte (kein LLM)
  fault_injection.py    FaultInjector (T18/T19/T20 lokal)
  event_store.py        SQLite-Event-Store (content-free)
  llm_adapter.py        Stub-LLM-Adapter (StubMode + FaultInjector)
  guards.py             Input- und Output-Guard (deterministisch)
  kernel.py             Kernel-Zustandsmaschine (Session-Orchestrator)
  run_session.py        Scripted Szenarien-Runner
  smoke_check.py        Start/Stop/Health-Verifikation
  inspect_events.py     Event-Store-Inspektion + Leak-Check
  data/
    .gitkeep            Verzeichnis-Platzhalter (events.db gitignored)
```
