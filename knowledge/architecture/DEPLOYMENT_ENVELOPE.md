# DEPLOYMENT_ENVELOPE

Status: aktiv | Owner: Jannek Büngener | Zuletzt geprüft: 2026-03-26

Basis: ARCHITECTURE_OVERVIEW §2–§9, KERNEL_GUARD_CONTRACTS §2–§10,
TEXT_FIRST_RUNTIME_FLOW §2–§8, SYSTEM_INVARIANTS A-1–A-4, P-1–P-4,
PILOT_READINESS §3.4–§3.5, SYSTEM.CONTEXT §Constraints

---

## 1. Zweck und Geltungsbereich

Dieses Dokument fixiert den minimalen, ehrlichen Deployment-Rahmen für den
text-first Mono-MVP. Es beantwortet:

- welche Laufzeitrollen es gibt und was jede Rolle verantwortet
- welche Trust Boundaries existieren und was sie schützen
- wo Secrets leben dürfen und wo absolut nicht
- was bei Provider-, Guard-, Storage- oder Prozessfehlern passiert
- wie fail-closed für den MVP auf Betriebsebene aussieht
- wie Dev, Pilot und produktionsnaher Betrieb voneinander getrennt werden

Es ist:
- kein Infrastrukturplan, kein IaC-Template, kein Cloud-Entscheid
- kein Code, kein Container-Setup, kein Kubernetes-Design
- keine Scale-, HA- oder Multi-Region-Spezifikation
- kein Ersatz für KERNEL_GUARD_CONTRACTS oder TEXT_FIRST_RUNTIME_FLOW

Es schließt die Lücke zwischen dem logischen Komponentenmodell
(ARCHITECTURE_OVERVIEW §3) und dem späteren tatsächlichen Systemaufbau.

---

## 2. Mono-MVP-Topologie: Der ehrlichste Schnitt

Der text-first MVP läuft als **ein Serverprozess**. Kein Microservices-Split,
keine separaten Guard-Services, kein verteilter Kernel.

```
[Client / UI]
     |  HTTP(S)
     v
[Server-Prozess]
  ├── Kernel          (Session-State im RAM, Orchestrierung)
  ├── Guard Layer     (Input- + Output-Guard, in-process)
  ├── Event-Log-Writer (append-only, redacted)
  └── LLM-Adapter     (outbound HTTP → externer Provider)
     |  HTTP(S) / API
     v
[LLM-Provider]         (extern, hinter Trust Boundary TB-2)
     |
[Event-Storage]        (lokal oder minimal extern, nur redacted Events)
```

**Begründung für den Mono-Schnitt:**
- Solo-Maintainer-Realität: kein Betrieb verteilter Dienste ohne Notwendigkeit
- Guards müssen Kernel-synchron und deterministisch sein; in-process ist
  einfacher korrekt als über Netzwerk
- Session-State ist ephemer und RAM-only; kein Shared-State-Problem
- Der Schnitt ist ehrlich gegenüber dem aktuellen Reife- und Ressourcenstand

Erweiterungen (separater Guard-Service, Sidecar-Log, Voice-Adapter) können
addiert werden, wenn ein belegter technischer Bedarf entsteht. Nicht vorher.

---

## 3. Laufzeitrollen und Verantwortungen

### 3.1 Client / UI

| Dimension | Inhalt |
|---|---|
| **Was es ist** | Browser-App, CLI oder vergleichbares Front-End |
| **Verantwortung** | Nutzereingaben entgegennehmen, Ausgaben darstellen, Exit jederzeit zugänglich halten |
| **Hält** | Keine Session-State, keine Logs, keine Secrets |
| **Darf nicht** | Safety-Entscheidungen treffen, Session-State halten, Safeword verarbeiten, LLM direkt ansprechen |
| **Erhält vom Server** | Nur formatierte Ausgabe und verfügbare Aktions-Signale (z. B. EXIT_AVAILABLE) |
| **Übergibt an Server** | Nur rohe Nutzereingabe + pseudonyme Session-ID; keine Nutzeridentität |

Der Client ist stateless. Sein Absturz verliert keine sicherheitskritischen Daten.

---

### 3.2 Server-Prozess (Kernel + Guards + Adapter + Log-Writer)

