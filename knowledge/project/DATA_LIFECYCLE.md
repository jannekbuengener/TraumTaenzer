# DATA_LIFECYCLE

Status: aktiv | Owner: Jannek Büngener | Zuletzt geprüft: 2026-03-26

Basis: PRIVACY_BY_DESIGN §2–§8, KERNEL_GUARD_CONTRACTS §4–§9,
TEXT_FIRST_RUNTIME_FLOW §8, DEPLOYMENT_ENVELOPE §4–§5,
SYSTEM_INVARIANTS P-1–P-4, GUARDRAILS_CONTENT_POLICY §7,
ARCHITECTURE_OVERVIEW §7

---

## 1. Zweck und Geltungsbereich

Dieses Dokument fixiert die minimale, belastbare Daten- und Lifecycle-Klammer
für den text-first Mono-MVP. Es vereint die in PRIVACY_BY_DESIGN, KERNEL_GUARD_CONTRACTS
und TEXT_FIRST_RUNTIME_FLOW verstreuten Lifecycle-Aussagen in einer Referenz.

Es beantwortet pro Datenkategorie:
- Persistenz-Status (`nie`, `transient`, `nur redigiert`, `erlaubt`)
- maximale Retention
- ob externe Übertragung stattfindet
- ob nutzer-seitig exportierbar

Es ist kein Datenbankschema, kein Migrationsplan, keine DPIA, kein Vendor-Entscheid.

---

## 2. Fünf Datenströme — die Grundtrennung

Alle Daten im Mono-MVP fallen in einen von fünf Strömen. Diese Ströme
dürfen nicht implizit verknüpft werden.

| Strom | Inhalt | Grundregel |
|---|---|---|
| **Content** | Nutzereingaben, Traumtexte, LLM-Output in der Session, konstruierter Prompt-Kontext | Ephemer. Niemals persistieren. Nur im Kernel-RAM während Verarbeitung. |
| **Safety-Signal** | Guard-Entscheidungen, Safe-State-Transitions, Session-Start/-End | Nur redigiert persistieren. Kein Content, kein Auslösetext. Zeitlich begrenzt. |
| **Betriebslog** | System-Fehler, technische Events ohne Safety-Bezug | Minimal persistieren. Kein Nutzerinhalt. Zeitlich begrenzt. |
| **Access** | Account-/Kontaktdaten für Zugang oder Pilot-Organisation (falls vorhanden) | Strikt getrennt von Runtime und Event-Log. Nur minimal für Zugang oder Pilotbetrieb. |
| **Config / Gov** | Safeword-Konfiguration, Kernel-Regeln, Repo-Artefakte, Agent-Trust-Events | Server-seitig oder im Repo. Kein Personenbezug. Kein Nutzer-Content. |

**Trennungspflicht (PRIVACY §3):** Session-Inhalte, Safety-Events,
Nutzungsmetadaten und Access-Daten werden nicht im selben Datensatz gespeichert.
Kein Linking ohne expliziten, dokumentierten Zweck.

---

## 3. Datenklassen-Matrix

Vollständige Übersicht aller Datenkategorien des text-first MVP.

| Datenkategorie | Strom | Persistenz-Status | Max. Retention | Externe Übertragung | Nutzer-Export |
|---|---|---|---|---|---|
| **Nutzereingaben / Traumtexte** | Content | `nie` | — | Nein¹ | Nein (nicht vorhanden) |
| **Konstruierter Prompt-Kontext** | Content | `nie` | — | Ja → LLM-Provider (TB-2)² | Nein |
| **LLM-generierter Text (vor Output-Guard)** | Content | `nie` | — | Kommt von LLM-Provider² | Nein |
| **Constraint Flags** | Content | `transient` | Session-Ende | Nein | Nein |
| **Guard-Entscheidungen** (`INPUT_GUARD_RESULT`, `OUTPUT_GUARD_RESULT`) | Safety-Signal | `nur redigiert` | 90 Tage | Nein | Nein³ |
| **Safe-State-Übergänge** (`SAFE_STATE_TRANSITION`) | Safety-Signal | `nur redigiert` | 90 Tage | Nein | Nein³ |
| **Session-Start** (`SESSION_STARTED`) | Betriebslog | `erlaubt` | 90 Tage | Nein | Ggf.⁴ |
| **Session-Ende** (`SESSION_ENDED`) | Betriebslog | `erlaubt` | 90 Tage | Nein | Ggf.⁴ |
| **System-Fehler** (`SYSTEM_ERROR`) | Betriebslog | `erlaubt` | 30 Tage | Nein | Nein |
| **Safeword-Konfiguration** | Config | `server-seitig` | Solange aktiv | Nein | Nein |
| **Kernel-Regeln / Guard-Konfiguration** | Config | `server-seitig` | Solange aktiv | Nein | Nein |
| **Account-/Kontaktdaten** (falls vorhanden) | Access⁵ | `erlaubt, minimal` | Solange Konto aktiv + 30d | Nein | Ja |
| **Agent-Trust-Events** (Governance/Repo) | Config / Gov | `Repo-versioniert` | Unbegrenzt (Governance) | Nein | n.a.⁶ |

