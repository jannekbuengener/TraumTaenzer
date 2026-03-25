# KNOWLEDGE_HUB

Kurze, belegte Entscheidungen + Links (intern) zu Evidence/Logs.

## Governance-Canon

- [CONSTITUTION](governance/CONSTITUTION.md) – oberste, nicht verhandelbare Regeln; Prioritäten, Domain-Canon-Bindung, Änderungsschwelle
- [GOVERNANCE](governance/GOVERNANCE.md) – Solo-Maintainer-Entscheidungsmodell, PR-Pflicht, Evidence-Schwellen, Canon-Konfliktlogik
- [AGENT_POLICY](governance/AGENT_POLICY.md) – was KI-Agenten dürfen und nicht dürfen; Evidence-Pflicht, Eskalationsregeln
- [GOVERNANCE_QUICKREF](governance/GOVERNANCE_QUICKREF.md) – einseitige operative Kurzreferenz
- [POLICY_STACK_MINI](governance/POLICY_STACK_MINI.md) – Konflikthierarchie und Auflösungslogik

## Domain-Canon (P0-bindend)

- [CLAIMS_FRAMEWORK](project/CLAIMS_FRAMEWORK.md) – Zulässige/unzulässige Claims, Red Flags, Guidance
- [SAFETY_PLAYBOOK](project/SAFETY_PLAYBOOK.md) – Safety-Prinzipien, Exit/Safeword, Trigger-Handling, Eskalationspfade
- [PRIVACY_BY_DESIGN](project/PRIVACY_BY_DESIGN.md) – Datenminimierung, Datenklassen, Retention, Löschung, Export, Logging-Grenzen (P0-Canon)
- [ARCHITECTURE_OVERVIEW](architecture/ARCHITECTURE_OVERVIEW.md) – MVP-Architektur-Canon: Kernel, Guard Layer, Adapter-Grenzen, Event-Log, fail-closed
- [GUARDRAILS_CONTENT_POLICY](project/GUARDRAILS_CONTENT_POLICY.md) – Operative Guard-Kriterien: Input/Output-Guards, Session-Transitions, Safe-State-Mapping, Logging-Grenzen, Red-Flag-Liste
- [KERNEL_GUARD_CONTRACTS](architecture/KERNEL_GUARD_CONTRACTS.md) – Technische Implementierungsvorlage: Zustandsmodell, Event-Contracts, Guard-Decision-Klassen, Adapter-Grenzen, fail-closed-Pfade
- [TEXT_FIRST_RUNTIME_FLOW](architecture/TEXT_FIRST_RUNTIME_FLOW.md) – Laufzeitfluss text-first MVP: Happy Path, Payloads, Constraint-Flags, neutrale Antwortklassen, Safe-State-Pfade, Sequenzablauf

## UX-Canon (P1)

- [UX_CORE_SEQUENCE](project/UX_CORE_SEQUENCE.md) – Text-first Kernsequenz für sichere Erstbegegnung: Entry, Check-in, Szene/Reflexionskern, Exit; Tonalität, verbotene Muster, UX-Prüfcheck

## Ops-Artefakte

- [PILOT_READINESS](ops/PILOT_READINESS.md) – Go/No-Go-Entscheidungsvorlage für ersten text-first Pilot: Voraussetzungen, No-Go-Bedingungen, Beobachtungspunkte, Stop-Kriterien, Incident-Logik

## Weitere Schlüsseldokumente

- [PROJECT_META](project/PROJECT_META.md) – Projektdefinition, Nicht-Ziele, Risiken, P0/P1/P2
- [CURRENT_STATUS](CURRENT_STATUS.md) – Aktueller Projektstand, offene Punkte, nächste Schritte
- [SYSTEM_INVARIANTS](SYSTEM_INVARIANTS.md) – immer geltende Invarianten (Governance, Safety, Privacy, Architecture, Claims)
- [SYSTEM_CONTEXT](SYSTEM.CONTEXT.md) – Umgebung, Repo-Struktur, Toolchain, Constraints
- [ACTIVE_ROADMAP](ACTIVE_ROADMAP.md) – Now / Next / Later