Der Server-Prozess ist die einzige Instanz mit Safety-Entscheidungsgewalt.

| Sub-Rolle | Verantwortung | Darf nicht |
|---|---|---|
| **Kernel** | Session-State im RAM halten, Guard-Aufrufe orchestrieren, Safe-State-Übergänge auslösen, Prompt konstruieren | LLM direkt ansprechen ohne Guard, Inhalte persistieren, Safety per Inference entscheiden |
| **Guard Layer** | Input/Output regelbasiert und deterministisch prüfen, Entscheidungsklasse zurückgeben | LLM aufrufen, Session-State ändern, Logging auslösen, Inference nutzen |
| **LLM-Adapter** | Strukturierten Prompt-Kontext an externen Provider senden, generierten Text zurückgeben | Session steuern, Safety entscheiden, Logs schreiben, Persistenz veranlassen, Prompt selbst konstruieren |
| **Event-Log-Writer** | Redacted Events append-only schreiben | Nutzertext, LLM-Output, Auslösetext oder Content in Events aufnehmen |

**Session-State ist RAM-only.** Er wird nicht persistiert und nicht zwischen Prozess-Neustarts übertragen. Das ist keine Einschränkung — es ist Privacy-by-Default (SYSTEM_INVARIANTS P-1).

---

### 3.3 LLM-Provider (extern)

| Dimension | Inhalt |
|---|---|
| **Was es ist** | Externer API-Dienst zur Textgenerierung |
| **Erhält** | Nur den vom Kernel konstruierten Prompt-Kontext (kein Rohnutzertext, keine Session-ID, keine Guard-Entscheidungen, kein Safeword) |
| **Verantwortet nicht** | Session-State, Safety-Entscheidungen, Persistenz, Logging |
| **Vertrauensstufe** | Untrusted — jede Ausgabe läuft durch den Output-Guard, bevor sie die UI erreicht |
| **Provider-Wechsel** | Muss möglich bleiben, ohne Kernel- oder Guard-Logik zu ändern (SYSTEM_INVARIANTS A-4) |

---

### 3.4 Event-Storage

| Dimension | Inhalt |
|---|---|
| **Was es ist** | Append-only Speicher für redacted System-Events |
| **Enthält** | Nur: session_id (pseudonym), timestamp, event_type, Entscheidungs-/Fehler-Enums — kein Content |
| **Retention** | Guard-/Safety-Events: max. 90 Tage; System-Error-Logs: max. 30 Tage (→ KERNEL §9) |
| **Für Pilot** | Kann lokale Datei oder minimales DB-Backend sein — kein Cloud-Service zwingend |

---

## 4. Trust Boundaries

Vier explizite Trust Boundaries für den Mono-MVP:

| Grenze | Trennt | Was darf die Grenze passieren | Was darf nicht passieren |
|---|---|---|---|
| **TB-1** | Client ↔ Server | Nutzereingabe (roh, transient), formatierte Ausgabe, Session-ID (pseudonym), Aktions-Signale | Session-State, Secrets, Guard-Entscheidungen, Safety-Events, LLM-Prompt oder -Output |
| **TB-2** | Server ↔ LLM-Provider | Konstruierter Prompt-Kontext (redacted, kein Rohtext), generierter Text (transient, vor Guard) | Session-ID, Nutzeridentität, Guard-Entscheidungen, Safeword-Konfiguration, Safety-Event-Daten |
| **TB-3** | Server ↔ Event-Storage | Redacted Events (Typ, Zeitstempel, Enums, pseudonyme Session-ID) | Nutzertext, LLM-Output, Auslösetext, Content-Kontext, direkte Nutzeridentität |
| **TB-4** | Config/Secrets ↔ Prozess | Secrets sind nur dem Server-Prozess zugänglich (env var oder Secret-Store) | Secrets ins Client-Bundle, in Logs, in Event-Storage, in LLM-Prompts, ins Repo |

**TB-2 ist die kritischste Grenze:** Hier verlässt Inhalt den eigenen Kontrollbereich und geht an einen externen Provider. Was TB-2 passiert, muss vor dem Kernel-Call vollständig konstruiert und redacted sein. Kein Rohnutzertext, keine Session-ID, keine Safety-Informationen.

