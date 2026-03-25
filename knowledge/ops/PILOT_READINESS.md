# PILOT_READINESS

Status: aktiv | Owner: Jannek Büngener | Zuletzt geprüft: 2026-03-25

Basis: CLAIMS_FRAMEWORK, SAFETY_PLAYBOOK, PRIVACY_BY_DESIGN, ARCHITECTURE_OVERVIEW,
UX_CORE_SEQUENCE, GUARDRAILS_CONTENT_POLICY, SYSTEM_INVARIANTS

---

## 1. Zweck und Geltungsbereich

Dieses Dokument beschreibt die Mindestbedingungen für den Start eines ersten, kleinen text-first Pilots mit Traumtänzer. Es ist eine operative Go/No-Go-Entscheidungsvorlage – kein Recruiting-Plan, kein Markttest-Deck, keine klinische Validierungslogik, kein Pricing-Dokument.

Es gilt vor dem ersten Nutzerkontakt. Bei Erfüllung aller Voraussetzungen darf ein kleiner, kontrollierter Pilot beginnen. Bei Verletzung auch nur einer No-Go-Bedingung: kein Start.

---

## 2. Pilot-Rahmen

| Dimension | Definition |
|---|---|
| **Größe** | Kleine, namentlich bekannte Pilotgruppe (keine offene Anmeldung, kein öffentlicher Rollout) |
| **Pfad** | Ausschließlich text-first MVP – kein Voice, kein 3D, kein erweiterter Feature-Scope |
| **Zweck** | Beobachtung und Risikoprüfung – kein Wirkungsbeweis, keine Outcome-Erhebung |
| **Positionierung** | Explizit als Pilot-Testphase eines KI-gestützten Reflexionsformats kommuniziert |
| **Nicht-Ziele** | Keine Therapie, keine Beratung, keine Krisenintervention, kein Companionship |

---

## 3. Verbindliche Voraussetzungen vor Pilotstart

### 3.1 Claims-Klarheit

| Was mindestens stehen muss | Was noch nicht perfekt sein muss | No-Go |
|---|---|---|
| CLAIMS_FRAMEWORK als Canon vorhanden und aktiv | Fertige Website-Texte, vollständige AGB | Keine dokumentierte Nicht-Therapie-Positionierung |
| Nicht-Therapie-Positionierung schriftlich fixiert | Rechtlich vollständig geprüfte Formulierungen | Pilot-Kommunikation impliziert Therapie, Diagnose oder Krisenhilfe |
| Verbotene Formulierungen aus CLAIMS §3–§4 bekannt und ausgeschlossen | Vollständiger Kommunikationsplan | Heilversprechen, Wirksamkeitsbehauptungen oder Diagnose-Äquivalente in Pilot-Texten |

### 3.2 Safety-Basics

| Was mindestens stehen muss | Was noch nicht perfekt sein muss | No-Go |
|---|---|---|
| Exit jederzeit, sofort, ohne Friction möglich | Vollständige Red-Team-Test-Dokumentation | Kein funktionierender Exit-Mechanismus |
| Safeword operativ vorhanden und im Onboarding erklärt | Abgedeckte Randszenarien aller Safeword-Varianten | Kein Safeword oder Safeword ohne Wirkung |
| Trigger-Handling für Krisensprache definiert: Session stoppen, externer Verweis | Automatisierte Erkennung aller Trigger-Muster | Krisensprache wird nicht erkannt oder führt zu Weitervertiefung |
| Externe Ressourcen (Notruf 112, TelefonSeelsorge 0800 111 0 111) in System-Reaktion eingebaut | Mehrsprachige Ressourcenliste | Kein externer Verweis bei Krisen-Signal |
| Keine Session-Fortführung nach Safeword oder Abbruch | Vollständige Abbruch-Testfälle | Reframing oder Inhalte nach Abbruch |

### 3.3 Guardrails / Content Policy

