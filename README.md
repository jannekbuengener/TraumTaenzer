# Traumtänzer – Governance & Knowledge Repository

Dieses Repository ist das Governance- und Wissens-Framework für **Traumtänzer** (Modus Mono): einen privaten, digitalen Erfahrungsraum zur Selbstreflexion durch Erlebnis.

---

## Was dieses Repo ist

Ein dokumentations- und governance-first Repository. Es enthält:

- den vollständigen **Canon** (Regeln, Grenzen, Prioritäten) für das Projekt
- **Governance-Dokumente** (CONSTITUTION, GOVERNANCE, AGENT_POLICY)
- **Domain-Canons** (Claims, Safety, Privacy, Architecture)
- **Projektwissen** (Status, Roadmap, Systemkontext, Invarianten)

Es gibt keinen Runtime-Code, kein Build-System, kein Deployment. Die CI-Pipeline setzt Hygiene-Gates (CodeQL, Gitleaks, Dependency Review), keine Produktchecks.

---

## Was dieses Repo nicht ist

- kein lauffähiges Produkt oder Prototyp
- kein Therapieangebot, keine medizinische Zweckbestimmung
- kein generisches Starter-Kit oder Template-Pack

---

## Einstieg

| Dokument | Zweck |
|---|---|
| [KNOWLEDGE_HUB](knowledge/KNOWLEDGE_HUB.md) | Zentraler Einstiegspunkt in alle Canon- und Wissens-Dokumente |
| [CONSTITUTION](knowledge/governance/CONSTITUTION.md) | Oberste, nicht verhandelbare Projektregeln |
| [PROJECT_META](knowledge/project/PROJECT_META.md) | Projektdefinition, Nicht-Ziele, Risiken, P0/P1/P2 |
| [CLAIMS_FRAMEWORK](knowledge/project/CLAIMS_FRAMEWORK.md) | Was Traumtänzer behaupten darf – und was nicht |
| [SAFETY_PLAYBOOK](knowledge/project/SAFETY_PLAYBOOK.md) | Exit-First, Safeword, Trigger-Handling |
| [PRIVACY_BY_DESIGN](knowledge/project/PRIVACY_BY_DESIGN.md) | Datensparsamkeit, Retention, Löschung |
| [ARCHITECTURE_OVERVIEW](knowledge/architecture/ARCHITECTURE_OVERVIEW.md) | MVP-Architektur-Canon |
| [CURRENT_STATUS](knowledge/CURRENT_STATUS.md) | Aktueller Projektstand |

---

## Beitragen

Siehe [CONTRIBUTING.md](CONTRIBUTING.md). Kurzfassung: PR-only für Canon-Änderungen, kleine Scopes, Evidence in der PR-Beschreibung.

---

## Projektkontext

- **Owner:** Jannek Büngener
- **Modell:** Solo-Maintainer + KI-Zuarbeit (Claude, Codex, Gemini)
- **Sprache:** primär Deutsch
- **Phase:** Governance und Canon vollständig; Produktarbeit (P1) steht noch aus

---

## Sicherheit

Sicherheitsrelevante Meldungen bitte nicht als öffentliches Issue. Siehe [SECURITY.md](SECURITY.md).
