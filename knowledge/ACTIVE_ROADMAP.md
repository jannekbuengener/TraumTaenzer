# ACTIVE_ROADMAP

Stand: 2026-04-03 – gespiegelt auf den aktuellen Canon-Stand inkl. interner Testmodus-Basis

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

---

## Now

- **Kein freigabefähiger externer LLM-Pfad** (P0-Blocker vor Live-Nutzer): fünf Pfade bewertet (Azure OpenAI, Anthropic Claude API, Amazon Bedrock, OpenAI API, IONOS AI Model Hub) – keiner `zulässig für Pilot`; OpenAI bleibt im Standardpfad `nicht zulässig für Live-Nutzer`; Provider-Gate bleibt offen
- **Degraded mode ist kein Ersatzpilot**: degraded mode ist ausschließlich Safe-/Fehlerbetrieb; Live-Pilot nur mit freigegebenem externem LLM-Pfad
- **Provider-neutraler maintainer-only interner Testmodus ist nur Arbeitsmodus**: befristeter Aufbaupfad auf kontrolliertem Systempfad für interne System-Evidence; kein Pilot, kein Live-Pfad und kein Provider-Go
- **Lokales Harness vorhanden** (`harness/`): Kernel-Zustandsmaschine, deterministische Guards, content-freier SQLite-Event-Store, Stub-Adapter, Fault-Injection, Smoke-Check und Szenarien-Runner implementiert; nicht-provider-gekoppelte Testfälle lokal ausführbar; Hetzner-deploybare Runtime fehlt weiterhin; Vorbedingungsliste für Hetzner-Pfad in `OPERATIONS_RUNBOOK §3`; provider-gekoppelte Pflichtfälle bleiben `blockiert`

---

## Next

- Interne Testläufe nur zur System-/Containment-Evidence nutzen und strikt getrennt von Pilot-/Provider-Freigabe halten; das offene Provider-Gate bleibt eigene P0-Lücke
- Export-/IAM-Pfad nur bei echtem Persistenzbedarf konkretisieren
- Non-LLM-MVP nur falls separat entschieden: eigener Scope, kein Fallback des aktuellen Piloten und keine Voraussetzung für Pilotfreigabe im aktuellen Rahmen

---

## Later

- Deep-Layer optional (nur wenn Safety/Privacy stabil und Pilot ausgewertet)
- Outcome-Metriken (Abbrüche, Safety-Event-Rate) ohne Therapieclaim
- Externe Ressourcenliste über Deutschland hinaus erweitern
- Produktisierung: App-/Experience-Packaging, Audio/Soundscape, Skalierung
