# CURRENT_STATUS – Traumtänzer

Zuletzt aktualisiert: 2026-03-26

---

## Aktueller Stand

**Branch:** `main`
**PRs:** Docs-/Spec- und Sync-PRs bis #42 gemergt – Canon-Grundstock, Frame-Artefakte und CI-Infra auf `main`
**Phase:** Core-Canon und Frame-Artefakte gemergt; geprüft sind jetzt auch
alternative LLM-Pfade, aber der Pilot bleibt an produktionsnahen P0-Kanten und
fehlender Live-Provider-Freigabe blockiert

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
| Nach Bewertung von Azure OpenAI, Anthropic Claude API (`/v1/messages`) und Amazon Bedrock (`InvokeModel` + `anthropic.claude-sonnet-4-6`) ist aktuell kein LLM-Pfad freigabefähig; produktnahe Subprocessor-, Löschpfad- und Side-Artifact-Blocker bleiben live-relevant | P0 vor Live-Nutzer | PROVIDER_DPA_INPUT_MATRIX §7–§8 |
| Minimale Red-Team-/Prompt-Testbaseline ist kanonisch definiert; die Durchführung gegen reale Runtime inkl. Leak-/fail-closed-Nachweis bleibt offen | P0 vor Live-Nutzer | PROMPT_TEST_BASELINE, PILOT_READINESS §3.3 |
| Externe Ressourcenliste über Deutschland hinaus erweitern | bei Produktisierung | SAFETY_PLAYBOOK §7 |

---

## Nächster Schritt

Zwei P0-Blocker bleiben vor Live-Nutzern offen: Erstens ist nach belastbarer
Prüfung von Azure OpenAI, Anthropic Claude API und Amazon Bedrock weiterhin
kein freigabefähiger externer LLM-Providerpfad identifiziert. Zweitens fehlt
die dokumentierte Durchführung der minimalen Red-Team-/Prompt-Testbaseline
inklusive Leak- und fail-closed-Nachweisen. Der Infrastrukturpfad für reale
Pilot-Events ist dagegen jetzt konkret festgelegt: `Hetzner Cloud Server` in
`nbg1` mit angehängtem `Hetzner Volume` und lokalem `SQLite`-Event-Store.
Ohne diese zwei Nachweise bleibt der Pilot gesperrt.
