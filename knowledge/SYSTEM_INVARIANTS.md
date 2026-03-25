# SYSTEM_INVARIANTS – Traumtänzer

Status: aktiv | Owner: Jannek Büngener | Zuletzt geprüft: 2026-03-25

Invarianten gelten immer. Sie sind nicht verhandelbar und werden nicht durch Operative Defaults oder Session-Absprachen außer Kraft gesetzt. Bei Konflikt mit einer Invariante gilt: Canon prüfen, nicht Invariante ignorieren.

---

## Governance-Invarianten

**G-1: Canon-Änderungen nur via PR.**
Kein Commit direkt auf `main`. Keine Ausnahme, auch nicht für den Owner.

**G-2: Evidence vor Behauptung.**
Jede Canon-Änderung, jede neue Claim, jede Architekturentscheidung braucht eine belegbare Grundlage. „Fühlt sich okay an" ist kein Go.

**G-3: Kein Agenten-Entscheid ohne User-Go.**
KI-Agenten liefern Zuarbeit. Finale Entscheidungen trifft der Owner. Keine irreversible Aktion ohne explizites Go.

---

## Safety-Invarianten

**S-1: Safety vor Experience.**
Kein Feature, kein UX-Ziel, keine Performanceüberlegung überschreibt Safety-Prinzipien. Exit, Safeword und Safe-State-Verhalten kommen zuerst.

**S-2: Fail-closed.**
Bei Unsicherheit, fehlendem Signal oder Guard-Verstoß: sicherer Zustand, kein Improvisieren, kein „weiter wie bisher".

**S-3: Keine Therapie- / Diagnose- / Krisenintervention-Positionierung.**
Absolut. Keine Ausnahme, keine Formulierungsvariante, kein Kontext, der dies rechtfertigt.

**S-4: Keine Companion-Bindungsmechanik.**
Kein System-Design, das emotionale Abhängigkeit oder dauerhaften Bindungserwartungen erzeugt.

---

## Privacy-Invarianten

**P-1: Session-Content ist ephemer.**
Nutzerinhalte werden nicht als Default persistiert. Kein Persistieren ohne dokumentierten Zweck und definierten Löschpfad.

**P-2: Redaction-first.**
Bevor etwas gespeichert wird: kann stattdessen ein Aggregat, ein Flag oder gar nichts gespeichert werden?

**P-3: Kein Content-Logging.**
Technische Logs enthalten keine Nutzertexte, keine Session-Inhalte, keine Auslösetexte zu Safety-Events.

**P-4: Kein Provider-Einsatz ohne geprüften DPA.**
Keine Produktionsnutzung personenbezogener Daten mit externen Diensten, solange Datenverarbeitungsvertrag nicht geprüft und dokumentiert ist.

---

## Architektur-Invarianten

**A-1: Kernel ist Single Source of Control.**
Weder UI noch LLM treffen Safety-Entscheidungen. Alle sicherheitsrelevanten Entscheidungen laufen durch den Kernel.

**A-2: Guards sind deterministisch.**
Guard Layer prüft regelbasiert – keine Safety-Entscheidungen per Inference oder Modell-Aufruf.

**A-3: LLM ist Adapter, kein Orchestrator.**
Das Sprachmodell generiert Text auf Basis zugeführten Kontexts. Es steuert keine Session-Logik, keine Safety-Entscheidungen, keine Persistenz.

**A-4: Provider-Agnostik.**
Keine Hartkopplung an einen LLM-, Storage- oder Infrastruktur-Provider in Kernel- oder Guard-Logik.

---

## Claims-Invarianten

**C-1: Keine Heilwirkung, Wirksamkeitsbehauptung oder klinische Aussage.**
Nicht in Website-, PR-, UX-, In-App- oder sonstigem Kontext. Keine Formulierungsvariante umgeht diese Grenze.

**C-2: KI-Charakter transparent.**
Das System ist KI-gestützt. Dieser Charakter wird kommuniziert – keine Imitation menschlicher Vertrauensbeziehungen.
