# PILOT_READINESS

Status: aktiv | Owner: Jannek Büngener | Zuletzt geprüft: 2026-04-03

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
| fail-closed-Verhalten bei Guard-Unsicherheit sowie Guard-, Adapter- und Provider-Output-Fehlerpfaden definiert | Vollständige Guard-Testabdeckung | Kein definiertes Verhalten bei Guard-Unsicherheit oder fehlerhaftem Provider-Output |
| `PROMPT_TEST_BASELINE.md` als minimale Evidence-Baseline vorhanden; vor Pilotstart sind alle P0-Fälle sowie Leak-/fail-closed-/sidepath-Fälle gegen den freigegebenen Pilotpfad (`Hetzner Cloud Server` `nbg1` + `Hetzner Volume` + lokales `SQLite`) dokumentiert `bestanden`, und kein providergekoppelter Pflichtfall steht auf `blockiert`; `blockiert` ist für providergekoppelte Fälle bei offenem externem LLM-Gate reserviert; nicht-providergekoppelte Fälle ohne ausführbare Runtime, definierte Start-/Stop-/Health-/Log-Inspektionspfade und reale Artefakte stehen auf `Vorbedingung fehlt` – dieser Status ist kein `bestanden`; ein benannter Hetzner-/SQLite-Pilotpfad allein reicht nicht für evidenzfähige reale Durchführung; maintainer-only interne Testläufe auf kontrolliertem Systempfad erzeugen nur interne System-Evidence und zählen nicht als `bestanden` oder Pilot-Nachweis für diesen Pfad | Vollständige Automatisierung, Fuzzing oder Langzeit-Drift-Tests | Keine minimale Red-Team-/Prompt-Testbaseline oder kein Nachweis für Krisen-, Boundary-, Companion-, Leak-, Sidepath- und fail-closed-Pfade gegen den freigegebenen Pilotpfad |

### 3.4 Privacy- und Retention-Grundlagen

| Was mindestens stehen muss | Was noch nicht perfekt sein muss | No-Go |
|---|---|---|
| Session-Inhalte ephemer (kein Default-Speichern) | Technische Lösch-Automatisierung vollständig implementiert | Session-Inhalte werden als Default persistiert |
| Safety-/Guard-Event-Logs enthalten nur Typ + Zeitstempel, keinen Content | Vollständig geprüfte Provider-DPAs | Content-Logging als Default |
| Runtime-Events tragen nur opaque/pseudonyme `session_id`; keine direkte Nutzeridentität und keine stille Session↔Access-Korrelation | Vollständige Auth-/IAM-Architektur | Event-Log, Debug- oder Ops-Pfad verknüpft Runtime-Ereignisse mit Account-/Access-Daten ohne dokumentierten Minimalzweck |
| Löschpfad konzeptuell definiert | Vollständige DPIA | Kein definierter Löschpfad |
| Zielkomponente für Event-Storage/Logs ist konkret benannt; 90-/30-Tage-Retention, automatische Löschung und Backup-/Nebenlogik dieses Pfads sind technisch belastbar beschrieben | Vollständige Audit-/Observability-Infrastruktur | Offener Event-Storage-/Hosting-Pfad oder nur behauptetes Retention-Enforcement |
| Pilot-Teilnehmer wissen, dass das System KI-gestützt ist und welche Daten verarbeitet werden | Vollständige Datenschutzerklärung in Endform | Keine Information der Teilnehmer über Datenverarbeitung |
| Kein Live-Nutzer mit externen Providern ohne ausgefüllte und positiv bewertete `PROVIDER_DPA_INPUT_MATRIX.md`; maintainer-only interne Testläufe oder interne System-Evidence ersetzen weder positive Matrix noch Provider-Freigabe | Vollständige juristische Endprüfung aller Verträge | Personenbezogene Daten fließen an einen Provider mit offener Matrix oder negativem Entscheidungsstatus |
| Retention, Training/Service-Verbesserung, Region/Transfer und Subprocessor-Lage des konkreten Produktpfads sind geklärt | Vollständige Vertragsarchivierung im Endzustand | Ungeklärte Retention-, Training-, Region- oder Subprocessor-Lage |

**Aktueller Pilotpfad (Entscheid 2026-03-26):**

- Hosting: `Hetzner Cloud Server` in `nbg1`
- Event-Storage: lokales `SQLite` auf angehängtem `Hetzner Volume`
- Nicht freigegeben: append-only Dateipfad als Pilot-Event-Store, weil
  TTL- und fallbezogene Löschung dort nur über Rewrite-/Rotationspfade
  erreichbar wären
- Zusatzbedingungen: keine Server-Backups, keine Snapshots, keine externen
  Log-/Storage-Replikate; täglicher TTL-Purge + `VACUUM`; Host-Logs bleiben
  content-free und max. 30 Tage

