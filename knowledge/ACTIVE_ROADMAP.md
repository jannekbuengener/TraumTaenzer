# ACTIVE_ROADMAP

Stand: 2026-03-30 – synchronisiert mit `main` (nach gemergtem PR-Stack #63–#65)

---

## Abgeschlossen (auf main)

- Governance-Canon: CONSTITUTION, GOVERNANCE, AGENT_POLICY, GOVERNANCE_QUICKREF, POLICY_STACK_MINI
- Domain-Canon (P0): CLAIMS_FRAMEWORK, SAFETY_PLAYBOOK, PRIVACY_BY_DESIGN, ARCHITECTURE_OVERVIEW
- Foundation: README, CODEOWNERS, CONTRIBUTING, SECURITY, SYSTEM_INVARIANTS, SYSTEM.CONTEXT
- UX-Kernsequenz: Entry → Check-in → Szene → Exit (UX_CORE_SEQUENCE.md)
- CI-Gates: CodeQL, Gitleaks, Dependency-Review, strukturelle Canon-Prüfung (PR #17, #18)
- Guardrails / Content Policy (PR #23): GUARDRAILS_CONTENT_POLICY.md
- Pilot-Readiness (PR #24): PILOT_READINESS.md
- Kernel-Guard-Contracts (PR #26): KERNEL_GUARD_CONTRACTS.md
- Text-First Runtime Flow (PR #28): TEXT_FIRST_RUNTIME_FLOW.md
- Prompt Construction Rules (PR #30): PROMPT_CONSTRUCTION_RULES.md
- Trivy-Action-Bump (PR #31): Infra-Fix, trivy-action auf 0.35.0
- Provider-/Adapter-Envelope + DPA-Input-Matrix (PR #39): DEPLOYMENT_ENVELOPE.md, PROVIDER_DPA_INPUT_MATRIX.md
- Mono-Safety-Incident-Logik (PR #40): Incident-Stufen und Postmortem-Minimum in PILOT_READINESS.md
- AI-Transparenz / Disclosure / Anti-Manipulation (PR #41): CLAIMS_FRAMEWORK.md, UX_CORE_SEQUENCE.md geschärft
- Data-Lifecycle-Matrix (PR #42): DATA_LIFECYCLE.md
- Bootstrap-Runtime-Grundpfad (PRs #63–#65): `harness/runtime_server.py`, `harness/runtime_tools.py`, `harness/inspect_events.py`, `harness/event_store.py`; `/health`, explizite absolute Pfade, fail-closed ohne Adapter, lokale DB-/Log-/Sidepath-Inspektion

---

## Now

- **Kein freigabefähiger externer LLM-Pfad** (P0-Blocker vor Live-Nutzer): fünf Pfade bewertet (Azure OpenAI, Anthropic Claude API, Amazon Bedrock, OpenAI API, IONOS AI Model Hub) – keiner `zulässig für Pilot`; Provider-Gate bleibt offen
- **Degraded mode ist kein Ersatzpilot**: degraded mode ist ausschließlich Safe-/Fehlerbetrieb; Live-Pilot nur mit freigegebenem externem LLM-Pfad; kein Non-LLM-Ersatzpilot im aktuellen MVP-Scope
- **Bootstrap-Runtime-Pfad vorhanden** (`harness/`): Kernel-Zustandsmaschine, deterministische Guards, content-freier SQLite-Event-Store, Stub-Adapter, Fault-Injection, Smoke-Check, Szenarien-Runner sowie `runtime_server.py` + `runtime_tools.py` auf `main`; Start / Stop / Health / Inspect lokal mit expliziten absoluten Pfaden und explizitem `workdir`-Scanroot belegbar; offen ist jetzt die Hetzner-Zielpfadbindung samt erster evidenzfähiger Rezeptur, nicht weiterer Runtime-Neubau; provider-gekoppelte Pflichtfälle bleiben `blockiert`

---

## Next

- `Hetzner Bootstrap Path Contract + First Evidence Recipe`: `app_root`, `workdir`, `volume_mount`, `db_path`, `log_path`, `pid_file`, `bind_host`, `bind_port` für genau einen realen Zielpfad festziehen; repo-seitig ist die explizite `workdir`-Bindung vorbereitet; vorhandenen Bootstrap-Pfad in der Sequenz `start -> health -> kurzer Session-Smoke -> inspect-db -> inspect-log -> inspect-sidepaths -> stop` fahren; Abschluss nur mit den vier Artefaktklassen aus `OPERATIONS_RUNBOOK §4`
- Export-/IAM-Pfad nur bei echtem Persistenzbedarf konkretisieren
- Non-LLM-MVP aktuell nicht Teil des MVP-Scope; nur falls separat entschieden: eigener Scope, kein Fallback des aktuellen Piloten und keine Voraussetzung für Pilotfreigabe im aktuellen Rahmen

---

## Later

- Deep-Layer optional (nur wenn Safety/Privacy stabil und Pilot ausgewertet)
- Outcome-Metriken (Abbrüche, Safety-Event-Rate) ohne Therapieclaim
- Externe Ressourcenliste über Deutschland hinaus erweitern
- Produktisierung: App-/Experience-Packaging, Audio/Soundscape, Skalierung
