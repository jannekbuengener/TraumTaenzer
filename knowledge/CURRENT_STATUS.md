# CURRENT_STATUS – Traumtänzer

Zuletzt aktualisiert: 2026-03-26

---

## Aktueller Stand

**Branch:** `main`
**PRs:** Docs-/Spec- und Sync-PRs bis #42 gemergt – Canon-Grundstock, Frame-Artefakte und CI-Infra auf `main`
**Phase:** Core-Canon und Frame-Artefakte gemergt; offen sind nur noch produktionsnahe P0-Kanten und Test-Evidenz

---

## Was steht (auf main, gemergt)

### Governance-Canon
- `knowledge/governance/CONSTITUTION.md` – komplett, projektspezifisch
- `knowledge/governance/GOVERNANCE.md` – Solo-Maintainer-Modell, PR-Pflicht, Evidence-Schwellen
- `knowledge/governance/AGENT_POLICY.md` – Agenten-Regeln, verbotene Muster
- `knowledge/governance/GOVERNANCE_QUICKREF.md` – operative Kurzreferenz
- `knowledge/governance/POLICY_STACK_MINI.md` – Konflikthierarchie

### Domain-Canon (P0)
- `knowledge/project/CLAIMS_FRAMEWORK.md` – zulässige/unzulässige Claims, Red Flags, Disclosure-Minimum
- `knowledge/project/SAFETY_PLAYBOOK.md` – Exit-First, Safeword, Trigger-Handling
- `knowledge/project/PRIVACY_BY_DESIGN.md` – Datensparsamkeit, Retention, Löschung
- `knowledge/project/DATA_LIFECYCLE.md` – Datenklassen, Event-Typen, Retention-/Export-Rahmen
- `knowledge/project/PROVIDER_DPA_INPUT_MATRIX.md` – Provider-Intake vor Live-Nutzer
- `knowledge/architecture/ARCHITECTURE_OVERVIEW.md` – Kernel, Guards, Adapter-Grenzen, fail-closed

### Content Policy & UX (P1 – gemergt)
- `knowledge/project/GUARDRAILS_CONTENT_POLICY.md` – Guard-Kriterien, erlaubte/verbotene Systemverhalten (PR #23)
- `knowledge/project/UX_CORE_SEQUENCE.md` – Entry → Check-in → Szene → Exit, Transparenz an risikorelevanten Stellen

### Architecture-Specs (P1 – gemergt)
- `knowledge/architecture/KERNEL_GUARD_CONTRACTS.md` – technische Vertragsvorlagen (PR #26)
- `knowledge/architecture/TEXT_FIRST_RUNTIME_FLOW.md` – Happy Path, Safe-State-Übergänge (PR #28)
- `knowledge/architecture/PROMPT_CONSTRUCTION_RULES.md` – Prompt-Sicherheit, Redaction-Regeln (PR #30)
- `knowledge/architecture/DEPLOYMENT_ENVELOPE.md` – Mono-MVP-Topologie, Trust Boundaries, Provider-/Secrets-Grenzen

### Ops (gemergt)
- `knowledge/ops/PILOT_READINESS.md` – Go/No-Go-Kriterien, Stop-Kriterien und Incident-/Eskalationslogik für den Pilot

### Foundation
- `README.md` – projektspezifisch, kein generisches Repo-Pack mehr
- `CODEOWNERS` – korrekt gesetzt (@jannekbuengener)
- `CONTRIBUTING.md` – auf Solo-Maintainer + KI-Zuarbeit zugeschnitten
- `SECURITY.md` – realistischer Meldeweg, Scope klar
- `knowledge/SYSTEM.CONTEXT.md` – reale Umgebungs- und Tool-Fakten
- `knowledge/SYSTEM_INVARIANTS.md` – harte, bindende Invarianten aus allen Domain-Canons

### Hub
- `knowledge/KNOWLEDGE_HUB.md` – zentraler Einstiegspunkt in alle Canon-Dokumente

### CI/Infra
- CI-Gates: CodeQL, Gitleaks, Dependency-Review, strukturelle Canon-Prüfung
- Trivy-Action auf 0.35.0 (PR #31)

---

## Was noch offen ist

| Punkt | Priorität | Referenz |
|---|---|---|
| Nach negativer Bewertung des Azure-OpenAI-Arbeitskandidaten einen live-tauglichen LLM-Pfad belastbar klären oder die Microsoft-Blocker für Retention, Subprocessor und Löschpfad schließen | P0 vor Live-Nutzer | PROVIDER_DPA_INPUT_MATRIX §7–§8 |
| Konkreten Pilot-Event-Storage-/Hosting-Pfad benennen; bis dahin bleibt Retention-, Lösch- und Event-Storage-Enforcement für reale Events live-blockiert | P0 vor Live-Nutzer | DATA_LIFECYCLE §6, DEPLOYMENT_ENVELOPE §7, PILOT_READINESS §3.4 |
| Red-Team-/Prompt-Tests auf Basis Guardrails + Prompt-Rules | aktiv | GUARDRAILS_CONTENT_POLICY, PROMPT_CONSTRUCTION_RULES |
| Pseudonymisierungs-/Session-ID-Entscheid vor Produktionsstart konkretisieren | vor Produktionsstart | DATA_LIFECYCLE §8 |
| Externe Ressourcenliste über Deutschland hinaus erweitern | bei Produktisierung | SAFETY_PLAYBOOK §7 |

---

## Nächster Schritt

Zwei P0-Blocker bleiben vor Live-Nutzern offen: Erstens ein konkret
freigabefähiger LLM-Providerpfad. Zweitens ein konkret benannter
Pilot-Event-Storage-/Hosting-Pfad, auf dem 90-/30-Tage-Retention,
automatische Löschung und Backup-/Nebenlogik technisch belegbar durchgesetzt
werden können. Ohne diese beiden Nachweise bleibt der Pilot gesperrt.
