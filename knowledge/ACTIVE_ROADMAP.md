# ACTIVE_ROADMAP

Stand: 2026-03-25 – synchronisiert mit `main` (nach Merge PR #16, #17, #18)

---

## Abgeschlossen (auf main)

- Governance-Canon: CONSTITUTION, GOVERNANCE, AGENT_POLICY, GOVERNANCE_QUICKREF, POLICY_STACK_MINI
- Domain-Canon (P0): CLAIMS_FRAMEWORK, SAFETY_PLAYBOOK, PRIVACY_BY_DESIGN, ARCHITECTURE_OVERVIEW
- Foundation: README, CODEOWNERS, CONTRIBUTING, SECURITY, SYSTEM_INVARIANTS, SYSTEM.CONTEXT
- UX-Kernsequenz: Entry → Check-in → Szene → Exit (UX_CORE_SEQUENCE.md)
- CI-Gates: CodeQL, Gitleaks, Dependency-Review, strukturelle Canon-Prüfung (PR #17, #18)

---

## Now

- **Guardrails / Content Policy** (#19): verbotene und erlaubte Systemverhalten konkretisieren; Guard-Kriterien für Input, Output und Session-Übergänge aus dem Canon ableiten; fail-closed verankern
- **Pilot-Readiness** (#21): Mindestvoraussetzungen für text-first Pilot definieren; Eintrittskriterien, Stop-Kriterien, Safety- und Privacy-Basics vor erstem Nutzerkontakt sichern

---

## Next

- Provider-DPAs für externe KI-/Hosting-Dienste klären (P0 vor Produktionsstart)
- Retention-Fristen gegen konkrete Infrastruktur validieren (P0 vor Produktionsstart)
- Red-Team-/Prompt-Tests auf Basis Guardrails-Artefakt (nach #19)
- AI Act Readiness Check (Disclosure, Content-Labeling, Anti-Manipulation)
- Support/Incident Ops minimal (Crisis-Templates, Postmortems)

---

## Later

- Deep-Layer optional (nur wenn Safety/Privacy stabil und Pilot ausgewertet)
- Outcome-Metriken (Abbrüche, Safety-Event-Rate) ohne Therapieclaim
- Externe Ressourcenliste über Deutschland hinaus erweitern
- Produktisierung: App-/Experience-Packaging, Audio/Soundscape, Skalierung