### Minimale Provider-Capability-Matrix

Die Adapter-Grenze bleibt nur dann ehrlich provider-agnostisch, wenn der MVP von
externen Providern nur die kleinste notwendige Oberfläche erwartet.

| Capability | Status im MVP | Bedeutung |
|---|---|---|
| **Stateless text-in / text-out über Server-API** | erforderlich | Der Adapter sendet konstruierte Anfrage, erhält Text zurück; kein externer Session-State |
| **Server-seitige Auth per Secret** | erforderlich | Zugangsdaten liegen nur im Server-Prozess (TB-4), nie im Client |
| **Klare Timeout-/Fehleroberfläche** | erforderlich | Provider-Fehler müssen als technische Fehler behandelbar sein, nicht als inhaltliche Sonderfälle |
| **Fehler-Normalisierung auf kanonische Fehler** | erforderlich | Adapter mappt Provider-Fehler auf `ERROR_FAIL_CLOSED` / `SYSTEM_ERROR`, nicht auf provider-spezifische Runtime-Zweige |
| **Streaming-Ausgabe** | optional | Nur zulässig, wenn jeder Chunk weiterhin vollständig hinter Output-Guard und Kernel-Kontrolle bleibt |
| **Tool-/Function-Calling** | optional, nicht erforderlich | Kein MVP-Bedarf; darf nicht in Kernel-Verantwortung oder Safety-Logik einbrechen |
| **Provider-seitiger Conversation-State / Threads / Memory** | verboten im MVP | Session-State bleibt im Kernel-RAM; keine externe Gedächtnis- oder Thread-Abhängigkeit |
| **Dokumentierte Retention / Datennutzung / Region / Subprocessor-Lage** | erforderlich vor Live-Nutzer | Kein technisches Nice-to-have, sondern Deployment-Gate vor realem Personenbezug |

**Wichtig:** Die letzte Zeile ist keine Provider-Auswahlhilfe, sondern eine
harte Einsatzgrenze. Ohne diese Klärung bleibt ein Provider auf Dev ohne reale
Personendaten beschränkt.

---

## 5. Secrets-Disziplin

| Secret | Erlaubter Ort | Verbotene Orte |
|---|---|---|
| **LLM-API-Key** | Server-Prozess: Umgebungsvariable oder Secret-Store | Client, Logs, Event-Storage, Repo, LLM-Prompt, Git-History |
| **Safeword-Konfiguration** | Server-seitig in Kernel-Config | Client-Bundle, Logs, Event-Storage, LLM-Adapter-Payload |
| **Session-IDs** | Pseudonym, RAM-only im Kernel | Nicht mit Nutzeridentität verknüpft in Storage |
| **Nutzeridentität** | Falls vorhanden: separater Auth-Layer, nicht im Kernel-Session-State | Event-Log (kein Inhaltsevent darf Nutzeridentität tragen), LLM-Adapter, Client-State |

**Operative Regel:** Bevor ein neuer Konfigurationswert angelegt wird, Frage stellen: Kann dieser Wert in einem Log landen? Kann er in einem Prompt landen? Wenn Ja: als Secret behandeln oder nicht anlegen.

Gitleaks scannt jeden PR (SYSTEM.CONTEXT §CI). Das ist die technische Durchsetzung der Secret-Disziplin im Repo. Runtime-Secrets liegen außerhalb des Repos.

---

## 6. Fail-Closed im Deployment-Kontext

Ergänzt KERNEL_GUARD_CONTRACTS §10 um die Betriebsebene.