| Was mindestens stehen muss | Was noch nicht perfekt sein muss | No-Go |
|---|---|---|
| GUARDRAILS_CONTENT_POLICY als Artefakt vorhanden | Vollständige Keyword-/Regex-Implementierung aller Muster | Guardrails nur im Prompt, kein Regelwerk oder Artefakt |
| Input-Guards für Safeword und Krisensprache operativ | Abdeckung jeder denkbaren Formulierungsvariante | Safeword oder Krisensprache werden nicht erkannt |
| Output-Guards-Kriterien definiert und angewandt | Automatisierte Prüfung jedes Outputs | Diagnose-, Therapie- oder Companion-Outputs werden nicht geblockt |
| fail-closed-Verhalten bei unklarem Guard-Signal definiert | Vollständige Guard-Testabdeckung | Kein definiertes Verhalten bei Guard-Unsicherheit |

### 3.4 Privacy- und Retention-Grundlagen

| Was mindestens stehen muss | Was noch nicht perfekt sein muss | No-Go |
|---|---|---|
| Session-Inhalte ephemer (kein Default-Speichern) | Technische Lösch-Automatisierung vollständig implementiert | Session-Inhalte werden als Default persistiert |
| Safety-/Guard-Event-Logs enthalten nur Typ + Zeitstempel, keinen Content | Vollständig geprüfte Provider-DPAs | Content-Logging als Default |
| Löschpfad konzeptuell definiert | Vollständige DPIA | Kein definierter Löschpfad |
| Pilot-Teilnehmer wissen, dass das System KI-gestützt ist und welche Daten verarbeitet werden | Vollständige Datenschutzerklärung in Endform | Keine Information der Teilnehmer über Datenverarbeitung |
| Kein Produktionseinsatz mit externen Providern ohne geprüfte DPA | Vollständige Subprozessor-Liste | Personenbezogene Daten werden an Provider ohne DPA übertragen |

### 3.5 Kernel- und Safe-State-Disziplin

| Was mindestens stehen muss | Was noch nicht perfekt sein muss | No-Go |
|---|---|---|
| Safe States PAUSED, EXIT, EXTERNAL_REFERRAL, GUARD_BLOCK konzeptuell definiert | Vollständige technische Implementierung aller Übergänge | Kein definiertes Verhalten bei Safety-Ereignis |
| fail-closed als Verhaltensprinzip verankert: bei Unklarheit → EXIT | Automatisierte Zustandsmaschine | UI oder LLM treffen Safety-Entscheidungen ohne Kernel-Kontrolle |
| Kein automatischer Re-Entry nach EXIT ohne explizite Nutzeraktion | Vollständige Automatisierung | Session nach EXIT automatisch fortgeführt |

### 3.6 UX-Mindeststand

| Was mindestens stehen muss | Was noch nicht perfekt sein muss | No-Go |
|---|---|---|
| Entry-Phase vorhanden: KI-Transparenz, Systemgrenzen, Safeword-Einführung, Exit-Erklärung, explizites Opt-in | Vollständig ausgearbeitete Szenenpfade | Kein Onboarding, keine Systemgrenzen-Kommunikation, kein Safeword im Entry |
| Check-in-Phase vorhanden: Bereitschaftsprüfung ohne Scoring oder Diagnose-Sprache | Vollständige Belastungs-Abfang-Logik | Kein Check-in oder Check-in mit Diagnose-Nähe |
| Exit-Phase: jederzeit, sofort, ohne Friction, ohne Kommentar zur Unterbrechung | Vollständig getestete Abbruch-Edge-Cases | Exit erfordert Bestätigung, Erklärung oder mehrere Schritte |
| UX_CORE_SEQUENCE als Canon vorhanden und angewandt | Vollständig fertige UI | Keine Sequenz-Grundstruktur, kein Canon für UX-Verhalten |

### 3.7 KI-Transparenz und Erwartungsmanagement

