# CURRENT_STATUS – Traumtänzer

Zuletzt aktualisiert: 2026-03-25

---

## Aktueller Stand

**Branch:** `main`
**PRs:** #16, #17, #18 gemergt – Canon-Grundstock, Foundation-Scope und CI-Gates vollständig integriert
**Phase:** Governance und Foundation abgeschlossen; P1-Scope aktiv (Guardrails, Pilot-Readiness)

---

## Was steht (auf main, gemergt)

### Governance-Canon
- `knowledge/governance/CONSTITUTION.md` – komplett, projektspezifisch
- `knowledge/governance/GOVERNANCE.md` – Solo-Maintainer-Modell, PR-Pflicht, Evidence-Schwellen
- `knowledge/governance/AGENT_POLICY.md` – Agenten-Regeln, verbotene Muster
- `knowledge/governance/GOVERNANCE_QUICKREF.md` – operative Kurzreferenz
- `knowledge/governance/POLICY_STACK_MINI.md` – Konflikthierarchie

### Domain-Canon (P0)
- `knowledge/project/CLAIMS_FRAMEWORK.md` – zulässige/unzulässige Claims, Red Flags
- `knowledge/project/SAFETY_PLAYBOOK.md` – Exit-First, Safeword, Trigger-Handling
- `knowledge/project/PRIVACY_BY_DESIGN.md` – Datensparsamkeit, Retention, Löschung
- `knowledge/architecture/ARCHITECTURE_OVERVIEW.md` – Kernel, Guards, Adapter-Grenzen, fail-closed

### Foundation
- `README.md` – projektspezifisch, kein generisches Repo-Pack mehr
- `CODEOWNERS` – korrekt gesetzt (@jannekbuengener)
- `CONTRIBUTING.md` – auf Solo-Maintainer + KI-Zuarbeit zugeschnitten
- `SECURITY.md` – realistischer Meldeweg, Scope klar
- `knowledge/CURRENT_STATUS.md` – dieses Dokument
- `knowledge/SYSTEM.CONTEXT.md` – reale Umgebungs- und Tool-Fakten
- `knowledge/SYSTEM_INVARIANTS.md` – harte, bindende Invarianten aus allen Domain-Canons

### Hub
- `knowledge/KNOWLEDGE_HUB.md` – Governance-Sektion ergänzt, Domain-Canon-Sektion retitelt

---

## Was noch offen ist

| Punkt | Priorität | Referenz |
|---|---|---|
| Guardrails / Content Policy aus Canon ableiten | P1 – aktiv (Issue #19) | SAFETY_PLAYBOOK, CLAIMS_FRAMEWORK |
| Pilot-Readiness für text-first MVP definieren | P1 – aktiv (Issue #21) | PROJECT_META |
| Provider-DPAs für externe KI-/Hosting-Dienste klären | P0 vor Produktionsstart | PRIVACY_BY_DESIGN §9 |
| Retention-Fristen gegen konkrete Infrastruktur validieren | P0 vor Produktionsstart | PRIVACY_BY_DESIGN §6 |
| Red-Team-/Prompt-Tests auf Basis Guardrails | nach Issue #19 | SAFETY_PLAYBOOK |
| AI Act Readiness Check | vor Produktionsstart | AGENT_POLICY |
| Externe Ressourcenliste über Deutschland hinaus erweitern | bei Produktisierung | SAFETY_PLAYBOOK §7 |

---

## Nächster Schritt

Guardrails/Content Policy (Issue #19) und Pilot-Readiness (Issue #21) bearbeiten. Beide Artefakte sind Voraussetzung vor erstem Nutzerkontakt.
