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
| **LLM** | Azure OpenAI Service in Microsoft Foundry, `Chat Completions API` mit `gpt-4o-mini (2024-07-18)`, `Standard` Deployment in `Sweden Central`; ausdrücklich nicht `Responses API`, `Threads` oder `Stored completions` | Redacted Prompt-Kontext mit potentiell hochsensiblen Reflexionsinhalten, transienter Modell-Output, Request-/Betriebsmetadaten; bei Abuse-Monitoring zusätzlich selektierte Prompt-/Output-Samples | ja | offen | ja | ja | offen | offen | nicht zulässig für Live-Nutzer |
| **Hosting** | eintragen | eintragen | ja / nein / offen | ja / nein / offen | n. a. / ja / nein / offen | ja / nein / offen | ja / nein / offen | ja / nein / offen | eintragen |
| **E-Mail** | eintragen | eintragen | ja / nein / offen | ja / nein / offen | n. a. / ja / nein / offen | ja / nein / offen | ja / nein / offen | ja / nein / offen | eintragen |
| **Weiterer externer Dienst** | eintragen | eintragen | ja / nein / offen | ja / nein / offen | ja / nein / offen | ja / nein / offen | ja / nein / offen | ja / nein / offen | eintragen |

---

### Bewertungsnotiz 2026-03-26 – LLM-Arbeitskandidat

**Arbeitsannahme für diese Bewertung:** Da das Repo bewusst provider-agnostisch
bleibt und keinen konkreten Anbieter vorgibt, wird genau ein plausibler
LLM-Pfad für den text-first MVP bewertet:
`Azure OpenAI Service` in Microsoft Foundry, `Chat Completions API`,
`gpt-4o-mini (2024-07-18)`, `Standard` Deployment in `Sweden Central`.

**Warum genau dieser Zuschnitt:** `DEPLOYMENT_ENVELOPE.md` verbietet
provider-seitigen Conversation-State im MVP. Deshalb wurde der stateful
`Responses API`-/`Threads`-/`Stored completions`-Pfad nicht als Live-Kandidat
gewertet.

**Offizielle Quellenbasis (Stand 2026-03-26):**

- Microsoft: Data, privacy, and security for Azure Direct Models in Microsoft
  Foundry (`https://learn.microsoft.com/en-us/legal/cognitive-services/openai/data-privacy`)
- Microsoft: Deployment types for Foundry models
  (`https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-models/concepts/deployment-types`)
- Microsoft: Azure OpenAI / Foundry model availability
  (`https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/models`)
- Microsoft: Azure Direct Models abuse monitoring
  (`https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/abuse-monitoring`)
- Microsoft: Products and Services Data Protection Addendum (DPA)
  (`https://www.microsoft.com/licensing/docs/view/Microsoft-Products-and-Services-Data-Protection-Addendum-DPA`)

**Belastbar geklärt:**

- Das Produkt ist real und konkret benannt: `Azure OpenAI Service` /
  Azure-Direct-Model-Pfad in Microsoft Foundry mit `Chat Completions API`.
- `gpt-4o-mini (2024-07-18)` ist laut offizieller Modellverfügbarkeit für
  `Standard` Deployment in `Sweden Central` verfügbar.
- Microsoft dokumentiert für Azure Direct Models, dass Prompts, Outputs,
  Embeddings und Trainingsdaten nicht an OpenAI oder andere Modellanbieter
  weitergegeben werden.
- Für inferencing gilt laut offizieller Datenprivacy-Doku: Modelle sind
  stateless; Prompts und Completions werden nicht im Modell gespeichert und
  nicht zum Training, Retraining oder zur Verbesserung der Basismodelle
  verwendet.
- Für `Standard`-/`Regional`-Deployments gilt laut Deployment-Type-Doku:
  Inferencing-Daten werden in der Deployment-Region verarbeitet; für den
  gewählten Pfad also `Sweden Central`.
- Die Microsoft-DPA ist offiziell verfügbar, und die Datenprivacy-Doku nennt
  sie ausdrücklich als maßgebliche DPA-Grundlage für Azure Direct Models.
- Diese Bewertung bestätigt damit die offizielle Produktgeltung der DPA, nicht
  automatisch die bereits vollständig nachgewiesene Vertragsumsetzung im
  konkreten Azure-Tenant.

**Explizite Blocker / No-Go-Risiken:**

- **Retention nicht belastbar geschlossen:** Die offiziellen Microsoft-Quellen
  beschreiben Default-Abuse-Monitoring und mögliche Speicherung ausgewählter
  Prompt-/Output-Daten für Review, benennen für diesen konkreten Pfad aber in
  der hier verifizierten Quellenbasis keine belastbare Haltedauer.
- **Subprocessor-Lage nicht belastbar geschlossen:** Die DPA enthält allgemeine
  Subprocessor-Regeln, aber in der hier verifizierten Quellenbasis liegt keine
  konkret belegte, produktnahe Subprocessor-Liste speziell für diesen
  Azure-OpenAI-Pfad vor.
- **Löschpfad nicht belastbar geschlossen:** Die DPA enthält generelle
  Delete-/Return-Verpflichtungen, aber kein in dieser Session belastbar
  verifizierter produktnaher Löschpfad für Abuse-Monitoring-Artefakte,
  Support-Zugriffe und Backup-/Replikationsreste dieses konkreten Pfads.
- **Modified abuse monitoring ist kein Default:** Microsoft beschreibt einen
  Antragsweg zur Modifikation des Abuse-Monitorings. Für diese Bewertung liegt
  keine belastbare Grundlage vor, dass dieser Pfad bereits bewilligt oder für
  den MVP operativ verfügbar wäre.

**Operativer Entscheid:**

- `zulässig für Dev ohne reale Personendaten`: ja
- `zulässig für Pilot`: nein
- **Status vor erstem Live-Nutzer: `nicht zulässig für Live-Nutzer`**

Der Pfad ist damit keine Freigabegrundlage für reale Pilot-Nutzer. Die
Negativbewertung ist kein juristisches Endurteil, sondern eine operative
Go/No-Go-Bewertung für den MVP auf Basis der derzeit belastbar verifizierten
Microsoft-Quellen.

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