| Was mindestens stehen muss | Was noch nicht perfekt sein muss | No-Go |
|---|---|---|
| KI-Charakter im Onboarding explizit benannt | Vollständige AI-Act-Disclosure-Prüfung | System gibt sich als menschlicher Ansprechpartner aus |
| Keine Imitation menschlicher Wärme in einem Maß, das KI-Natur verschleiert | Vollständige rechtliche Kennzeichnungsprüfung | Pilot-Teilnehmer wissen nicht, dass sie mit einem KI-System interagieren |
| Systemgrenzen klar kommuniziert: kein Therapeut, kein Krisenformat, kein Notfallangebot | Fertige Disclaimer-Texte in Endform | Systemgrenzen werden nicht aktiv kommuniziert |

---

## 4. No-Go-Bedingungen

Wenn auch nur eine dieser Bedingungen zutrifft: **kein Pilotstart**.

| # | No-Go-Bedingung |
|---|---|
| 1 | Keine dokumentierte, schriftliche Nicht-Therapie-/Nicht-Diagnose-Positionierung |
| 2 | Kein funktionierender Exit-Mechanismus (sofort, ohne Friction) |
| 3 | Kein Safeword oder Safeword ohne definierte Wirkung |
| 4 | Keine Reaktion auf Krisensprache (kein Stopp, kein externer Verweis) |
| 5 | Guardrails nur implizit im Prompt, kein Regelwerk oder Artefakt |
| 6 | Session-Inhalte werden als Default persistiert |
| 7 | Content-Logging als Default (Nutzertexte, Trauminhalte in Logs) |
| 8 | Kein definierter Löschpfad für persistierte Daten |
| 9 | Personenbezogene Daten werden an externe Provider ohne geprüfte DPA übertragen |
| 10 | Kein Onboarding mit KI-Transparenz, Systemgrenzen und Safeword-Einführung |
| 11 | Exit erfordert Bestätigung, Begründung oder mehrere Schritte |
| 12 | Pilot-Kommunikation impliziert Therapie, Diagnose, Krisenhilfe oder Companionship |
| 13 | Kein definiertes Verhalten bei Safety-Ereignis (kein Safe State, kein fail-closed) |
| 14 | Pilot-Teilnehmer wissen nicht, dass sie mit einem KI-System interagieren |

---

## 5. Beobachtungspunkte im Pilot

Wenige, operative Beobachtungspunkte – keine Outcome-Metrik-Wolke.

| Beobachtungspunkt | Was beobachtet wird |
|---|---|
| **Abbrüche / vorzeitige Exits** | Wie häufig und an welchen Stellen verlassen Nutzer die Session vor dem regulären Ende |
| **Safeword-Auslösungen** | Ob und wie oft das Safeword genutzt wird |
| **Safety-Events** | Ob Krisensprache, Dissoziation oder Überforderungssignale auftreten (Typ + Zeitstempel, kein Content) |
| **Guard-Blocks** | Ob und wie oft Output-Guards anschlagen |
| **Overreach / Deutungsnähe** | Ob das System in Outputs zu nah an Wahrheitsbehauptungen oder Diagnose-Nähe kommt |
| **UX-Missverständnisse** | Ob Nutzer die Systemgrenzen missverstehen oder falsche Erwartungen zeigen |
| **Fehlpositionierung** | Ob Nutzer das System als Therapie, Krisenhilfe oder Beziehungssurrogat lesen |

**Wie beobachtet:** ausschließlich über Guard-/Safety-Event-Logs (Typ + Zeitstempel, kein Content) und qualitative Rückmeldungen. Keine Inhaltsanalyse von Session-Texten.

---

## 6. Stop-Kriterien für laufenden Pilot

Wenn eines dieser Kriterien eintritt: Pilot sofort pausieren oder stoppen.

