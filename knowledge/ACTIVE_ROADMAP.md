# ACTIVE_ROADMAP

Stand: 2026-03-26 – synchronisiert mit `main` (nach gemergter Docs-/Spec-Kette bis PR #42)

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

- **Konkreten Providerpfad per `PROVIDER_DPA_INPUT_MATRIX.md` positiv bewerten** (P0 vor Live-Nutzer)
- **Retention-, Lösch- und Event-Storage-Enforcement** gegen konkrete Infrastruktur validieren (P0 vor Live-Nutzer)
- **Red-Team-/Prompt-Tests** auf Basis der Guardrails-, Prompt- und Pilot-Artefakte

---

## Next

- Export-/IAM-Pfad nur bei echtem Persistenzbedarf konkretisieren

---

## Later

- Deep-Layer optional (nur wenn Safety/Privacy stabil und Pilot ausgewertet)
- Outcome-Metriken (Abbrüche, Safety-Event-Rate) ohne Therapieclaim
- Externe Ressourcenliste über Deutschland hinaus erweitern
- Produktisierung: App-/Experience-Packaging, Audio/Soundscape, Skalierung