**Legende Persistenz-Status:**
- `nie` — kein Persistieren unter keinen Umständen; nur transienter RAM
- `transient` — existiert nur während aktiver Session im Kernel-RAM; kein Schreiben
- `nur redigiert` — darf nur als enum/flag/timestamp persistiert werden; kein Freitext, kein Content
- `erlaubt` — minimale Metadaten dürfen persistiert werden; Inhaltsfeldverbot gilt weiterhin
- `server-seitig` — liegt in Kernel-Konfiguration; keine Nutzerdaten-Semantik

**Fußnoten:**
1. Nutzereingaben gehen nicht direkt an den LLM-Provider. Sie werden durch den Kernel zu einem Prompt-Kontext verarbeitet; nur der Kontext passiert TB-2.
2. Prompt-Kontext und LLM-Output passieren TB-2 (Server ↔ LLM-Provider). Was der Provider daraus loggt, unterliegt dessen Datenpolitik — offener DPA-Prüfpunkt (PRIVACY §9).
3. Safety-Signal-Daten sind ggf. im Rahmen von Auskunftsrechten relevant; gesondert zu prüfen bei Produktionsstart (PRIVACY §8).
4. Session-Start/-End-Timestamps sind Nutzungsmetadaten; Export-Pflicht bei Produktisierung prüfen.
5. Account-Daten liegen außerhalb der text-first Runtime und existieren im MVP-Piloten mit namentlich bekannter Gruppe ggf. gar nicht. Die Zeile ist vorsorglich für einen minimalen Zugangs- oder Kontaktpfad angelegt.
6. Agent-Trust-Events sind Governance-Protokolle des Projekts, keine Nutzerdaten.

---

## 4. Event-Typen-Matrix

Zwei klar getrennte Event-Domains. Keine Verwechslung, kein Cross-Linking.

### 4.1 Runtime-Events des Systems (Kernel → Event-Log)

Definiert in KERNEL_GUARD_CONTRACTS §4 und TEXT_FIRST_RUNTIME_FLOW §8.

| Event-Typ | Persistierbar? | Pflichtfelder (wenn persistiert) | Absolut verbotene Felder |
|---|---|---|---|
| `SESSION_STARTED` | Ja | session_id (pseudonym), timestamp | Nutzer-ID (nicht-pseudonym), Startinhalt |
| `SESSION_ENDED` | Ja | session_id, timestamp, end_type (enum) | Ursachentext, Nutzerinhalt |
| `USER_INPUT_RECEIVED` | **Nein** (nur Kernel-RAM) | — | Eingabetext darf Log nie erreichen |
| `INPUT_GUARD_RESULT` | Ja (redigiert) | session_id, timestamp, decision (enum), guard_category (enum) | Auslösetext, Nutzerformulierung |
| `LLM_OUTPUT_RECEIVED` | **Nein** (nur Kernel-RAM) | — | LLM-Output darf Log nie erreichen |
| `OUTPUT_GUARD_RESULT` | Ja (redigiert) | session_id, timestamp, decision (enum), violation_type (enum, nur bei BLOCK) | Ausgabetext, LLM-Output |
| `SAFE_STATE_TRANSITION` | Ja (redigiert) | session_id, timestamp, from_state, to_state, trigger_event (enum) | Ursachentext, Nutzerinhalt |
| `SYSTEM_ERROR` | Ja | session_id, timestamp, error_code, component (enum) | Nutzerinhalt, LLM-Prompt/-Output |

**Regel für alle Runtime-Events:** Kein Freitext. Alle inhaltsbezogenen Felder sind verboten.
Nur Enums, Zeitstempel und pseudonyme Session-IDs.