| Fehlerszenario | Systemverhalten |
|---|---|
| **LLM-Provider nicht erreichbar / Timeout** | LLM-Adapter gibt Fehler zurück → Output Guard erhält keinen Output → `ERROR_FAIL_CLOSED` → Kernel → `EXIT` + `NEUTRAL_ERROR_FAIL_CLOSED_RESPONSE`; kein Retry ohne Kernel-Entscheidung |
| **Guard-Modul wirft Fehler / Timeout** | `ERROR_FAIL_CLOSED` → Kernel → `EXIT`; kein LLM-Call; neutrale Fehlermeldung |
| **Server-Prozess-Absturz / Restart** | Client sieht Verbindungsabbruch; Session-State geht verloren (ephemer by design, kein Datenverlust); nach Neustart beginnt neue Session bei ENTRY |
| **Event-Storage-Schreibfehler** | Logging-Fehler blockiert keine Kernel-Entscheidung (KERNEL §10); Fehler intern vermerken; Session läuft weiter; Logging-Ausfall-Sequenz für Nachverfolgung protokollieren |
| **Config fehlt (kein API-Key)** | Server-Prozess startet, aber LLM-Adapter-Calls schlagen fehl; `ERROR_FAIL_CLOSED` auf LLM-Aufruf; predefined Kernel-Pfade (ENTRY, EXIT, Safe States) bleiben funktionsfähig |
| **Widersprüchliche oder fehlende Constraint-Flags** | Restriktivste Regel gewinnt (KERNEL §10); wenn nicht auflösbar → `EXIT` |
| **TB-2 gibt invaliden Output zurück (non-text, malformed)** | Output Guard kann nicht prüfen → `ERROR_FAIL_CLOSED` → `EXIT`; kein ungeprüfter Inhalt an UI |

**Deployment-Fail-Closed-Priorität (Ergänzung zu KERNEL §10):**
```
Prozess-Neustart (mit sauberem ENTRY) > degradierter Betrieb > kein Betrieb
```
Degradierter Betrieb bedeutet: ENTRY / EXIT / Safe-State-Pfade funktionieren; LLM-Pfade nicht. Das ist akzeptabel. Kein Betrieb mit defekten Guards ist es nicht.

### no-provider / degraded mode / provider failure

| Szenario | Minimal zulässiges Verhalten |
|---|---|
| **No-provider** | Kein freigeschalteter Provider oder kein konfigurierter API-Zugang: predefined Kernel-Pfade wie `ENTRY`, `EXIT`, `PAUSED`, `EXTERNAL_REFERRAL` und neutrale Fehlermeldungen bleiben nutzbar; `REFLECTION` läuft nicht |
| **Degraded mode** | Bedeutet ausschließlich: sichere predefined Kernel-Pfade bleiben nutzbar, LLM-Pfade nicht. Keine Guard-Lockerung, kein alternativer Safety-Modus, kein verändertes Entscheidungsverhalten |
| **Provider failure** | Timeout, API-Fehler, ungültiger Output oder fehlender API-Key werden auf `ERROR_FAIL_CLOSED` normalisiert und enden in `EXIT`; kein stiller Retry, kein stiller Fallback auf anderen Provider |
| **DPA ungeklärt** | Kein Live-Nutzer-Verkehr. Das ist kein Runtime-Fallback, sondern ein Deployment-Gate gemäß `PROVIDER_DPA_INPUT_MATRIX.md` und SYSTEM_INVARIANTS P-4 |

**Invariante:** Degraded mode ist kein „weniger sicherer Betrieb". Wenn Guards
nicht korrekt arbeiten oder der Providerpfad nicht sauber fail-closed endet,
gibt es keinen degradierten Modus – nur `EXIT` oder kein Betrieb.

---

## 7. Umgebungstrennung: Dev / Pilot / Produktionsnah

Die Topologie bleibt in allen drei Umgebungen identisch. Was sich unterscheidet: Provider-Konfiguration, Secret-Management-Rigor und DPA-Status.

| Dimension | Dev (lokal) | Pilot (kontrolliert) | Produktionsnah |
|---|---|---|---|
| **LLM-Provider** | Mock, lokales Modell oder kostenpflichtiger API-Test ohne reale Nutzerdaten | Echter externer Provider | Echter Provider |
| **DPA-Status** | Nicht erforderlich (keine realen Personendaten) | Erforderlich vor erstem Nutzerkontakt; `PROVIDER_DPA_INPUT_MATRIX.md` ausgefüllt und positiv bewertet | Erforderlich und geprüft; Matrix weiterhin aktuell |
| **Secret-Management** | Lokale `.env`-Datei (nie committen; Gitleaks fängt Fehler) | Env var in isolierter Pilot-Umgebung; kein Sharing mit Dev | Secret-Store; Rotation dokumentiert |
| **Event-Storage** | Lokale Datei, kein Retention-Enforcement nötig | Retention-Enforcement ab Erstem realen Event (90/30 Tage) | Retention automatisiert und auditierbar |
| **Nutzerdaten** | Keine echten Personendaten | Kleine bekannte Pilotgruppe; explizit informiert (PILOT_READINESS §3.7) | Geregelter Onboarding-Flow |
| **Session-Content** | Ephemer (wie immer) | Ephemer; zusätzliche Prüfung, dass kein Content in Logs landet | Ephemer; technisch erzwungen |
| **Guard-Verhalten** | Identisch zu Pilot/Prod — Guard-Logik hat keine Umgebungs-Modi | Identisch | Identisch |
| **Fail-Closed** | Identisch — kein Dev-Modus mit geschwächten Guards | Identisch | Identisch |

