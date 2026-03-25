# CONSTITUTION – Traumtänzer

Status: aktiv | Owner: Jannek Büngener | Zuletzt geprüft: 2026-03-25

---

## 1. Zweck

Dieses Dokument ist der oberste, nicht verhandelbare Regelrahmen für Traumtänzer.
Alle anderen Dokumente – Governance, Agent Policy, Domain Canons, operative Defaults – sind diesem Rahmen untergeordnet.

---

## 2. Projektkern (unveränderlich)

Traumtänzer ist ein privater, digitaler Erfahrungsraum zur Selbstreflexion durch Erlebnis.

**Was Traumtänzer nicht ist und nie wird:**

- kein Therapieangebot, keine Diagnostik, keine medizinische Zweckbestimmung
- keine Krisenintervention, kein Notfallangebot
- kein manipulativer Companion oder Bindungssystem
- kein Instrument zur autoritativen Traumdeutung
- kein datenhungriges Tracking-System

---

## 3. Nicht verhandelbare Prioritäten

**P0 – Safety vor Experience.**
Exit, Safeword und Safe-State-Verhalten sind das erste, nicht das letzte. Kein Feature, kein UX-Ziel, keine Performance-Überlegung überschreibt diese Ordnung.

**P0 – Privacy vor Bequemlichkeit.**
Session-Inhalte sind ephemer. Privacy-by-Default ist strukturell erzwungen, nicht konfigurierbar deaktivierbar. Keine Persistenz ohne dokumentierten Zweck und definierten Löschpfad.

**P0 – Fail-closed, nicht fail-open.**
Bei Unsicherheit, fehlendem Signal oder Guard-Verstoß fällt das System in einen definierten sicheren Zustand. Kein Improvisieren, kein „weiter wie bisher" als Fallback.

**P0 – Evidence vor Behauptung.**
Claims, Safety-Entscheidungen und Architekturaussagen brauchen Belege. „Fühlt sich okay an" ist kein Go.

---

## 4. Domain-Canons (bindend)

| Domain Canon | Kern-Aussage |
|---|---|
| CLAIMS_FRAMEWORK | keine Therapie-, Diagnose- oder Heilbehauptung; keine Companion-Rhetorik |
| SAFETY_PLAYBOOK | Exit-First, Safeword, Fail-closed, Trigger-Handling, kein Kriseninterventionsanspruch |
| PRIVACY_BY_DESIGN | Session-Content ephemer, Redaction-first, kein Logging von Nutzerinhalten, kein DPA-loser Provider-Einsatz |
| ARCHITECTURE_OVERVIEW | Kernel als Single Source of Control, Guards deterministisch, LLM ist Adapter kein Orchestrator, Provider-Agnostik |

Diese Canons sind untereinander konsistent und stützen sich gegenseitig. Ein Widerspruch zwischen Domain Canons ist ein Canon-Fehler und muss via PR aufgelöst werden – nicht durch Ignore oder operativen Workaround.

---

## 5. Nicht-Ziele (permanent)

- keine Therapie, Diagnose, Krisenhilfe, Heilversprechen
- kein manipulatives Companion-Design, keine Abhängigkeitsmechaniken
- keine Provider-Hartkopplung im Kernel
- keine autonomen Agenten-Entscheidungen ohne User-Go
- kein Governance-Theater ohne reale Rollen
- keine Komplexität um ihrer selbst willen

---

## 6. Änderungsschwelle

Diese Constitution darf nur via PR auf `main` geändert werden.

Änderungen an §§ 2–4 (Projektkern, Prioritäten, Domain-Canons) erfordern:

1. klare Begründung mit Evidence
2. explizites Go des Owners (Jannek Büngener)
3. keine Abschwächung von Safety oder Privacy ohne gleichwertige, dokumentierte Gegenmaßnahme

Sprachliche Korrekturen und Klarstellungen, die den Sinn nicht verändern, können im PR ohne weiteren Prüfprozess gemergt werden.

---

## 7. Canon-Hierarchie

```
CONSTITUTION
  → GOVERNANCE
      → AGENT_POLICY
          → Domain Canons (Claims / Safety / Privacy / Architecture)
              → Operative Defaults
```

Wenn Konflikt: höheres Level gewinnt. Konflikte werden explizit benannt, nicht verdeckt.
