# PRIVACY_BY_DESIGN

Status: aktiv | Owner: Jannek Büngener | Zuletzt geprüft: 2026-04-03

---

## 1. Zweck und Geltungsbereich

Dieses Dokument definiert verbindliche Datenprinzipien, Datenklassen, Speicher- und Löschregeln sowie Export- und Logging-Grenzen für Traumtänzer. Es ist operativer P0-Canon – keine fertige DPIA, keine TOM-Liste, kein Rechtsersatz.

Es gilt für alle Systemkomponenten, UX-Flows, KI-Interaktionen, Session-Designs und technischen Entscheidungen, sobald personenbezogene oder inhaltsbezogene Daten verarbeitet werden.

Nicht-Ziel dieses Dokuments: juristische Vollständigkeit, Subprozessor-Abschlussbeurteilung, fertige TOMs. Offene Prüfpunkte sind explizit als solche markiert.

---

## 2. Privacy-Prinzipien

**Privacy-by-Default, nicht auf Antrag.**
Jede neue Funktion, jeder neue Flow, jedes neue Log startet mit der Annahme: kein Speichern, kein Tracking, keine Persistenz – bis ein konkreter, minimaler Zweck belegt ist.

**Datenminimierung vor Datenvollständigkeit.**
Es werden nur Daten erhoben, die für den unmittelbaren Zweck notwendig sind. Kein Vorratsdatendenken. Kein „könnte später nützlich sein".

**Redaction-first.**
Bevor etwas persistiert wird, wird geprüft: Kann stattdessen ein aggregierter Wert, ein Hash, ein Flag oder gar nichts gespeichert werden?

**Traumtexte und Sitzungsinhalte sind hochsensibel.**
Nutzereingaben in Reflexions- und Erlebnissessions können Informationen zu psychischer Gesundheit, Traumata und weiteren Sonderkategorien nach DSGVO Art. 9 enthalten. Diese werden nicht als Default gespeichert.

**Keine implizite Datenpersistenz.**
Was nicht ausdrücklich persistiert werden soll, wird nicht persistiert. Kein stilles Logging, kein implizites Caching von Inhalten.

**Externe Provider sind ein Risikofaktor.**
Daten, die an externe Dienste (KI-Provider, Infrastruktur, Kommunikationsanbieter) übermittelt werden, unterliegen deren Datenschutzbedingungen. Diese Abhängigkeiten werden als offene Prüfpunkte geführt, nicht als abgeschlossen behandelt.

---

## 3. Datenklassen

| Klasse | Beispiele | Sensitivität | Speicher-Default |
|---|---|---|---|
| **Session-Inhalte** | Traumtexte, Reflexionseingaben, Antworten in geführten Flows | Sehr hoch – potentiell Art. 9 DSGVO | Kein Speichern |
| **Safety-Events** | Safeword-Auslösung, Exit-Ereignis, Trigger-Signal | Hoch | Minimal, redacted (kein Content) |
| **Nutzungsmetadaten** | Session-Zeitstempel, Session-ID, Sitzungsdauer | Mittel | Nur wenn technisch notwendig |
| **Account-/Kontaktdaten** | E-Mail-Adresse, Nutzername | Mittel | Nur für Zugangsverwaltung |
| **Technische Logs** | Fehler-Codes, System-Events | Niedrig | Zeitlich begrenzt, kein Nutzerinhalt |
| **Governance-Artefakte** | Dieses Repo, Policies, Protokolle | Intern | Versioniert, kein Personenbezug |

**Trennungsregel:** Session-Inhalte, Safety-Events und Nutzungsmetadaten werden nicht gemeinsam in einem Datensatz gespeichert. Kein Linking ohne expliziten, dokumentierten Zweck.

**MVP-Entscheidung für Session-Bezug:** `session_id` ist eine opaque, zufällige
Pseudonym-ID pro Session, kein Nutzerpseudonym über mehrere Sessions hinweg. Sie
darf Runtime-Ereignisse derselben Session korrelieren, aber nicht still mit
Account-/Access-Daten, E-Mail, Pilotlisten, Geräte- oder Analytics-Daten
verknüpft werden.