| # | Stop-Kriterium |
|---|---|
| 1 | Wiederkehrende Safety-Events ohne Guard-Block (System eskaliert, anstatt zu begrenzen) |
| 2 | Guard-Fehlleistung: verbotene Outputs (Diagnose, Companion, Heilversprechen) erreichen den Nutzer |
| 3 | Content-Logging-Verstoß: Nutzertexte oder Auslösetexte landen in Logs |
| 4 | Nutzer lesen das System wiederholt als Therapie, Krisenhilfe oder Companion |
| 5 | Instabiles Exit- oder Safeword-Verhalten: Exit nicht sofort, Safeword ohne Wirkung |
| 6 | Kein klares fail-closed bei Systemfehler oder Guard-Unsicherheit |
| 7 | Privacy-Verletzung: Session-Inhalte persistiert ohne dokumentierten Zweck |
| 8 | Pilot-Kommunikation erzeugt systematisch falsche Produktwahrnehmung |

---

## 7. Minimale Incident- und Eskalationslogik

**Für das Solo-Maintainer-Setup – keine Team-Fiktion.**

### Bei Safety-Event im Pilot

1. Session für betroffenen Nutzer sofort stoppen (manuell falls nötig).
2. Externer Verweis sicherstellen (Notruf 112, TelefonSeelsorge).
3. Ereignistyp und Zeitstempel dokumentieren – kein Inhalt, kein Content-Logging.
4. Prüfen: war dies ein Einzelfall oder ein Muster?
5. Bei Muster: Pilot pausieren, Root Cause analysieren, Canon-Lücke schließen, dann ggf. fortführen.

### Bei Guard-Fehlleistung (verbotener Output erreicht Nutzer)

1. Pilot sofort pausieren.
2. Betroffenen Output-Typ identifizieren (welches verbotene Muster aus GUARDRAILS §8).
3. Guard-Kriterien und Prompt-Kontext prüfen.
4. Fehler beheben, Guard-Check dokumentieren.
5. Erst nach Behebung und Prüfung: Pilot fortführen.

### Bei Privacy-Verstoß

1. Pilot sofort stoppen.
2. Verstoß dokumentieren (was persistiert wurde, in welchem Log).
3. Daten löschen, Löschung bestätigen.
4. Root Cause schließen.
5. Kein Pilot-Neustart ohne vollständige Behebung.

### Dokumentation

Minimal: Datum, Ereignistyp, betroffener Bereich, Maßnahme, Status. Kein Content, keine Nutzertexte. Format: Eintrag in `knowledge/logs/sessions/` oder vergleichbarer Stelle.

---

## 8. Pilot-Go/No-Go-Check

**Alle Fragen müssen mit Ja beantwortet werden – sonst: kein Start.**

| # | Frage | Go-Bedingung |
|---|---|---|
| 1 | Ist die Nicht-Therapie-/Nicht-Diagnose-Positionierung schriftlich fixiert? | Ja |
| 2 | Funktioniert Exit sofort, ohne Friction, ohne Begründung? | Ja |
| 3 | Ist Safeword operational und im Onboarding erklärt? | Ja |
| 4 | Führt Krisensprache zu Stopp + externem Verweis, nicht zu Weitervertiefung? | Ja |
| 5 | Liegt GUARDRAILS_CONTENT_POLICY als Artefakt vor (nicht nur im Prompt)? | Ja |
| 6 | Sind Session-Inhalte ephemer – kein Default-Speichern? | Ja |
| 7 | Enthalten Logs keinen Nutzerinhalt oder Auslösetext? | Ja |
| 8 | Sind externe Provider (KI-API, Hosting) mit geprüfter DPA eingebunden – oder noch gar keine personenbezogenen Daten übergeben? | Ja |
| 9 | Enthält das Onboarding KI-Transparenz, Systemgrenzen und Safeword-Einführung? | Ja |
| 10 | Ist das Verhalten bei Safety-Ereignis definiert (Safe State, fail-closed)? | Ja |
| 11 | Kommuniziert der Pilot-Rahmen kein Therapie-, Diagnose- oder Companion-Versprechen? | Ja |
| 12 | Kann bei Safety-Event oder Guard-Fehlleistung sofort pausiert oder gestoppt werden? | Ja |

**Wenn eine Antwort Nein ist: kein Pilotstart. Lücke schließen, Check wiederholen.**
