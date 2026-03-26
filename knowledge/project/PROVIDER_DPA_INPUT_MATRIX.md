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
| **LLM** | Anthropic Claude API, `POST /v1/messages` mit `claude-sonnet-4-6` unter Commercial Terms; optional `inference_geo="us"`; ausdrücklich nicht `Files API`, `Messages Batches`, Console/Workbench oder gespeicherte Chat-Produkte | Redacted Prompt-Kontext mit potentiell hochsensiblen Reflexionsinhalten, transienter Modell-Output, Request-Metadaten; bei Policy-/Misuse-Flags zusätzlich retainte Input-/Output-Artefakte und Trust-&-Safety-Klassifikationen | ja | ja | ja | ja | offen | offen | nicht zulässig für Live-Nutzer |
| **LLM** | Amazon Bedrock Runtime, `InvokeModel` mit `anthropic.claude-sonnet-4-6` in `eu-central-1` (`Europe (Frankfurt)`), ohne Inference Profile / Cross-Region Inference; ausdrücklich nicht Agents, Knowledge Bases, Batch- oder Custom-Model-Pfade | Redacted Prompt-Kontext mit potentiell hochsensiblen Reflexionsinhalten, transienter Modell-Output, AWS Request-/Betriebsmetadaten; automatisierte Abuse-Detection-Klassifikationen | ja | offen | ja | ja | ja | offen | nicht zulässig für Live-Nutzer |
| **Hosting** | `Hetzner Cloud Server` in `nbg1` (`Nuremberg`, Deutschland) mit angehängtem `Hetzner Volume`; redacted Runtime-Events in lokalem `SQLite` auf dem `Volume`; keine Hetzner-Server-Backups, keine Snapshots, keine externen Replikate | Gegenüber Hetzner: Account-, Kontakt- und Abrechnungsdaten; auf dem Server selbst nur redacted Runtime-Events mit opaquer `session_id`, content-free Host-/App-Logs und technische Betriebsmetadaten; kein Session-Content | ja | ja | n. a. | ja | ja | ja | zulässig für Pilot |
| **E-Mail** | eintragen | eintragen | ja / nein / offen | ja / nein / offen | n. a. / ja / nein / offen | ja / nein / offen | ja / nein / offen | ja / nein / offen | eintragen |
| **Weiterer externer Dienst** | eintragen | eintragen | ja / nein / offen | ja / nein / offen | ja / nein / offen | ja / nein / offen | ja / nein / offen | ja / nein / offen | eintragen |

---

### Bewertungsnotizen 2026-03-26 – geprüfte LLM-Pfade

Diese Session bewertet drei produktgenaue, stateless text-in/text-out-Pfade
gegen die Matrix:

- `Azure OpenAI Service` in Microsoft Foundry, `Chat Completions API`,
  `gpt-4o-mini (2024-07-18)`, `Standard` Deployment in `Sweden Central`
- `Anthropic Claude API`, `POST /v1/messages`, `claude-sonnet-4-6`
- `Amazon Bedrock Runtime`, `InvokeModel`,
  `anthropic.claude-sonnet-4-6`, `eu-central-1`

Nicht bewertet wurden stateful oder speichernde Zusatzpfade wie `Responses API`,
`Threads`, `Stored completions`, `Files API`, `Messages Batches`,
Console/Workbench, Agents, Knowledge Bases oder Custom-Model-/Fine-Tuning-
Pfade, weil sie im MVP entweder verboten sind oder eigene Persistenzpfade
öffnen.

#### A. Azure OpenAI Service – bestehender Negativbefund

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

- Das Produkt ist real und konkret benannt; der bewertete Pfad ist stateless
  und liegt innerhalb des MVP-Envelope.
- Microsoft dokumentiert, dass Prompts, Outputs und Embeddings nicht an OpenAI
  oder andere Modellanbieter weitergegeben und nicht zum Basismodelltraining
  verwendet werden.