---

## 4. Speicherregeln / minimale Persistenz

### Grundregel

Nichts wird persistiert, solange kein konkreter, minimaler Zweck vorliegt. Im Zweifel: nicht speichern.

### Runtime-Daten

- Session-Inhalte (Nutzereingaben, KI-Antworten in der Session) sind ephemer: sie existieren nur während der aktiven Session.
- Nach Session-Ende: kein automatisches Persistieren von Inhalten.
- Wenn Nutzer eine Speicherung wünscht (z. B. eigenes Journal): explizites Opt-in erforderlich, technische Umsetzung noch zu definieren.

### Enger maintainer-only interner Testmodus

Der provider-neutrale maintainer-only interne Testmodus ist kein allgemeiner
Privacy-Override, sondern ein eng begrenzter Sonderpfad für interne Systemtests
auf einem kontrollierten Systempfad. Die Privacy-Defaults dieses Dokuments
bleiben für alle anderen Pfade unverändert.

- Nur maintainer-only; keine Pilot- oder Live-Nutzung.
- Nur kontrollierter Systempfad; keine Nebenpfade, keine Schattenablage, kein Schattenbetrieb.
- Eigenes Material des Maintainers ist zulässig.
- Material mit Drittbezug darf nur vorab abstrahiert, entschärft oder entfernt genutzt werden; kein Drittrohmaterial.
- Lokale Rohablage ist nur eng begrenzt zulässig, wenn sie für den konkreten Testlauf notwendig ist; maximale Haltedauer: 7 Tage.
- Für solche lokal abgelegten Rohinhalte besteht explizite Löschpflicht; stilles Liegenlassen ist kein zulässiger Default.
- Verboten ist jede Spiegelung in Repo, Tickets, Logs, Screenshots, Testfixtures, Beispieldaten oder sonstigen Nebenartefakten.
- Die pro Lauf geforderte Traceability bleibt content-frei und enthält keinen Rohinhalt.
- Der Modus erzeugt nur interne System-Evidence; er begründet weder Pilot-Go noch Live-Go noch Provider-Freigabe.

### Logs

- Technische Logs enthalten keine Nutzerinhalte, keine Session-Texte, keine Trauminhalte.
- Safety-Event-Logs enthalten nur Ereignistyp und Zeitstempel, keinen Auslösetext.
- Content-Logs sind verboten, es sei denn, ein konkreter technischer Notwendigkeitsnachweis liegt vor – dann nur redacted und zeitlich begrenzt.

### Knowledge-Artefakte

- Governance-Dokumente (dieses Repo) enthalten keine personenbezogenen Nutzerdaten.
- Interne Protokolle und Session-Logs des Projekts (unter `knowledge/logs/`) enthalten keine Nutzerinhalte.

### Trennung der Schichten

```
Runtime (ephemer)          → keine Persistenz ohne expliziten Zweck
Technische Logs            → Metadaten, kein Content, zeitlich begrenzt
Account-Verwaltung         → minimal, nur Zugang
Safety-Ereignisse          → Typ + Zeitstempel, kein Auslösetext
Governance / Repo          → kein Personenbezug
```

---

## 5. Logging und Analytics

**Content-Logging ist verboten als Default.**
Keine Trauminhalte, keine Reflexionstexte, keine Nutzereingaben in Logs.

**Analytics mit minimalen Aggregaten.**
Wenn Nutzungsstatistiken erhoben werden, dann nur aggregiert und ohne Nutzer-Einzelprofile. Kein Behavioral Tracking, kein Clickstream, keine Sitzungsrekonstruktion.

**Safety-Event-Logging ist erlaubt, aber begrenzt.**
- Erlaubt: Ereignistyp (Safeword, Exit, Abbruch), Zeitstempel, Session-ID (pseudonym).
- Verboten: Auslösetext, Nutzerformulierungen, Inhaltskontext.
- Zweck: systemische Qualitätssicherung, nicht Nutzerprofilierung.
- Debugging ändert diese Grenze nicht: kein Join von `session_id` mit
  Nutzeridentität, Kontaktlisten, Prompt-/Output-Rohdaten oder Support-Notizen
  als Default-Pfad.

