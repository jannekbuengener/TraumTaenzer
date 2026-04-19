# GOVERNANCE – Traumtänzer

Status: aktiv | Owner: Jannek Büngener | Zuletzt geprüft: 2026-04-03

---

## 1. Entscheidungsmodell

Traumtänzer wird solo geführt. Es gibt einen Owner: Jannek Büngener.

Es gibt keine Komitees, keine Review-Teams, keine geteilte Autorisierung. KI-Agenten (Claude, Codex, Gemini) liefern Zuarbeit, Evidence und Diffs – sie entscheiden nicht. Finale Entscheidungen trifft der Owner.

---

## 2. Was immer via PR geht

Jede Änderung an Canon-Dokumenten erfolgt ausschließlich über einen Pull Request auf `main`:

- `knowledge/governance/CONSTITUTION.md`
- `knowledge/governance/GOVERNANCE.md`
- `knowledge/governance/AGENT_POLICY.md`
- `knowledge/governance/GOVERNANCE_QUICKREF.md`
- `knowledge/governance/POLICY_STACK_MINI.md`
- `knowledge/project/CLAIMS_FRAMEWORK.md`
- `knowledge/project/SAFETY_PLAYBOOK.md`
- `knowledge/project/PRIVACY_BY_DESIGN.md`
- `knowledge/architecture/ARCHITECTURE_OVERVIEW.md`
- `knowledge/project/PROJECT_META.md`
- `knowledge/SYSTEM_INVARIANTS.md`
- `knowledge/KNOWLEDGE_HUB.md`

Direktänderungen auf `main` sind verboten – auch für den Owner.
CI-Checks (CodeQL, Gitleaks, Dependency Review) sind Merge-Gate, nicht Dekoration.

---

## 3. Was direkt auf Branch okay ist

Ohne erhöhten Prüfbedarf:

- neue Governance- oder Wissensdokumente, die noch kein Canon-Status haben (erstmalig angelegt)
- Ergänzungen zu Logs, Session-Protokollen, ADRs
- README-Korrekturen ohne Canon-Bezug
- Typo-Fixes in nicht-canonischen Dateien

In allen Fällen gilt: kleiner Scope, eine sachliche Änderung pro Commit, kein `git add .`.

---

## 4. Wann erhöhter Prüfbedarf besteht

Folgende Änderungen brauchen im PR-Body ein Evidence Pack:

- Abschwächung oder Einschränkung eines Safety- oder Privacy-Prinzips
- Neue Behauptung über Produktwirkung oder -positionierung
- Neue externe Provider-Einbindung (KI-API, Infrastruktur, E-Mail, Storage)
- Änderung der Canon-Hierarchie oder der CONSTITUTION
- Architekturentscheidung, die Guards umgeht, den Kernel aufteilt oder den LLM-Adapter zum Orchestrator macht

Evidence Pack bedeutet: was wurde geprüft, warum ist die Entscheidung sicher, was bleibt offen. Keine Pauschal-Freigabe ohne Belege.

---

## 5. Befristeter maintainer-only interner Testmodus

Ein provider-neutraler maintainer-only interner Testmodus ist nur als enge,
befristete Canon-Regel zulässig. Er gilt nur auf einem kontrollierten
Systempfad, nur für maintainer-only interne Läufe und erzeugt nur interne
System-Evidence. Er ist kein Pilot-Go, kein Live-Go und kein Provider-Go.

Einführung, Verlängerung und Aufhebung dieses Modus erfolgen ausschließlich via
PR auf `main` mit Evidence Pack und explizitem Befristungs- oder Review-Hinweis.
Informelle Session-Absprachen ersetzen diese Canon-Entscheidung nicht.

Jeder Lauf in diesem Modus braucht minimale, content-freie Traceability im
zugehörigen Issue oder PR:

- Zweck
- erwarteter Erkenntnisgewinn
- kurzer Befund
- Löschhinweis

---

## 6. Canon-Konflikte

Wenn zwei Canon-Dokumente widersprüchliche Regeln enthalten:

1. Konflikt explizit im PR benennen – nicht stillschweigend auflösen.
2. CONSTITUTION hat Vorrang vor allem anderen.
3. Höheres Level der Hierarchie gewinnt.
4. Wenn unklar: nicht mergen. Issue öffnen. Owner entscheidet.

Kein Merge „weil es sich okay anfühlt". Kein Merge, der einen Konflikt verdeckt.

---

## 7. Sauberer Session-Abschluss

Eine Arbeits-Session mit KI-Agenten gilt als abgeschlossen, wenn:

- relevante Dateien committed und gepusht sind
- PR vorhanden oder explizit als nicht nötig begründet
- offene Punkte in KNOWLEDGE_HUB oder Issue dokumentiert sind
- kein unaufgelöster Canon-Konflikt offen ist
- `git status -sb` einen sauberen Zustand zeigt

„Fachlich okay" allein reicht nicht. Operativer Abschluss heißt: git-Status sauber, Traceability vorhanden.

---

## 8. Branch-Strategie

- `main` – geschützt, PR-only, CI-Pflicht
- Feature-/Docs-Branches: `docs/`, `feat/`, `fix/` – kurzlebig, kleiner Scope
- Kein Long-Running-Branch ohne aktives Issue im Hintergrund

---

## 9. Was nicht erfunden wird

- keine Review-Gremien, die nicht existieren
- keine Approval-Chains ohne reale Personen dahinter
- keine Fake-Gates (kein „peer review", wenn nur ein Owner vorhanden ist)
- keine Rollen, die nur auf dem Papier stehen

Der Governance-Stack bildet die Realität ab – nicht ein Enterprise-Wunschbild.