### 4.2 Governance-Events des Projekts (Agent-Trust-Ledger)

Definiert in `knowledge/agent_trust/decision_event.schema.yaml`.
Diese Events dokumentieren Entscheidungen von KI-Agenten im Entwicklungsprozess.
Sie sind **vollständig getrennt** von Runtime-Events und enthalten keinen Nutzerinhalt.

| Feld | Bedeutung |
|---|---|
| `timestamp_utc` | Zeitpunkt der Governance-Entscheidung |
| `actor` | Handelnder Agent (z. B. „claude", „codex", „gemini") |
| `action` | Was getan wurde (z. B. „create", „review", „approve") |
| `scope` | Betroffenes Artefakt oder Bereich |
| `evidence` | Begründung oder Commit-Referenz |

**Abgrenzung:** Diese Events sind Repo-Artefakte. Sie enthalten keine Nutzerdaten,
keine Session-IDs, keine Runtime-Ereignisse. Sie sind nicht Teil des System-Event-Logs.

### 4.3 MVP-Entscheidung: Session-ID und Pseudonymisierung

Die bisher nur rahmenhafte Pseudonymisierungslogik wird für den Mono-MVP wie folgt
konkretisiert:

| Punkt | Entscheidung |
|---|---|
| **Session-ID-Typ** | Pro Session neu erzeugte, opaque Zufalls-ID. Kein semantischer Anteil, keine Ableitung aus E-Mail, Nutzername, Einladung, Gerät, IP oder Zeitstempel. |
| **Zweck** | Darf ausschließlich Runtime-Ereignisse derselben Session korrelieren. Kein Nutzerprofil, kein Cross-Session-Identifier. |
| **Erlaubte Orte** | Aktive Client-/Server-Session über TB-1, Kernel-RAM, redacted Runtime-Events in Event-Storage. |
| **Verbotene Orte** | TB-2 / LLM-Provider, Prompt-Kontext, Access-/Account-Datensätze, Analytics-/Profiling-Daten, URLs, persistente Client-Speicher, Support-/Debug-Logs mit Identität. |
| **Access-/Account-Bezug** | Im MVP gibt es standardmäßig keinen persistenten Session↔Account-Link. Falls ein minimaler Zugangs- oder Kontaktpfad existiert, bleibt er außerhalb der Runtime und darf nicht still mit Event-Storage gejoint werden. |
| **Erlaubte Korrelation** | Nur für einen expliziten, dokumentierten Minimalzweck in einem separaten Ops-Pfad, nicht als Default und nicht als Vorratsmapping. |
| **Re-Entry** | `PAUSED` oder `GUARD_BLOCK` innerhalb derselben Session behalten dieselbe `session_id`. `EXIT`, `EXTERNAL_REFERRAL`, Prozess-Neustart oder neue Session erzeugen eine neue `session_id`. |
| **Debugging** | Session-ID darf genau eine pseudonyme Runtime-Spur eingrenzen. Verboten bleibt jede Anreicherung mit E-Mail, Nutzer-ID, Einladungsdaten, IP, Prompt, Output oder Nutzertext. |

---

## 5. Redaction-vor-Persistenz — operative Entscheidungslogik

Erdet PRIVACY §2 (Redaction-first-Prinzip) auf Feldebene.

```
Soll ein Datenpunkt persistiert werden?
  │
  ├─ Enthält er Nutzertext, Trauminhalt, Reflexionstext, LLM-Output?
  │      → Nie persistieren. Kein Redaction-Weg für Content.
  │
  ├─ Enthält er ein Safety-Signal (Guard-Entscheidung, State-Transition)?
  │      → Nur als enum persistieren.
  │        Kein Freitext. Kein Auslöseinhalt. Kein Content-Kontext.
  │
  ├─ Ist es ein technisches Betriebsereignis (Session-Start/-End, Systemfehler)?
  │      → Minimal persistieren: Zeitstempel + enum-Felder.
  │        Kein Nutzerinhalt in Error-Messages oder Stack Traces.
  │
  ├─ Ist es Konfiguration (Safeword, Kernel-Regel)?
  │      → Server-seitig halten. Keine Nutzerdaten-Semantik.
  │
  └─ Ist unklar, welcher Kategorie es gehört?
         → Nicht persistieren. Erst Kategorie klären, dann entscheiden.
```

**Ergänzungsregel für externe Übertragung (TB-2):**
Bevor Daten die Servergrenze passieren (→ LLM-Provider):

```
Ist der Inhalt rohes Nutzertext?
  → Nein. Nur vom Kernel konstruierter, redacted Prompt-Kontext.

Enthält der Prompt-Kontext direkte Nutzeridentität?
  → Nie. Pseudonymisierung und Minimierung vor TB-2-Übergang.

Ist der DPA des Providers geprüft?
  → Für Produktion: Pflicht (SYSTEM_INVARIANTS P-4).
  → Für lokales Dev ohne reale Personendaten: nicht zwingend.
```

---

## 6. Retention und Löschung auf Rahmenebene

Basiert auf PRIVACY_BY_DESIGN §6–§7 und KERNEL_GUARD_CONTRACTS §9.

| Datenkategorie | Retention | Lösch-Trigger | Löschpfad-Status |
|---|---|---|---|
| Session-Inhalte | Keine Persistenz | n.a. | n.a. (nie persistiert) |
| Constraint Flags | Session-Ende | Session-Ende oder EXIT/EXTERNAL_REFERRAL | In-Memory, automatisch |
| Safety-Event-Logs (`INPUT_GUARD_RESULT`, `OUTPUT_GUARD_RESULT`, `SAFE_STATE_TRANSITION`) | Max. 90 Tage | Ablauf der Frist | Automatische Löschung; noch zu implementieren |
| Session-Metadaten (`SESSION_STARTED`, `SESSION_ENDED`) | Max. 90 Tage | Ablauf der Frist | Automatische Löschung; noch zu implementieren |
| System-Fehler-Logs (`SYSTEM_ERROR`) | Max. 30 Tage | Ablauf der Frist | Automatische Löschung; noch zu implementieren |
| Account-Daten (falls vorhanden) | Solange Konto aktiv + 30 Tage nach Kündigung | Nutzerkündigung oder manuelle Löschung | Noch nicht implementiert |
| Agent-Trust-Events | Unbegrenzt (Governance) | Explizite Governance-Entscheidung nötig | Repo-Git-History |

**Grundsatz:** Kein Retention-Enforcement = kein Persistieren.
Retention-Frist muss definiert und technisch erzwingbar sein, bevor Daten in
einem Speicher landen (PRIVACY §7: „Keine Datenpersistenz ohne definierten Löschpfad").

### Enforcement-Bewertung gegen die aktuelle Zielinfrastruktur (Stand 2026-03-26)

**Belastbar festgelegt sind derzeit nur:**

- Mono-MVP als ein Serverprozess mit in-process `Event-Log-Writer`
- append-only, redacted, content-free Runtime-Events hinter TB-3
- RAM-only Session-Content ohne Persistenzpfad

**Nicht belastbar festgelegt sind derzeit:**

- konkretes Pilot-Event-Storage-Backend (`lokale Datei` vs. `minimales DB-Backend`)
- konkreter Hosting-Pfad, auf dem dieses Event-Storage laufen würde
- technische Retention-Durchsetzung für reale Guard-/Safety-Events,
  Session-Metadaten und `SYSTEM_ERROR`
- Backup-/Replica-/Support-/Nebenlogik des später gewählten Storage-Pfads

**Operativer Befund:** Für Dev ohne reale Personendaten bleibt der Canon
ausreichend. Für Pilot oder sonstige Live-Nutzer-Nutzung ist die fehlende
Benennung des konkreten Event-Storage-/Hosting-Pfads ein Blocker, weil damit
90-/30-Tage-Retention, automatische Löschung und Nebenartefakte nicht
belastbar verifiziert werden können.

---

## 7. Export-Scope für den Mono-MVP

**Nüchterne Bestandsaufnahme:** Im text-first MVP mit Default-Ephemerität gibt es
für die meisten Nutzer faktisch keine exportierbaren Session-Inhalte, weil
Session-Content nie persistiert wird.

| Datenkategorie | Im Nutzer-Export? | Begründung |
|---|---|---|
| Session-Inhalte | Nein | Nie persistiert; kein Exportgegenstand vorhanden |
| Safety-Event-Logs | Nicht im Standard-Export | Betriebsdaten; Auskunftsrechts-Relevanz bei Produktionsstart prüfen (PRIVACY §8) |
| Session-Metadaten | Nicht im Standard-Export des MVP | Im MVP nur pseudonyme Betriebsmetadaten über `session_id`; kein Default-Zuordnungspfad zu Account-/Access-Daten. Etwaige Auskunftsrelevanz bei Produktionsstart gesondert prüfen |
| Account-Daten | Ja (wenn vorhanden) | DSGVO Art. 20 Portabilität; maschinenlesbares Format (JSON) als Baseline |
| Agent-Trust-Events | Nein | Keine Nutzerdaten; Governance-Protokolle des Projekts |

**Optionales Nutzer-Journal (falls implementiert):**
Wenn Nutzer Session-Inhalte auf expliziten Wunsch selbst speichern können,
muss dieser Inhalt vollständig exportierbar und löschbar sein (PRIVACY §8).
Diese Funktion ist kein MVP-Feature — sie ist als Konzept vorgemerkt.

**Folge für Löschung:** Solange kein separater, dokumentierter Zuordnungspfad
zwischen Account-/Access-Daten und Runtime-Events existiert, werden pseudonyme
Runtime-Events nicht per Konto-Lookup gelöscht, sondern ausschließlich über die
Retention- und Löschlogik des Event-Storage.

---

## 8. Was bewusst nicht festgelegt wird

| Nicht festgelegt | Warum offen |
|---|---|
| Konkretes Storage-Backend (DB, Datei, Cloud) | Repo-weit bleibt es provider-agnostisch; vor erstem realen Event ist es aber nicht offen. Ein konkreter Pilot-Event-Storage-Pfad muss benannt sein, sonst bleibt Live-Nutzung blockiert |
| Datenbankschema oder Tabellenstruktur | Zu früh; folgt aus Implementierungsentscheid |
| LLM-Provider-DPA-Abschluss | Offener Prüfpunkt (PRIVACY §9); Pflicht vor Produktionsstart |
| Account-/IAM-Architektur | Pilot mit bekannter Gruppe; keine offene Registrierung im MVP |
| Backup- und Disaster-Recovery-Logik | Kein großes DR-Design nötig; die Backup-/Replica-/Nebenlogik des konkret gewählten Event-Storage-Pfads muss vor Live-Nutzung trotzdem benannt sein. Offen = Blocker |
| Vollständige Export-/Auskunftsbehandlung pseudonymer Runtime-Events | Bleibt offen bis Produktionsstart; hängt an separater Rechts-/Ops-Bewertung und nicht an einem Default-Join |
| Export-Format-Implementierung | Noch kein persistierter Nutzerinhalt; Format-Entscheid wenn nötig |
| Subprozessor-Liste (vollständig) | Offen; zusammenzustellen bei Produktionsstart (PRIVACY §9) |

---

## 9. Operativer Kurz-Check für neue Datenflüsse

Vor jedem neuen Datenfluss, Log-Typ oder Persistenz-Entscheid:
**Alle Fragen müssen mit Nein beantwortet werden.**

| # | Frage | Bei Ja |
|---|---|---|
| 1 | Enthält dieser Datenpunkt Nutzertext, Trauminhalt, Reflexionstext oder LLM-Output? | Nie persistieren — kein Redaction-Weg |
| 2 | Wird hier Content mit Safety-Signal oder Nutzungsmetadaten im selben Datensatz verknüpft? | Trennungspflicht verletzt — aufteilen oder nicht anlegen |
| 3 | Fehlt ein definierter Löschpfad für diesen Datenpunkt? | Nicht persistieren, bis Löschpfad definiert ist |
| 4 | Passiert hier ein Freitext-Feld die Persistenzgrenze (statt enum/flag/timestamp)? | Redaction-Verletzung — auf enum reduzieren oder weglassen |
| 5 | Fließen hier reale Personendaten an einen externen Provider ohne geprüfte DPA? | P-4-Verletzung — stoppen bis DPA vorliegt |
| 6 | Ist unklar, zu welchem der fünf Datenströme dieser Datenpunkt gehört? | Nicht persistieren bis Zuordnung geklärt |
| 7 | Wird hier ein Safety-Signal mit einer Nutzeridentität verknüpft (statt pseudonymer Session-ID)? | Privacy-Verletzung — Verknüpfung entfernen |
| 8 | Könnte dieser Datenpunkt mit dem Agent-Trust-Ledger verwechselt werden? | Domäne klären — Runtime-Events und Governance-Events sind getrennte Schemas |
| 9 | Entsteht hier eine stille Session↔Account-/Access-Verknüpfung ohne dokumentierten Minimalzweck? | Privacy-Verletzung — Join entfernen oder Zweck explizit entscheiden |