**KI-Provider-Logs sind ein offener Prüfpunkt.**
Was externe KI-Dienste aus übermittelten Prompts und Antworten loggen, unterliegt deren Bedingungen. Vor Produktionsstart: Prüfung der Datenverarbeitungsvereinbarungen und Prompt-Datenpolitik des Providers (→ Abschnitt 9).

---

## 6. Retention

### Grundprinzip

Keine Vorratsdatenhaltung. Daten werden nur so lange gehalten, wie der dokumentierte Zweck besteht.

### Retention-Tabelle

| Datenklasse | Maximale Haltedauer | Begründung |
|---|---|---|
| Session-Inhalte | Keine Persistenz (Default) | Kein Zweck nach Session-Ende |
| Safety-Event-Logs | 90 Tage | Systemqualität, danach löschen |
| Nutzungsmetadaten | 90 Tage oder kürzer | Technischer Betrieb |
| Account-Daten | Solange Konto aktiv + 30 Tage nach Kündigung | Zugangsverwaltung |
| Technische Fehler-Logs | 30 Tage | Debugging |

**Hinweis:** Diese Fristen sind initialer Canon. Bei Produktionsstart sind sie gegen konkrete technische Architektur und geltende Anforderungen zu validieren und ggf. anzupassen.

---

## 7. Löschung

### Grundregel

Löschung muss technisch möglich und operativ zuverlässig sein, bevor Daten überhaupt persistiert werden. Keine Datenpersistenz ohne definierten Löschpfad.

### Nutzer-initiierte Löschung

Der Nutzer kann die Löschung seines Kontos und der zugehörigen persistierten Nutzerdaten veranlassen. Etwaige eng begrenzte Restdaten mit dokumentiertem Betriebs- oder Rechtsgrund sind gesondert zu behandeln und dürfen nicht als versteckte Vorratsdatenhaltung genutzt werden.

- Löschung muss ohne unverhältnismäßige Hürden erreichbar sein.
- Bestätigung der Löschung an den Nutzer (technische Umsetzung noch zu definieren).
- Pseudonyme Runtime-Events werden im MVP nicht über einen stillen
  Account-Lookup gesucht oder gelöscht; ohne separaten, dokumentierten
  Zuordnungspfad gilt für sie die Retention-/Löschlogik des Event-Storage.

### Automatische Löschung

- Daten, deren Retention-Frist abgelaufen ist, werden automatisch gelöscht.
- Kein manueller Eingriff erforderlich für Routine-Löschungen.

### Safety-Event-Daten

- Nach 90 Tagen automatisch gelöscht.
- Kein Archivieren ohne dokumentierten Grund.

### Offene Prüfpunkte

- Wie wird Löschung bei externen Providern (KI-API, Hosting) sichergestellt? → Abschnitt 9.
- Wie werden Backup-Systeme in die Löschlogik einbezogen? → Vor Live-Nutzerbetrieb zwingend zu definieren; bis dahin Blocker.

---

## 8. Export

### Grundregel

Der Nutzer hat das Recht, seine eigenen Daten zu erhalten. Dieser Exportpfad muss technisch vorgesehen werden, bevor Daten persistiert werden.

### Exportumfang

- Account-Daten (E-Mail, Einstellungen).
- Nutzungsdaten, die dem Nutzer zugeordnet sind und persistiert wurden.
- Nicht Teil des Standard-Nutzerexports sind interne Betriebslogs und Safety-Event-Logs. Ob und in welchem Umfang solche Daten im Rahmen von Auskunftsrechten relevant werden, ist gesondert zu prüfen.
- Reine Runtime-Events mit nur pseudonymer `session_id` sind im MVP kein
  Standard-Exportpfad, solange kein separater, dokumentierter Zuordnungspfad
  zu Account-/Access-Daten besteht.

### Format und Zugang

- Maschinenlesbares Format (z. B. JSON) als Baseline.
- Zugang ohne unverhältnismäßige Hürden.
- Technische Implementierung noch zu definieren bei Infrastrukturplanung.

