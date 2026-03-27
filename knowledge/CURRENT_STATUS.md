# CURRENT_STATUS – Traumtänzer

Zuletzt aktualisiert: 2026-03-27

---

## Aktueller Stand

**Branch:** `main`
**PRs:** Docs-/Spec- und Sync-PRs bis #56 gemergt – Canon-Grundstock,
Provider- und Infrastrukturentscheide auf `main`
**Phase:** Core-Canon, Providerprüfung (fünf externe LLM-Pfade bewertet:
Azure OpenAI, Anthropic Claude API, Amazon Bedrock, OpenAI API, IONOS AI
Model Hub – keiner freigabefähig), Pilot-Infrastrukturpfad und die auf die
konkrete Zielumgebung gespiegelt definierte MVP-Evidence-Baseline stehen; die
dokumentierte reale Durchführung der Pflichtfälle steht insgesamt aus –
nicht-providergekoppelte Fälle mangels Runtime-/Deploy-/Runbook-Substanz
als `Vorbedingung fehlt`, providergekoppelte Fälle durch das offene
Provider-Gate `blockiert`; degraded mode ist kein Pilot-Scope, sondern
nur Safe-/Fehlerbetrieb

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
| Nach Bewertung von Azure OpenAI, Anthropic Claude API (`/v1/messages`), Amazon Bedrock (`InvokeModel` + `anthropic.claude-sonnet-4-6`), OpenAI API (`eu.api.openai.com`, `POST /v1/chat/completions`) und IONOS AI Model Hub (`POST /v1/chat/completions`) ist aktuell kein externer LLM-Pfad freigabefähig; produktnahe Subprocessor-, Löschpfad- und Side-Artifact-Blocker bleiben live-relevant | P0 vor Live-Nutzer | PROVIDER_DPA_INPUT_MATRIX §7–§8 |
| Die minimale Red-Team-/Prompt-Testbaseline ist auf den freigegebenen Pilotpfad gespiegelt; dokumentierte Pflichtnachweise sind definiert, aber die reale Durchführung steht insgesamt aus: providergekoppelte Fälle sind `blockiert` (kein freigegebener LLM-Pfad), nicht-providergekoppelte Fälle ohne Runtime-/Deploy-/Runbook-Artefakte haben Status `Vorbedingung fehlt`; degraded mode ist kein Ersatzpilot | P0 vor Live-Nutzer | PROMPT_TEST_BASELINE, PILOT_READINESS §3.3 |
| Lokales Harness (`harness/`) vorhanden: Kernel, Guards, Stub-Adapter, content-freier SQLite-Event-Store, Fault-Injection, Smoke-Check und Szenarien-Runner; damit nicht-provider-gekoppelte Testfälle lokal ausführbar; Hetzner-deploybare Runtime fehlt weiterhin; konkrete Hetzner-Vorbedingungen in OPERATIONS_RUNBOOK §3 | P0 vor Evidence-Ausführung (Hetzner-Pfad) | OPERATIONS_RUNBOOK §3–§7 |
| Externe Ressourcenliste über Deutschland hinaus erweitern | bei Produktisierung | SAFETY_PLAYBOOK §7 |

---

## Nächster Schritt

Zwei P0-Blocker bleiben vor Live-Nutzern offen: Erstens ist nach belastbarer
Prüfung von fünf externen LLM-Pfaden (Azure OpenAI, Anthropic Claude API,
Amazon Bedrock, OpenAI API, IONOS AI Model Hub) weiterhin kein
freigabefähiger externer LLM-Providerpfad identifiziert; degraded mode ist
kein Ersatzpilot, sondern nur Safe-/Fehlerbetrieb. Zweitens stehen die
Pflichtfälle der MVP-Evidence-Baseline operativ nicht als `bestanden` fest:
providergekoppelte Fälle sind durch das offene Provider-Gate `blockiert`;
nicht-providergekoppelte Fälle auf dem Hetzner-Pfad haben Status
`Vorbedingung fehlt`. Das lokale Harness (`harness/`) schließt den
letzteren Punkt für nicht-provider-gekoppelte Fälle in der lokalen
Ausführungsumgebung – Hetzner-deploybare Runtime fehlt weiterhin.
Bis der Provider-Blocker und die Hetzner-Runtime-Vorbedingungen geschlossen
sind, bleibt der Pilot gesperrt.
