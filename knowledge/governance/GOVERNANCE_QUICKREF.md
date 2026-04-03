# GOVERNANCE QUICKREF – Traumtänzer

Einseitige operative Kurzreferenz. Kein Ersatz für die vollständigen Dokumente.

---

## Vor jeder Änderung prüfen

1. Ist die Datei Canon? → Nur via PR auf `main`, niemals direkt.
2. Berührt die Änderung Safety oder Privacy? → Evidence Pack Pflicht, kein Bauchgefühl.
3. Gibt es einen Canon-Konflikt? → Explizit benennen, nicht umschiffen.
4. Hat der Owner explizit Go gegeben? → Bei irreversiblen oder Canon-Änderungen: Pflicht.

---

## Rote Linien

- Direktänderung auf `main` → verboten
- Safety- oder Privacy-Abschwächung ohne Evidence → verboten
- Erfundene Reviews, Tests, Compliance-Bestätigungen → verboten
- Autonome Agenten-Entscheidungen ohne User-Go → verboten
- Merge „weil es sich okay anfühlt" → kein Go
- Claim ohne Deckung durch aktuellen Produktstand → verboten
- `git add .` → verboten

---

## Interner Testmodus (eng)

- interner Testmodus != Pilot
- interner Testmodus != Live
- interner Testmodus != Provider-Freigabe
- nur maintainer-only auf kontrolliertem Systempfad
- keine Spiegelung in Repo, Tickets, Logs, Screenshots oder Testfixtures
- lokale Rohablage nur eng begrenzt; max. 7 Tage, dann löschen
- pro Lauf nur minimale content-freie Traceability: Zweck, erwarteter Erkenntnisgewinn, kurzer Befund, Löschhinweis

---

## Sauberer Session-Abschluss

- [ ] Dateien committed und gepusht
- [ ] PR vorhanden oder explizit nicht nötig (begründet)
- [ ] Offene Punkte in KNOWLEDGE_HUB oder Issue dokumentiert
- [ ] Kein unaufgelöster Canon-Konflikt
- [ ] `git status -sb` zeigt sauberen Zustand

---

## Canon-Hierarchie

```
CONSTITUTION > GOVERNANCE > AGENT_POLICY > Domain Canons > Operative Defaults
```

Wenn Konflikt: höheres Level gewinnt. Konflikt immer explizit benennen.

---

## Domain Canons – Kern in einem Satz

| Canon | Kern |
|---|---|
| CLAIMS_FRAMEWORK | keine Therapie-, Diagnose- oder Heilbehauptung, keine Companion-Rhetorik |
| SAFETY_PLAYBOOK | Exit-First, Safeword, Fail-closed |
| PRIVACY_BY_DESIGN | Session-Content ephemer, Redaction-first, kein Content-Logging |
| ARCHITECTURE_OVERVIEW | Kernel = Single Source of Control, Guards deterministisch, LLM = Adapter |
