# CURRENT_STATUS – Traumtänzer

Zuletzt aktualisiert: 2026-03-26

---

## Aktueller Stand

**Branch:** `main`
**PRs:** Docs-/Spec- und Sync-PRs bis #56 gemergt – Canon-Grundstock,
Provider- und Infrastrukturentscheide auf `main`
**Phase:** Core-Canon, Providerprüfung, Pilot-Infrastrukturpfad und die auf die
konkrete Zielumgebung gespiegelt definierte MVP-Evidence-Baseline stehen; die
dokumentierte reale Durchführung der Pflichtfälle steht aber weiterhin aus, und
providergekoppelte Fälle bleiben zusätzlich an der offenen
Live-Provider-Freigabe blockiert

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
| Die minimale Red-Team-/Prompt-Testbaseline ist jetzt auf den freigegebenen Pilotpfad (`Hetzner Cloud Server` in `nbg1` + `Hetzner Volume` + lokales `SQLite`) gespiegelt; dokumentierte Pflichtnachweise für Leak-/Redaction, fail-closed und fehlende Dateifallbacks sind definiert, die reale Durchführung bleibt aber für providergekoppelte Fälle ohne freigegebenen LLM-Pfad blockiert | P0 vor Live-Nutzer | PROMPT_TEST_BASELINE, PILOT_READINESS §3.3 |
| Externe Ressourcenliste über Deutschland hinaus erweitern | bei Produktisierung | SAFETY_PLAYBOOK §7 |

---

## Nächster Schritt

Zwei P0-Blocker bleiben vor Live-Nutzern offen: Erstens ist nach belastbarer
Prüfung von Azure OpenAI, Anthropic Claude API und Amazon Bedrock weiterhin
kein freigabefähiger externer LLM-Providerpfad identifiziert. Zweitens ist die
MVP-Evidence-Baseline jetzt zwar auf den freigegebenen Hetzner-/SQLite-
Pilotpfad gespiegelt, aber die dokumentierte reale Durchführung der
Pflichtfälle steht insgesamt noch aus; providergekoppelte Fälle bleiben
zusätzlich blockiert, solange kein freigegebener externer LLM-Pfad existiert.
Leak-/Redaction-, fail-closed- und Sidepath-Anforderungen sind damit operativ
klarer, aber noch nicht als `bestanden` nachgewiesen. Ohne diese zwei
Nachweise bleibt der Pilot gesperrt.
