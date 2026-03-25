# POLICY_STACK_MINI – Traumtänzer

Konflikthierarchie. Praktisch, nicht theoretisch.

---

## Stack (bindend)

```
1. CONSTITUTION           – oberste, nicht verhandelbare Regeln
2. GOVERNANCE             – Entscheidungs- und Änderungslogik
3. AGENT_POLICY           – was Agenten dürfen und nicht dürfen
4. Domain Canons          – Claims / Safety / Privacy / Architecture
5. Operative Defaults     – session-spezifische, nicht-canonische Absprachen
```

---

## Konfliktauflösung

**Höheres Level gewinnt immer.**

| Konflikt | Gewinner |
|---|---|
| CONSTITUTION vs. GOVERNANCE | CONSTITUTION |
| GOVERNANCE vs. AGENT_POLICY | GOVERNANCE |
| AGENT_POLICY vs. Domain Canon | AGENT_POLICY (Prozess schlägt Inhalt) |
| Domain Canon vs. Domain Canon | Canon-Fehler – nicht umschiffen, via PR auflösen, Owner entscheidet |
| Domain Canon vs. Operative Default | Domain Canon |
| Recht vs. Canon | Recht geht vor – Canon via PR anpassen |

---

## Was Operative Defaults sind

Nicht-canonische, nicht persistente Absprachen: session-spezifische Formate, Zeitpläne, Zuarbeits-Vereinbarungen. Sie gelten nur im aktuellen Kontext, binden nicht zwischen Sessions und überschreiben keinen Canon.

---

## Was dieser Stack nicht regelt

- Priorität zwischen zwei gleichrangigen Domain Canons (z. B. Claims vs. Safety): in der Praxis ist Konsistenz Pflicht. Bei Konflikt: eskalieren, nicht auflösen.
- Externe rechtliche Pflichten: Recht geht vor allem. Wenn eine gesetzliche Pflicht einen Canon berührt, ist Canon anzupassen – via PR.

---

## Solo-Maintainer-Realität

Es gibt einen Owner. Agenten liefern Zuarbeit. Dieser Stack ist kein Rollenspiel – er beschreibt, wie Entscheidungen wirklich getroffen werden.