**Explizite Abgrenzung zum internen Testmodus:**
Maintainer-only interne Testläufe nach `GOVERNANCE.md §5` und
`PRIVACY_BY_DESIGN.md §2` sind kein Pilotpfad. Auch mit realem Eigenmaterial
erzeugen sie nur interne System-Evidence; sie zählen weder als
Pilot-Nachweis noch als Provider-Freigabe-Evidence und ändern keine negative
Matrixbewertung.

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
| 9 | Personenbezogene Daten werden an externe Provider ohne positiv bewertete `PROVIDER_DPA_INPUT_MATRIX.md` übertragen |
| 10 | Kein Onboarding mit KI-Transparenz, Systemgrenzen und Safeword-Einführung |
| 11 | Exit erfordert Bestätigung, Begründung oder mehrere Schritte |
| 12 | Pilot-Kommunikation impliziert Therapie, Diagnose, Krisenhilfe oder Companionship |
| 13 | Kein definiertes Verhalten bei Safety-Ereignis (kein Safe State, kein fail-closed) |
| 14 | Pilot-Teilnehmer wissen nicht, dass sie mit einem KI-System interagieren |
| 15 | Keine minimale Red-Team-/Prompt-Testbaseline oder kein Nachweis für Safeword-, Krisen-, Boundary-, Companion-, Leak-, Sidepath- und fail-closed-Pfade gegen den freigegebenen Pilotpfad |
| 16 | Maintainer-only interne Testläufe oder interne System-Evidence werden als Pilot-Nachweis oder Ersatz für positive Provider-Matrix behandelt |

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

### Incident-Stufen für den Mono-Pilot

Die folgenden drei Stufen reichen für den text-first MVP. Sie sind keine
klinische Klassifikation, sondern eine operative Mono-Ops-Taxonomie für
Stop-, Pause- und Nachfassentscheidungen.

| Stufe | Typ | Typische Auslöser | Sofortmaßnahme | Betriebswirkung | Nachfasslogik |
|---|---|---|---|---|---|
| **I1 – Session-lokaler Safety-Vorfall** | Einzelne betroffene Session | Safeword, expliziter Abbruch, Distress, Krisensprache, Boundary-Fall | Betroffene Session sofort stoppen oder pausieren; externer Verweis falls nötig; nur Ereignistyp + Zeitstempel dokumentieren | Pilot kann weiterlaufen, solange kein Muster sichtbar wird | Prüfen: Einzelfall oder Muster? Bei Muster → mindestens `I2` |
| **I2 – Guard-/System-Vorfall** | Sicherheitsrelevante Systemabweichung | Verbotener Output erreicht Nutzer, fail-closed greift nicht sauber, Exit/Safeword instabil, wiederkehrende Safety-Events ohne Begrenzung | Pilot sofort pausieren; betroffenen Pfad isolieren; Root Cause analysieren; Guard-/Kernel-Lücke schließen | Keine neuen Live-Sessions bis Prüfung und Fix erfolgt sind | Nach Behebung Guard-Check dokumentieren; erst dann Fortführung |
| **I3 – Privacy-/Containment-Vorfall** | Daten- oder Provider-Grenze verletzt | Content-Logging, ungewollte Persistenz, reale Personendaten bei ungeklärtem Providerpfad, Löschpfad versagt | Pilot sofort stoppen; Verstoß eingrenzen; Daten löschen soweit möglich; Löschung bestätigen | Kein Neustart des Piloten bis vollständige Behebung | Root Cause schließen, Canon-/Konfigurationslücke dokumentieren, Neustart nur nach sauberer Neubewertung |

**Wichtig:** Es gibt keine 24/7-Eskalationskette und keinen Team-Dispatch. Der
Mono-Pfad ist bewusst klein: Session begrenzen, Pilot pausieren oder stoppen,
dann nüchtern prüfen und erst nach belegter Behebung fortführen.

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

### Postmortem-Minimum

Für `I2` und `I3` genügt im Mono-Setup ein kleines, redigiertes Feldset:

- Datum / Zeit
- Incident-Stufe (`I1`, `I2`, `I3`)
- betroffener Bereich oder Pfad
- Sofortmaßnahme
- Containment-/Löschstatus
- Restart-Entscheidung (`weiter`, `pausiert`, `gestoppt`)
- Root Cause / Canon-Lücke in knapper, nicht-inhaltlicher Form

Kein Nutzertext, kein Prompt, kein LLM-Output, kein Auslösetext. Kein
Postmortem im Team-Format; die Funktion ist operative Nachvollziehbarkeit für
den Solo-Maintainer, nicht Prozess-Theater.

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
| 8 | Sind externe Provider (KI-API, Hosting, E-Mail falls genutzt) nur mit positiv bewerteter `PROVIDER_DPA_INPUT_MATRIX.md` eingebunden – oder noch gar keine personenbezogenen Daten übergeben? | Ja |
| 9 | Enthält das Onboarding KI-Transparenz, Systemgrenzen und Safeword-Einführung? | Ja |
| 10 | Ist das Verhalten bei Safety-Ereignis definiert (Safe State, fail-closed)? | Ja |
| 11 | Kommuniziert der Pilot-Rahmen kein Therapie-, Diagnose- oder Companion-Versprechen? | Ja |
| 12 | Kann bei Safety-Event oder Guard-Fehlleistung sofort pausiert oder gestoppt werden? | Ja |

**Wenn eine Antwort Nein ist: kein Pilotstart. Lücke schließen, Check wiederholen.**
