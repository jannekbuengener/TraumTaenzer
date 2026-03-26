# PROVIDER_DPA_INPUT_MATRIX

Status: aktiv | Owner: Jannek Büngener | Zuletzt geprüft: 2026-03-26

Basis: PRIVACY_BY_DESIGN §2, §5, §6, §9; DEPLOYMENT_ENVELOPE §4–§7;
PILOT_READINESS §3.4, §8; SYSTEM_INVARIANTS P-1–P-4, A-4

---

## 1. Zweck und Geltungsbereich

Diese Matrix ist das minimale Intake-Artefakt für externe Provider im
text-first MVP. Sie sammelt die wenigen Informationen, die vor Live-Nutzer-
Verkehr mit personenbezogenen oder inhaltsbezogenen Daten geklärt sein müssen.

Sie ist:
- kein Rechtsersatz
- keine fertige DPIA
- keine finale Provider-Auswahl
- keine Vertragsprüfung im Detail

Sie ist die verbindliche Go/No-Go-Grundlage dafür, ob ein konkreter externer
Providerpfad für reale Nutzer überhaupt in Pilot oder produktionsnahem Betrieb
freigeschaltet werden darf.

---

## 2. Wann die Matrix zwingend ausgefüllt sein muss

Die Matrix muss vorliegen, bevor:

- ein LLM-Provider mit realen Personendaten oder Session-Kontext genutzt wird
- ein Hosting- oder Infrastrukturpfad reale Personendaten verarbeitet
- ein E-Mail-Dienst für Nutzerkommunikation eingesetzt wird
- ein weiterer externer Dienst mit Personenbezug oder Content-Bezug hinzukommt
- ein bestehender Provider auf ein anderes Produkt, eine andere API, Region oder
  wesentliche Datenpolitik umgestellt wird

Ohne ausgefüllte Matrix bleibt ein Provider auf Dev ohne reale Personendaten
beschränkt.

---

## 3. Betroffene Provider-Klassen

| Provider-Klasse | Typische Rolle | Muss diese Matrix nutzen? |
|---|---|---|
| **LLM** | Textgenerierung über externe API | Ja |
| **Hosting** | Server, Datenhaltung, Plattformdienste mit Personenbezug | Ja |
| **E-Mail** | Versand von Login-, Kontakt- oder Service-Mails | Ja, sobald echte Nutzerdaten betroffen sind |
| **Weitere externe Dienste** | z. B. Monitoring, Support, Analytics, Storage | Ja, sobald Personenbezug oder Content-Bezug entsteht |

---

## 4. Pflichtfragen pro Provider

Jeder konkrete Providerpfad muss diese Fragen beantworten. „Anbieter ist
bekannt" reicht nicht; entscheidend ist das genaue Produkt/API mit seiner
konkreten Datenpolitik.

| Prüffeld | Was konkret geklärt sein muss | No-Go bei ungeklärt |
|---|---|---|
| **Konkretes Produkt / API** | Exaktes Produkt, API-Typ, Tarif oder Betriebsmodus; nicht nur der Anbietername | Ja |
| **Datenklassen über der Grenze** | Welche Datenklassen die Grenze tatsächlich passieren: Prompt-Kontext, Output, Logs, Account-Daten, Metadaten | Ja |
| **DPA / AVV** | Gibt es einen DPA/AVV, und gilt er für genau dieses Produkt/API? | Ja |
| **Retention** | Wie lange werden Prompts, Outputs, Logs, Metadaten und Backups gehalten? | Ja |
| **Training / Service-Verbesserung / Opt-out** | Werden Daten für Training oder Service-Verbesserung genutzt, und welche Default-/Opt-out-Lage gilt? | Ja |
| **Region / internationale Übermittlung / Rechtsgrundlage** | Wo wird verarbeitet, welche Transfers finden statt, und auf welcher Grundlage? | Ja |
| **Subprocessor** | Welche Subprocessor sind beteiligt, und für welche Teilverarbeitung? | Ja |
| **Löschpfad inkl. Support-Logs / Backups** | Wie werden Daten gelöscht, auch außerhalb des Hauptpfads? | Ja |
| **Go/No-Go vor erstem Live-Nutzer** | Ergibt die Gesamtsicht einen positiven Einsatzentscheid für reale Nutzer? | Ja |