### Einschränkung bei Session-Inhalten

Da Session-Inhalte nicht als Default persistiert werden, gibt es für den Regelfall keine exportierbaren Session-Texte. Wenn ein optionales Nutzer-Journal implementiert wird, muss dieses vollständig exportierbar sein.

---

## 9. Externe Provider / offene Prüfblöcke

Externe Provider werden als aktives Risiko geführt, nicht als abgeschlossen behandelt.

Vor jeder Nutzung externer Provider mit realen Personendaten muss die
`knowledge/project/PROVIDER_DPA_INPUT_MATRIX.md` für den konkret genutzten
Produktpfad ausgefüllt werden. Diese Matrix ist die verbindliche
Entscheidungsgrundlage für Live-Nutzer-Nutzung; ohne ausgefüllte und positiv
bewertete Matrix bleibt der Provider auf Dev ohne reale Personendaten
beschränkt.

### Offene Prüfpunkte (Stand 2026-03-25)

| Prüfpunkt | Status | Wer muss handeln |
|---|---|---|
| KI-API-Provider: konkretes Produkt/API, DPA, Prompt-/Output-Retention | Offen – über `PROVIDER_DPA_INPUT_MATRIX.md` zu klären | Owner / technische Umsetzung |
| Hosting/Infrastruktur: Produktpfad, Serverstandort, DPA, Löschpfad | Offen – über Matrix zu klären | Owner / technische Umsetzung |
| E-Mail-Dienst (falls genutzt): Produktpfad, DPA, Retention, Region | Offen – über Matrix zu klären | Owner / technische Umsetzung |
| Subprozessor-Liste und internationale Übermittlungen | Offen – pro Providerpfad über Matrix zu klären | Owner |

### Grundsatz bis zur Klärung

Keine Produktions- oder Pilotnutzung personenbezogener Daten mit externen
Providern, solange DPA, Datenpolitik, Retention, Region und Subprocessor-Lage
nicht über die `PROVIDER_DPA_INPUT_MATRIX.md` geprüft, dokumentiert und positiv
bewertet sind.

### Was dieses Dokument nicht leistet

Keine vollständige Subprozessor-Liste. Keine abgeschlossene DPIA. Keine finalen TOMs. Diese sind Aufgaben für die Produktionsphase – auf Basis dieses Canon-Rahmens.

---

## 10. Operativer Kurz-Check für neue Features, Flows oder Logs

Vor Umsetzung jedes neuen Features, jedes neuen Datenflusses oder jedes neuen Logs: alle Fragen prüfen.

**Fragen zur Datenerhebung:**

1. Welche Daten werden erhoben – und sind diese wirklich notwendig für den konkreten Zweck?
2. Enthält der Flow Nutzerinhalte (Texte, Reflexionen, Eingaben)? Wenn ja: warum werden diese persistiert?
3. Kann stattdessen ein Aggregat, ein Flag oder gar nichts gespeichert werden (Redaction-first)?

**Fragen zur Persistenz:**

4. Ist der Löschpfad für diese Daten definiert, bevor sie gespeichert werden?
5. Ist die Retention-Frist festgelegt?
6. Werden externe Provider einbezogen? Wenn ja: ist die `PROVIDER_DPA_INPUT_MATRIX.md` für den konkreten Produktpfad positiv bewertet?

**Fragen zu Logs:**

7. Enthält dieses Log Nutzerinhalte oder Auslöse-Texte? Wenn ja: Logging verboten oder redacten.
8. Ist dieser Log wirklich für den Betrieb notwendig – oder nur „könnte nützlich sein"?

**Stopp-Kriterien:**
Wenn eine der folgenden Bedingungen zutrifft, darf der Flow oder das Log nicht eingeführt werden, bis die Frage geklärt ist:

- Session-Inhalte würden als Default persistiert.
- Kein Löschpfad ist definiert.
- Externe Provider werden einbezogen ohne positiv bewertete `PROVIDER_DPA_INPUT_MATRIX.md`.
- Daten aus verschiedenen Klassen werden ohne dokumentierten Zweck verknüpft.