- Für `Standard`-/`Regional`-Deployments werden Inferencing-Daten in der
  Deployment-Region verarbeitet; für den gewählten Pfad also `Sweden Central`.
- Die Microsoft-DPA ist offiziell verfügbar und in der Datenprivacy-Doku für
  Azure Direct Models ausdrücklich referenziert.

**Blocker / No-Go-Risiken:**

- Retention für den konkreten Abuse-Monitoring-Pfad bleibt in der hier
  verifizierten Quellenbasis offen.
- Produktnahe Subprocessor-Liste für genau diesen Pfad bleibt offen.
- Produktnaher Löschpfad für Abuse-Monitoring-Artefakte, Support-Zugriffe und
  Backup-/Replikationsreste bleibt offen.
- Modified abuse monitoring ist kein Default und für den MVP nicht belastbar
  nachgewiesen.

**Operativer Entscheid:** `nicht zulässig für Live-Nutzer`

#### B. Anthropic Claude API – direkter API-Arbeitskandidat

**Offizielle Quellenbasis (Stand 2026-03-26):**

- Anthropic: Messages API (`https://platform.claude.com/docs/en/api/messages.md`)
- Anthropic: Models overview
  (`https://platform.claude.com/docs/en/about-claude/models/overview.md`)
- Anthropic: Commercial Terms of Service
  (`https://www.anthropic.com/legal/commercial-terms`)
- Anthropic: Data Processing Addendum
  (`https://www.anthropic.com/legal/data-processing-addendum`)
- Anthropic: Privacy Policy (`https://www.anthropic.com/legal/privacy`)
- Anthropic: Supported regions
  (`https://platform.claude.com/docs/en/api/supported-regions.md`)
- Anthropic: Data residency
  (`https://platform.claude.com/docs/en/build-with-claude/data-residency.md`)
- Anthropic: Zero Data Retention
  (`https://platform.claude.com/docs/en/build-with-claude/zero-data-retention.md`)
- Anthropic Privacy Center: How long do you store my organization's data?
  (`https://privacy.claude.com/en/articles/7996866-how-long-do-you-store-my-organization-s-data`)

**Belastbar geklärt:**

- `POST /v1/messages` ist ein realer, stateless API-Pfad; Mehrturn-Kontext wird
  im Request übergeben, nicht als externer Thread-State erzwungen.
- Die Commercial Terms gelten ausdrücklich für Anthropic API keys und Services;
  der DPA ist darin per Referenz eingebunden und gilt für die Services.
- Unter Commercial Terms darf Anthropic Customer Content aus den Services nicht
  zum Modelltraining verwenden.
- Für API-Nutzer gilt laut Privacy Center eine Standard-Retention von 30 Tagen
  für Inputs/Outputs; bei Usage-Policy-Verstößen können Inputs/Outputs bis zu
  2 Jahre und Trust-&-Safety-Klassifikationen bis zu 7 Jahre gehalten werden.
- `inference_geo` erlaubt nur `global` oder `us`; Workspace-Geo ist derzeit nur
  `us`. Für Transfers außerhalb EEA/UK nennt Anthropic Adequacy und SCCs als
  Rechtsgrundlagen.
- ZDR ist für `/v1/messages` grundsätzlich als separater Arrangement-Pfad
  beschrieben, gilt aber nicht automatisch und behält Gesetz-/Misuse-
  Ausnahmen bei.

**Blocker / No-Go-Risiken:**

- Die öffentliche Subprocessor-Liste ist offiziell verlinkt, die konkrete
  Subprocessor-/Rollenlage für diesen Pfad war in dieser Session aus den
  offiziellen Quellen aber nicht belastbar extrahierbar und bleibt operativ
  offen.
- Der Löschpfad ist für den Standardpfad nur teilweise geschlossen:
  30-Tage-Backend-Löschung und DPA-Delete/Return sind dokumentiert, aber
  Support-/Nebenartefakte sowie die genaue Side-Path-Logik für Missbrauchs-,
  Rechts- und Backup-Ausnahmen bleiben nicht produktnah genug belegt.
