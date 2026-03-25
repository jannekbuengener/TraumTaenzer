# Contributing – Traumtänzer

## Wer beiträgt

Dieses Repository wird solo geführt (Owner: Jannek Büngener). KI-Agenten (Claude, Codex, Gemini) leisten Zuarbeit: Diffs, Evidence, Kommentare. Finale Entscheidungen trifft der Owner.

Es gibt keine Review-Teams, keine Komitees, keine geteilte Autorisierung.

---

## Änderungen an Canon-Dokumenten

Canon-Dokumente dürfen nur via Pull Request auf `main` geändert werden – niemals direkt.

Canon-Dokumente sind alle Dateien unter:
- `knowledge/governance/`
- `knowledge/project/CLAIMS_FRAMEWORK.md`, `SAFETY_PLAYBOOK.md`, `PRIVACY_BY_DESIGN.md`
- `knowledge/architecture/ARCHITECTURE_OVERVIEW.md`
- `knowledge/project/PROJECT_META.md`
- `knowledge/SYSTEM_INVARIANTS.md`
- `knowledge/KNOWLEDGE_HUB.md`

---

## Scope und Commits

- Scope pro PR so klein wie möglich halten.
- Ein sachliches Thema pro Commit.
- Kein `git add .` – nur relevante Dateien stagen.
- Commit-Message: knapp, direkt, ohne Floskel.

---

## Evidence in PR-Beschreibungen

Jeder PR zu Canon-Änderungen braucht im Body:

- was geändert wurde und warum
- was geprüft wurde
- was offen bleibt

Keine Merge-Freigabe auf Basis von „fühlt sich okay an".

---

## Erhöhter Prüfbedarf

Folgende Änderungen brauchen explizite Begründung mit Evidence:

- Abschwächung eines Safety- oder Privacy-Prinzips
- Neue Produktbehauptung oder Positionierung
- Neue externe Provider-Einbindung
- Änderung der Canon-Hierarchie

---

## Definition of Done

- CI-Checks grün (CodeQL, Gitleaks, Dependency Review)
- PR-Body vollständig (Scope, Checks, offene Punkte)
- Kein unaufgelöster Canon-Konflikt
- Relevante Dokumente konsistent aktualisiert

---

## Was nicht erwünscht ist

- Erfundene Prüfergebnisse oder Compliance-Bestätigungen
- Änderungen, die Safety- oder Privacy-Grenzen abschwächen
- Vorschläge, die Teamrollen oder Prozesse voraussetzen, die real nicht existieren
- Scope-Ausweitung ohne Absprache
