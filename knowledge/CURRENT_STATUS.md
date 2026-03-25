# CURRENT_STATUS – Traumtänzer

Zuletzt aktualisiert: 2026-03-25

---

## Aktueller Stand

**Branch:** `docs/modus-mono-pdf`
**PR:** #16 offen – enthält den vollständigen Canon-Grundstock und Foundation-Scope
**Phase:** Governance und Foundation abgeschlossen; Produktarbeit (P1) steht aus

---

## Was steht (auf Branch, ausstehend Merge)

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

## Was blockiert

- **PR #16 merge:** CI-Checks müssen grün sein, Owner-Review steht aus.
- **`knowledge/SYSTEM_INVARIANTS.md`** war bis heute leer – in diesem Run gefüllt.

---

## Was noch offen ist (nach Merge)

| Punkt | Priorität | Referenz |
|---|---|---|
| `SYSTEM_INVARIANTS.md` befüllen | erledigt in diesem Run | – |
| Provider-DPAs für externe KI-/Hosting-Dienste klären | P0 vor Produktionsstart | PRIVACY_BY_DESIGN §9 |
| Retention-Fristen gegen konkrete Infrastruktur validieren | P0 vor Produktionsstart | PRIVACY_BY_DESIGN §6 |
| Guardrails / Content Policy aus Safety Playbook ableiten | P1 | SAFETY_PLAYBOOK |
| UX-Prototyp „Sanfte Begegnung" (Entry → Szene → Exit) | P1 | PROJECT_META |
| `knowledge/ACTIVE_ROADMAP.md` aktualisieren | P1 | – |
| Externe Ressourcenliste über Deutschland hinaus erweitern | bei Produktisierung | SAFETY_PLAYBOOK §7 |

---

## Nächster Schritt

PR #16 mergen, sobald CI grün und Owner-Review abgeschlossen. Danach beginnt P1-Scope: Guardrails, UX-Prototyp, Roadmap.
