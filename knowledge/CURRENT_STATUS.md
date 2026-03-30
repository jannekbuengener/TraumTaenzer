# CURRENT_STATUS – Traumtänzer

Zuletzt aktualisiert: 2026-03-30

---

## Aktueller Stand

**Branch:** `main`
**PRs:** PR-Stack #63, #64 und #65 gemergt; #62 geschlossen/superseded –
Bootstrap-Runtime-Pfad und Canon-Sync auf `main`
**Phase:** Core-Canon, Providerprüfung (fünf externe LLM-Pfade bewertet:
Azure OpenAI, Anthropic Claude API, Amazon Bedrock, OpenAI API, IONOS AI
Model Hub – keiner freigabefähig), Pilot-Infrastrukturpfad und die auf die
konkrete Zielumgebung gespiegelt definierte MVP-Evidence-Baseline stehen; die
dokumentierte reale Durchführung der Pflichtfälle steht insgesamt aus –
auf dem Hetzner-Pilotpfad bleiben nicht-providergekoppelte Fälle mangels
kanonisch gebundenem Zielpfad und erstem evidenzfähigen Runbook-Rezept
`Vorbedingung fehlt`, providergekoppelte Fälle durch das offene
Provider-Gate `blockiert`; ein lokaler Bootstrap-Runtime-Pfad auf `main`
ist vorhanden, aber noch nicht an einen echten Hetzner-Zielpfad gebunden;
degraded mode ist kein Pilot-Scope, sondern nur Safe-/Fehlerbetrieb; ein
Non-LLM-Ersatzpilot ist im aktuellen MVP-Scope nicht entschieden

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

### Harness / Bootstrap (PRs #63–#65)
- `harness/runtime_server.py`, `harness/runtime_tools.py`, `harness/inspect_events.py`, `harness/event_store.py` – minimaler Bootstrap-Runtime-Pfad mit `/health`, expliziten absoluten Pfaden, fail-closed ohne Adapter und lokalen DB-/Log-/Sidepath-Inspektionen
- `harness/README.md` – operatorische Ausführung und Grenzen des lokalen Bootstrap-/Harness-Pfads

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
| Die minimale Red-Team-/Prompt-Testbaseline ist auf den freigegebenen Pilotpfad gespiegelt; dokumentierte Pflichtnachweise sind definiert; providergekoppelte Fälle sind `blockiert` (kein freigegebener LLM-Pfad); auf dem Hetzner-Pilotpfad verbleiben nicht-providergekoppelte Fälle auf `Vorbedingung fehlt`; im lokalen Harness sind bestimmte Fälle (Gruppen A/B) prüfbar (→ PROMPT_TEST_BASELINE §3.2); degraded mode ist kein Ersatzpilot | P0 vor Live-Nutzer | PROMPT_TEST_BASELINE §3.1–§3.2, PILOT_READINESS §3.3 |
| Lokaler Bootstrap-Runtime-Pfad (`harness/runtime_server.py`, `harness/runtime_tools.py`) auf `main` vorhanden: Start / Stop / Health / kurzer Session-Smoke / DB-/Log-/Sidepath-Inspect lokal mit expliziten absoluten Pfaden und explizitem `workdir`-Scanroot möglich; offene Lücke ist jetzt `Hetzner Bootstrap Path Contract + First Evidence Recipe`, nicht weiterer Runtime-Neubau; lokale Harness-Artefakte bleiben kein Pilot-Nachweis | P0 vor Evidence-Ausführung (Hetzner-Pfad) | PROMPT_TEST_BASELINE §3.2, OPERATIONS_RUNBOOK §2.1, §3–§9 |
| Externe Ressourcenliste über Deutschland hinaus erweitern | bei Produktisierung | SAFETY_PLAYBOOK §7 |

---

## Nächster Schritt

Zwei P0-Blocker bleiben vor Live-Nutzern offen: Erstens ist nach belastbarer
Prüfung von fünf externen LLM-Pfaden (Azure OpenAI, Anthropic Claude API,
Amazon Bedrock, OpenAI API, IONOS AI Model Hub) weiterhin kein
freigabefähiger externer LLM-Providerpfad identifiziert; degraded mode ist
kein Ersatzpilot, sondern nur Safe-/Fehlerbetrieb; ein Non-LLM-Ersatzpilot
ist im aktuellen MVP-Scope nicht entschieden. Zweitens stehen die
Pflichtfälle der MVP-Evidence-Baseline auf dem Hetzner-Pilotpfad nicht als
`bestanden` fest: providergekoppelte Fälle sind durch das offene
Provider-Gate `blockiert`; nicht-providergekoppelte Fälle auf dem
Hetzner-Pfad haben Status `Vorbedingung fehlt`. Das lokale Harness
(`harness/`) macht bestimmte nicht-provider-gekoppelte Fälle (Gruppe A/B,
→ PROMPT_TEST_BASELINE §3.2) lokal prüfbar. Der nächste echte P0-Block ist
jetzt `Hetzner Bootstrap Path Contract + First Evidence Recipe`: der
vorhandene Bootstrap-Runtime-Pfad (`harness/runtime_server.py` +
`harness/runtime_tools.py`) muss an genau einen echten Hetzner-Zielpfad
gebunden werden, inklusive `app_root`, `workdir`, `volume_mount`, `db_path`,
`log_path`, `pid_file`, `bind_host` und `bind_port`, und genau in der
Sequenz `start -> health -> kurzer Session-Smoke -> inspect-db ->
inspect-log -> inspect-sidepaths -> stop` gefahren werden. Repo-seitig ist
der `workdir`-Contract jetzt durch den Bootstrap-Startpfad explizit
vorbereitet; offen bleiben die echten Hetzner-Zielwerte und der erste
Artefaktlauf. Bis die vier Artefaktklassen aus `OPERATIONS_RUNBOOK §4` für
diesen Lauf vorliegen, bleibt der Pilot gesperrt.