- Ohne bereits aktiviertes ZDR-Arrangement bleibt der Standardpfad mit 30-Tage-
  Retention plus Misuse-Ausnahmen der operative Default.

**Operativer Entscheid:** `nicht zulässig für Live-Nutzer`

#### C. Amazon Bedrock Runtime – Cloud-vermittelter API-Arbeitskandidat

**Offizielle Quellenbasis (Stand 2026-03-26):**

- AWS: Amazon Bedrock data protection
  (`https://docs.aws.amazon.com/bedrock/latest/userguide/data-protection.html`)
- AWS: Amazon Bedrock abuse detection
  (`https://docs.aws.amazon.com/bedrock/latest/userguide/abuse-detection.html`)
- AWS: Amazon Bedrock FAQs (`https://aws.amazon.com/bedrock/faqs/`)
- AWS: Model support by AWS Region in Amazon Bedrock
  (`https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html`)
- AWS: AWS Service Terms (`https://aws.amazon.com/service-terms/`)
- AWS: GDPR Center (`https://aws.amazon.com/compliance/gdpr-center/`)
- AWS: AWS GDPR DPA PDF
  (`https://d1.awsstatic.com/legal/aws-gdpr/AWS_GDPR_DPA.pdf`)
- AWS: AWS Sub-processors (`https://aws.amazon.com/compliance/sub-processors/`)

**Belastbar geklärt:**

- `InvokeModel` auf Amazon Bedrock ist ein realer, stateless API-Pfad; das
  konkrete Modell `anthropic.claude-sonnet-4-6` ist laut Regionsmatrix in
  `Europe (Frankfurt)` verfügbar.
- AWS dokumentiert, dass Amazon Bedrock Prompts und Completions nicht speichert
  oder loggt, nicht zum Training von AWS-Modellen verwendet und nicht an
  Dritte verteilt; Modellanbieter haben keinen Zugriff auf Prompts,
  Completions oder Bedrock-Logs.
- Die Abuse-Detection-Doku beschreibt vollautomatische Klassifikation ohne
  Human Review; Benutzer-Inputs und Modell-Outputs werden laut dieser Doku
  nicht gespeichert und nicht mit Drittanbietern geteilt, nur anonymisierte
  Klassifikator-Metriken können geteilt werden.
- FAQ und DPA-/GDPR-Doku schließen die Produktgeltung von AWS-Vertrags- und
  Transfermechanismen grundsätzlich für AWS-Services; die AWS-Subprocessor-
  Seite ist öffentlich und regions-/serviceabhängig.
- Die FAQ sagt, dass von Bedrock verarbeitetes Customer Content verschlüsselt
  und at rest in der gewählten AWS-Region gespeichert wird; für den hier
  betrachteten Pfad wäre das `eu-central-1`.

**Blocker / No-Go-Risiken:**

- Die offiziellen Quellen lassen für diesen exakten Runtime-Pfad offen, wie
  provider-seitige Request-Metadaten, Service-Control-Logs, Support-Artefakte
  und Backups gehalten und gelöscht werden.
- Zwischen „doesn't store or log your prompts and completions“ und „content is
  encrypted and stored at rest in the AWS Region“ bleibt die konkrete
  Speicher-/Backup-Semantik für verarbeitete Inhalte nicht präzise genug
  geschlossen.
- Die Service Terms halten produktseitig Abuse-Detection- und
  Cross-Region-Inference-Mechaniken im Scope; für den MVP liegt keine
  account-spezifische Evidenz vor, dass alle Nebenpfade operativ sauber
  ausgeschlossen oder anders geregelt sind.

**Operativer Entscheid:** `nicht zulässig für Live-Nutzer`

#### D. Hetzner Cloud Server + lokaler `SQLite`-Event-Store – positiver Pilotpfad

**Offizielle Quellenbasis (Stand 2026-03-26):**