---

## 5. No-Go-Regeln

Wenn einer dieser Punkte zutrifft, ist der Providerpfad nicht für Live-Nutzer
zulässig:

- Das konkrete Produkt/API ist nicht eindeutig benannt.
- DPA/AVV fehlt oder ist nicht eindeutig auf dieses Produkt/API anwendbar.
- Retention, Training/Service-Verbesserung, Region/Transfer oder Subprocessor
  sind ungeklärt.
- Der Löschpfad ist nur für den Hauptpfad beschrieben, nicht aber für Support-
  Logs, Metadaten oder Backups.
- Der geplante Einsatz würde reale Personendaten an einen Provider senden,
  dessen Matrix nicht positiv bewertet ist.

**Keine weiche Auslegung:** „Wir testen erst einmal im kleinen Pilot" ist kein
Ersatz für diese Klärung. Pilot mit Live-Nutzern bleibt Live-Nutzung.

---

## 6. Minimaler Entscheidungsstatus

Jeder Providerpfad erhält genau einen Status:

| Status | Bedeutung |
|---|---|
| **zulässig für Dev ohne reale Personendaten** | Lokale Entwicklung, Tests, Demos oder technische Smoke-Tests ohne echte Personendaten |
| **nicht zulässig für Live-Nutzer** | Für Pilot und produktionsnahe Nutzung gesperrt; Klärung fehlt oder fällt negativ aus |
| **zulässig für Pilot** | Matrix ist ausgefüllt und positiv bewertet; Live-Nutzer-Einsatz im kontrollierten Pilot ist zulässig |

`zulässig für Pilot` ist kein Blanket-Go für Produktisierung. Bei Produkt-, API-,
Region- oder Datenpolitikwechsel ist die Matrix neu zu prüfen.

---

## 7. Minimale Ausfüllmatrix pro Providerpfad

| Provider-Klasse | Konkretes Produkt / API | Welche Datenklassen passieren die Grenze? | DPA / AVV passend? | Retention geklärt? | Training / Opt-out geklärt? | Region / Transfer geklärt? | Subprocessor geklärt? | Löschpfad inkl. Support-Logs / Backups geklärt? | Entscheidungsstatus |
|---|---|---|---|---|---|---|---|---|---|
| **LLM** | eintragen | eintragen | ja / nein / offen | ja / nein / offen | ja / nein / offen | ja / nein / offen | ja / nein / offen | ja / nein / offen | eintragen |
| **Hosting** | eintragen | eintragen | ja / nein / offen | ja / nein / offen | n. a. / ja / nein / offen | ja / nein / offen | ja / nein / offen | ja / nein / offen | eintragen |
| **E-Mail** | eintragen | eintragen | ja / nein / offen | ja / nein / offen | n. a. / ja / nein / offen | ja / nein / offen | ja / nein / offen | ja / nein / offen | eintragen |
| **Weiterer externer Dienst** | eintragen | eintragen | ja / nein / offen | ja / nein / offen | ja / nein / offen | ja / nein / offen | ja / nein / offen | ja / nein / offen | eintragen |

---

## 8. Operative Nutzungsregel

Vor erstem Live-Nutzer-Verkehr:

1. Matrix für jeden real beteiligten Providerpfad ausfüllen.
2. Offene Felder nicht mit Annahmen schließen.
3. Entscheidungsstatus je Providerpfad setzen.
4. Wenn auch nur ein für Live-Nutzer relevanter Providerpfad nicht positiv
   bewertet ist: kein Pilotstart.

Die Matrix soll den Solo-Maintainer entlasten, nicht eine Scheinsicherheit
erzeugen. Wenn die Faktenlage unklar ist, ist der korrekte Status nicht
„wahrscheinlich okay", sondern `nicht zulässig für Live-Nutzer`.