**Invariante für alle Umgebungen:** Guard-Logik, Kernel-Entscheidungen und fail-closed-Verhalten haben keine Umgebungs-Modi. Es gibt kein `DEBUG_SKIP_GUARDS=true`. Wer Guards in Dev deaktiviert, testet ein anderes System.

### Umgebungswechsel-Checkliste (Pilot-Start)

Vor erstem realen Nutzerkontakt — zusätzlich zu PILOT_READINESS §3:

- [ ] `PROVIDER_DPA_INPUT_MATRIX.md` für den konkret genutzten Providerpfad ausgefüllt und positiv bewertet
- [ ] Secrets nicht in `.env` im Repo-Verzeichnis, sondern in isolierter Pilot-Config
- [ ] Event-Storage-Retention-Enforcement aktiv (90 Tage Guard-Events, 30 Tage Errors)
- [ ] Kein Nutzerinhalt-Logging durch manuellen Smoke-Test bestätigt
- [ ] Fail-Closed-Pfad bei Provider-Ausfall manuell getestet
- [ ] Session-Content-Ephemerität bestätigt: Prozess-Neustart löscht Session-State

---

## 8. Was dieser Rahmen nicht festlegt

| Nicht festgelegt | Begründung |
|---|---|
| Konkrete Cloud-Plattform, Hosting-Anbieter | Provider-Agnostik (SYSTEM_INVARIANTS A-4); zu früh für Commitments |
| Container-Runtime, Orchestrierung (Docker, k8s) | Kein belegter MVP-Bedarf; Mono-Prozess reicht |
| Auth-/IAM-System für Endnutzer | MVP-Pilot mit bekannter Gruppe; kein offenes Registrierungs-System |
| Monitoring-/Alerting-Infrastruktur | Operative Beobachtungspunkte in PILOT_READINESS §5; Tooling ist Implementation |
| LLM-Provider-Festlegung | Adapter-Grenze hält Optionen offen |
| Voice-Adapter-Deployment | Explizit MVP-nachgelagert (ARCHITECTURE_OVERVIEW §9) |
| Backup / Disaster-Recovery | Kein persistenter Session-Content; Event-Log ist low-stakes; kein DR-Design nötig |

---

## 9. Operativer Kurz-Check für Deployment-Entscheidungen

Vor jeder Infrastruktur-, Config- oder Deployment-Entscheidung:

| # | Frage | Bei Ja |
|---|---|---|
| 1 | Muss Guard-Logik geändert werden, um diese Entscheidung zu ermöglichen? | Architekturverstoß – Guards sind environment-invariant |
| 2 | Könnte diese Konfiguration einen Secret in einen Log, einen Prompt oder den Client bringen? | Security-Verletzung – als Secret behandeln oder nicht anlegen |
| 3 | Verlässt hier Session-Content oder Nutzertext die Server-Prozess-RAM-Grenze? | Privacy-Verstoß – SYSTEM_INVARIANTS P-1, P-3 |
| 4 | Passiert hier etwas ohne geprüfte DPA, während reale Personendaten fließen? | P-4-Verletzung – kein Produktionseinsatz ohne DPA |
| 5 | Fügt diese Entscheidung eine zweite Instanz mit Safety-Entscheidungsgewalt ein? | Architekturverstoß – Kernel ist Single Source of Control (A-1) |
| 6 | Wird für diese Entscheidung ein HA/Scale/Multi-Region-Argument eingesetzt, das der Mono-MVP-Realität nicht entspricht? | Scope-Drift – auf MVP-Schnitt zurückführen |