- Hetzner Docs: Locations (`https://docs.hetzner.com/cloud/general/locations`)
- Hetzner Docs: Backups/Snapshots overview
  (`https://docs.hetzner.com/cloud/servers/backups-snapshots/overview`)
- Hetzner Docs: Enabling Backups
  (`https://docs.hetzner.com/cloud/servers/getting-started/enabling-backups`)
- Hetzner Docs: Taking Snapshots
  (`https://docs.hetzner.com/cloud/servers/getting-started/taking-snapshots`)
- Hetzner Docs: Volumes overview
  (`https://docs.hetzner.com/cloud/volumes/overview`)
- Hetzner Docs: Data Protection at Hetzner
  (`https://docs.hetzner.com/general/company-and-policy/data-protection-at-hetzner`)
- Hetzner DPA (`https://www.hetzner.com/AV/DPA_en.pdf`)
- Hetzner approved subprocessors
  (`https://www.hetzner.com/AV/subunternehmer.pdf`)

**Belastbar geklärt:**

- `Hetzner Cloud Server` in `nbg1` ist ein konkreter Hosting-Pfad in
  Deutschland; Hetzner betreibt den Standort selbst.
- Die Hetzner-DPA ist produktnah verfügbar und kann im Kundenkonto
  abgeschlossen werden; sie gilt für die auf den Produkten verarbeiteten
  personenbezogenen Daten.
- Für EU-Serverstandorte werden Serverdaten laut Hetzner-Doku ausschließlich
  innerhalb der EU verarbeitet; Supportdienstleistungen erfolgen ebenfalls
  innerhalb der EU.
- Server-Backups sind optional und müssen aktiv eingeschaltet werden;
  Snapshots sind manuell initiierte Kopien. Beides bleibt im Pilotpfad
  deaktiviert bzw. verboten.
- Angehängte `Volumes` haben laut Produktdoku keine providerseitigen
  Backups/Snapshots; Server-Backups und Snapshots umfassen angehängte
  `Volumes` nicht.
- Die offizielle Subunternehmerliste benennt für den EU-Pfad
  `Hetzner Finland Oy` (Gebäudevermietung, technischer Support); US- und
  Singapur-Subunternehmer sind nur für diese Standorte relevant.
- Die DPA regelt Delete/Return nach Vertragsende auf Client-Anweisung; als
  Ausnahmen bleiben nur notwendige Backup-Kopien und gesetzliche
  Aufbewahrungspflichten. Für den gewählten Pfad werden deshalb keine
  Server-Backups oder Snapshots verwendet.

**Operativer Entscheidungsrahmen innerhalb dieses Hostingpfads:**

- `zulässig für Pilot` nur mit angehängtem `Hetzner Volume` + lokalem
  `SQLite`-Event-Store, ohne Server-Backups, ohne Snapshots und ohne externe
  Log-/Storage-Replikate.
- Nicht freigegeben ist der dateibasierte Event-Store auf demselben Host, weil
  TTL- und fallbezogene Löschung dort unnötige Rewrite-/Rotations-Nebenpfade
  öffnen würden.
- Vor Live-Start müssen täglicher TTL-Purge + `VACUUM` aktiv sein; Support-
  Tickets, Rescue- und VNC-Pfade dürfen keine Eventdaten aufnehmen.

#### Gesamtergebnis 2026-03-26

Von den in dieser Session belastbar geprüften LLM-Pfaden ist **kein** Pfad
`zulässig für Pilot`.

- `zulässig für Dev ohne reale Personendaten`: ja, für alle drei Pfade
- `zulässig für Pilot`: nein, für alle drei Pfade
- **Status vor erstem Live-Nutzer: derzeit kein freigabefähiger externer
  LLM-Providerpfad**

Das ist keine juristische Endabnahme, sondern eine operative Go/No-Go-Bewertung
für den MVP. Solange ein konkreter Produktpfad seine Subprocessor-, Löschpfad-
und Side-Artifact-Lage nicht belastbar schließt, bleibt der Pilot mit
Live-Nutzern gesperrt.

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
