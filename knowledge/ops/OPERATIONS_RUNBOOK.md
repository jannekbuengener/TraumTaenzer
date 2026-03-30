# OPERATIONS_RUNBOOK

Status: aktiv | Owner: Jannek Büngener | Zuletzt geprüft: 2026-03-30

Basis: DEPLOYMENT_ENVELOPE §2–§9, KERNEL_GUARD_CONTRACTS §3–§10,
TEXT_FIRST_RUNTIME_FLOW §2–§8, PILOT_READINESS §3.3–§3.4,
PROMPT_TEST_BASELINE §3.1, SYSTEM_INVARIANTS A-1–A-4, P-1–P-4

---

## 1. Zweck und Geltungsbereich

Dieses Dokument beschreibt die minimalen operativen Voraussetzungen und
Inspektionsschritte für den text-first Mono-MVP-Betrieb auf dem freigegebenen
Pilotpfad (`Hetzner Cloud Server` in `nbg1` + angehängtes `Hetzner Volume` +
lokales `SQLite`-Event-Store).

Es ist:
- die operative Grundlage für evidenzfähige Testläufe (→ PROMPT_TEST_BASELINE)
- kein Infrastrukturplan und kein IaC-Template
- kein Code, kein Deployment-Script, kein Container-Setup
- kein Ersatz für DEPLOYMENT_ENVELOPE oder KERNEL_GUARD_CONTRACTS

Es beantwortet:
- was vor jedem Testlauf vorhanden und prüfbar sein muss
- welche Artefaktklassen ein Lauf erzeugen muss
- welche Inspektionsschritte ein Lauf mindestens erfordert
- was aktuell noch fehlt und deshalb jeden Lauf blockiert

---

## 2. Aktueller Status

**Bootstrap-Runtime-Pfad im Repo:** vorhanden (`harness/runtime_server.py`, `harness/runtime_tools.py`, `harness/inspect_events.py`, `harness/event_store.py`)
**Hetzner-Zielpfadbindung und reale Evidence:** offen

Der Pilotpfad (Hetzner/SQLite) ist infrastrukturell und datenschutzrechtlich
freigegeben (PROVIDER_DPA_INPUT_MATRIX §7, DEPLOYMENT_ENVELOPE §7), aber die
kanonische Bindung auf echte Hetzner-Zielpfade und der erste evidenzfähige Lauf
sind noch nicht dokumentiert.

Das lokale Harness (`harness/`) implementiert den kanonischen Kernel, die
deterministischen Guards, einen content-freien SQLite-Event-Store und
Fault-Injection-Stubs. Zusätzlich existiert auf `main` ein minimaler
Bootstrap-Serverprozess mit `/health` sowie Start-/Stop-/Inspect-Tooling auf
Basis expliziter absoluter Pfade. Diese Substanz ist die operative Basis für
den nächsten P0-Block, aber kein Ersatz für den Hetzner-Pilotpfad und kein
degraded-Mode-Pilot.

Konsequenz für PROMPT_TEST_BASELINE:
- Nicht-provider-gekoppelte Testfälle mit lokalem Harness: Status `ausführbar`;
  nach tatsächlichem Lauf: `bestanden` oder `nicht bestanden`
- Nicht-provider-gekoppelte Testfälle ohne Runtime-Artefakte (Hetzner-Pfad):
  Status `Vorbedingung fehlt`
- LLM-gekoppelte Testfälle (TB-2): Status `blockiert` (offenes Provider-Gate)

Die §3-Punkte beziehen sich auf den Hetzner-Pilotpfad. Für lokale
Harness-Läufe gilt §3.3/§3.8 als lokal erfüllt (smoke_check.py,
runtime_server.py, runtime_tools.py, fault_injection.py).

### 2.1 Nächster P0-Block: Hetzner Bootstrap Path Contract + First Evidence Recipe

Der nächste echte P0-Block bindet den vorhandenen Bootstrap-Pfad aus
`harness/runtime_server.py` und `harness/runtime_tools.py` an genau einen
realen Hetzner-Zielpfad. Konkrete Zielwerte werden hier nicht erfunden; vor dem
ersten evidenzfähigen Lauf müssen nur die folgenden Felder kanonisch feststehen:

| Feld | Minimalregel |
|---|---|
| `app_root` | Repo-Checkout bzw. Startwurzel des Prozesses auf dem Zielhost; der Bootstrap-Code wird von hier geladen |
| `workdir` | explizites Arbeitsverzeichnis des Prozesses; muss beim Start gesetzt werden, ist Pflicht-Scanroot für `inspect-sidepaths` und darf nicht implizit aus `app_root` oder dem aufrufenden Shell-Kontext abgeleitet werden |
| `volume_mount` | Root des gemounteten Hetzner Volumes |
| `db_path` | absolute SQLite-Datei unter `volume_mount`; kein Fallback |
| `log_path` | absoluter Host-/App-Log-Pfad; kein impliziter Workdir-Fallback |
| `pid_file` | absoluter PID-/Metadatenpfad für `runtime_tools` |
| `bind_host` | explizite Bind-Adresse des Runtime-Prozesses |
| `bind_port` | expliziter Bind-Port des Runtime-Prozesses |

Die erste evidenzfähige Sequenz ist genau:
1. `start`
2. `health`
3. kurzer Session-Smoke
4. `inspect-db`
5. `inspect-log`
6. `inspect-sidepaths`
7. `stop`

Command-first-Referenz aus `app_root`; der Laufprozess selbst arbeitet mit
explizitem `workdir`:

```bash
python -m harness.runtime_tools start --db <db_path> --log <log_path> --pid-file <pid_file> --workdir <workdir> --host <bind_host> --port <bind_port>
python -m harness.runtime_tools health --host <bind_host> --port <bind_port>
curl -sS -X POST "http://<bind_host>:<bind_port>/v1/sessions" -H "Content-Type: application/json" -d "{}"
curl -sS -X POST "http://<bind_host>:<bind_port>/v1/turns" -H "Content-Type: application/json" -d '{"session_id":"<session_id>","user_text":"ja"}'
curl -sS -X POST "http://<bind_host>:<bind_port>/v1/turns" -H "Content-Type: application/json" -d '{"session_id":"<session_id>","user_text":"ja"}'
python -m harness.runtime_tools inspect-db --db <db_path>
python -m harness.runtime_tools inspect-log --log <log_path>
python -m harness.runtime_tools inspect-sidepaths --db <db_path> --log <log_path> --pid-file <pid_file> --workdir <workdir>
python -m harness.runtime_tools stop --pid-file <pid_file>
```

Der bei `start` gesetzte `--workdir`-Wert ist derselbe Scanroot, der bei
`inspect-sidepaths` wiederverwendet werden muss.

Der Session-Smoke ist erst dann ausreichend, wenn der zweite Opt-in-Turn den
vorhandenen no-adapter-Pfad kontrolliert fail-closed
(`NO_ADAPTER_CONFIGURED`) durchläuft.

Dieser P0-Block ist erst geschlossen, wenn genau die vier Artefaktklassen aus
§4 vorliegen: SQLite-Auszug, Host-Log-Ausschnitt, Sidepath-Check,
Teststatus-Eintrag.

---

## 3. Vorbedingungen für evidenzfähige Testläufe

Alle Punkte müssen vor einem Testlauf erfüllt und manuell verifiziert sein.
Kein Punkt darf mit einer Annahme geschlossen werden.

### 3.1 Ausführbare Runtime

| Vorbedingung | Was konkret vorhanden sein muss | Noch nicht vorhanden |
|---|---|---|
| Server-Prozess startbar | Der Mono-Serverprozess (Kernel + Guards + LLM-Adapter + Event-Log-Writer) ist auf dem Zielsystem startbar | ja |
| Prozess endet sauber | Ein definierter Stop-Befehl beendet den Prozess ohne hängende Handles, ohne SQLite-WAL-Leichen und ohne offene Dateisperren | ja |
| Prozess-Neustart setzt Session-State zurück | Nach Neustart beginnt jede neue Session bei ENTRY; kein persistierter Session-State aus vorherigem Lauf sichtbar | ja |
| Kein Content außerhalb RAM | Nach Prozessneustart enthält der SQLite-Store keine Session-Content-Artefakte aus dem vorherigen Lauf | ja |

### 3.2 Definierter Start-/Stop-Pfad

| Vorbedingung | Was konkret vorhanden sein muss | Noch nicht vorhanden |
|---|---|---|
| Start-Befehl dokumentiert | Ein konkreter, reproduzierbarer Startbefehl ist festgelegt (Prozessname, Konfigurationspfad, Port, Umgebungsvariablen) | ja |
| Stop-Befehl dokumentiert | Ein konkreter Stop-Befehl ist festgelegt; ggf. SIGTERM-Handling dokumentiert | ja |
| Bekannte Startdauer | Es ist bekannt, nach wie vielen Sekunden der Prozess bereit ist und welches Signal (Log-Zeile o. ä.) das anzeigt | ja |
| Keine Init-Fehler im Normalpfad | Der Startvorgang erzeugt im Normalpfad keine Fehlermeldungen | ja |

### 3.3 Definierter Health-/Smoke-Check

| Vorbedingung | Was konkret vorhanden sein muss | Noch nicht vorhanden |
|---|---|---|
| Erreichbarkeitscheck definiert | Ein einfacher Befehl oder Request, der zeigt, dass der Prozess läuft und Anfragen entgegennimmt (z. B. Health-Endpunkt oder Prozess-Check) | ja |
| ENTRY-Phase erreichbar | Eine Test-Session kann die ENTRY-Phase erreichen und eine neutrale Antwort erhalten | ja |
| Smoke-Check ohne Provider | Der Smoke-Check läuft durch, auch wenn kein LLM-Provider konfiguriert ist (degraded mode: ENTRY, EXIT erreichbar) | ja |

### 3.4 Definierte Log-Inspektionspfade

| Vorbedingung | Was konkret vorhanden sein muss | Noch nicht vorhanden |
|---|---|---|
| Host-Log-Pfad bekannt | Der Pfad für Host-/App-Logs auf dem Server ist dokumentiert | ja |
| Host-Logs content-free verifizierbar | Es gibt einen dokumentierten Inspect-Befehl, mit dem überprüft werden kann, dass Host-Logs keinen Nutzertext, keinen LLM-Output und keinen Auslösetext enthalten | ja |
| Log-Rotation-/Retention-Verhalten bekannt | Die maximale Haltedauer der Host-Logs (max. 30 Tage per DEPLOYMENT_ENVELOPE §7) ist konfiguriert und prüfbar | ja |
| Prozessabsturz im Log sichtbar | Ein Prozess-Crash erzeugt einen erkennbaren Logeintrag; dieser enthält keinen Session-Content | ja |

### 3.5 Definierter SQLite-Event-Store-Pfad

| Vorbedingung | Was konkret vorhanden sein muss | Noch nicht vorhanden |
|---|---|---|
| SQLite-Datei auf Hetzner Volume | Der genaue Dateipfad der SQLite-Datei auf dem angehängten Hetzner Volume ist dokumentiert | ja |
| Event-Store auslesbar | Ein dokumentierter Inspect-Befehl zeigt Tabellenstruktur und Inhalt der SQLite-Datei an | ja |
| Kein Shadow-Store vorhanden | Es gibt einen dokumentierten Check, der bestätigt, dass keine append-only Datei (`.log`, `.jsonl`, `.txt`) parallel als Event-Store genutzt wird | ja |
| TTL-Purge-Job dokumentiert und aktiv | Der tägliche TTL-Purge-Job (Guard-Events > 90 Tage, System-Error-Events > 30 Tage) ist konfiguriert, läuft und ist verifizierbar | ja |
| VACUUM nach Purge dokumentiert | `VACUUM` wird nach TTL-Purge ausgeführt; keine freien Seiten mit gelöschten Daten sind nach VACUUM prüfbar vorhanden | ja |
| WAL-Datei nach Stop aufgeräumt | Nach sauberem Prozesstopp existiert keine `wal`- oder `shm`-Datei mit Event-Content neben der SQLite-Datei | ja |

### 3.6 Artefakte für Leak-/Redaction-Prüfung

Für jede Testdurchführung muss nach dem Lauf prüfbar sein:

| Artefaktklasse | Erwarteter Befund | Noch nicht prüfbar |
|---|---|---|
| SQLite-Events aus Testlauf | Enthält nur: session_id (opaque), timestamp, event_type (Enum), decision/error-Enums — kein Freitext, kein Nutzerinhalt, kein LLM-Output | ja |
| Host-Logs aus Testlauf | Kein Nutzertext, kein LLM-Output, kein Raw-Payload, keine direkte Nutzeridentität | ja |
| Kein Content in WAL/SHM | WAL-/SHM-Dateien der SQLite enthalten nach Lauf keinen Content | ja |
| Kein Debug-Dump | Im Arbeitsverzeichnis des Prozesses oder in `/tmp` sind keine Debug-Exports mit Prompt-/Output-Content entstanden | ja |

### 3.7 Artefakte für Sidepath-/Dateifallback-Prüfung

| Vorbedingung | Was konkret prüfbar sein muss | Noch nicht prüfbar |
|---|---|---|
| Kein Datei-Event-Store neben SQLite | Ein nach dem Lauf ausgeführter Befehl zeigt, dass keine `.log`/`.jsonl`/`.txt`-Datei Event- oder Content-Daten außerhalb des SQLite-Stores hält | ja |
| Kein Content in Prozess-Workdir | Das Arbeitsverzeichnis des Prozesses enthält nach dem Lauf keine unerwarteten Dateien mit Content-Artefakten | ja |
| Volume-Inhalt nach Lauf vollständig prüfbar | Ein dokumentierter Befehl listet alle Dateien auf dem angehängten Hetzner Volume auf; keine unerwarteten Content-Dateien | ja |

### 3.8 Fault-Injection-Punkte für lokale fail-closed-Fälle

Die folgenden fail-closed-Fälle aus PROMPT_TEST_BASELINE (T18–T20) können ohne
externen LLM-Provider lokal über den vorhandenen Harness-/Bootstrap-Pfad
geprüft werden:

| Fault-Injection | Was injiziert wird | Erwartetes Verhalten |
|---|---|---|
| Guard-Timeout / Guard-Fehler (T18) | Der Input-Guard gibt kein Ergebnis zurück oder wirft einen Fehler | `ERROR_FAIL_CLOSED` → Kernel → `EXIT`; neutrale Fehlermeldung; kein LLM-Call |
| Malformed Provider-Output (T19) | Der LLM-Adapter-Stub liefert leeren String, invalides JSON oder Teil-Response | Kein Output an UI; `ERROR_FAIL_CLOSED` → `EXIT`; kein Raw-Payload im Log |
| Adapter-/Transport-Fehler (T20) | Der LLM-Adapter-Stub signalisiert Timeout, DNS-Fehler oder 5xx | `ERROR_FAIL_CLOSED` → `EXIT`; kein stiller Retry; kein Content-Log |

**Lokale Fault-Injection:** Die stub-fähige Adapter-Schnittstelle ist im lokalen
Harness implementiert (`harness/fault_injection.py`, `harness/llm_adapter.py`,
`harness/kernel.py`). T18–T20 lokal sind über `run_session.py` ausführbar.

Die T18–T20-Fälle im Hetzner-Deployment-Kontext (d. h. mit deploytem Prozess)
bleiben `Vorbedingung fehlt`, bis §3.1–§3.7 geschlossen sind.

LLM-abhängige Testfälle (T01–T17 vollständig, T21 real) bleiben `blockiert`, bis
ein freigabefähiger Provider-Pfad existiert (TB-2-Gate; PROVIDER_DPA_INPUT_MATRIX).

---

## 4. Minimale Laufartefakte

Jeder dokumentierte Testlauf muss folgende Artefakte erzeugen oder bestätigen:

| Artefakt | Format / Ort | Mindestinhalt |
|---|---|---|
| **SQLite-Event-Dump** | Auszug aus SQLite-Datei auf Hetzner Volume | Alle Events des Testlaufs: session_id, timestamp, event_type, decision/error-Enum — kein Freitext |
| **Host-Log-Ausschnitt** | Textauszug aus Server-/App-Log | Log-Einträge für Testlauf-Zeitraum; Bestätigung kein Content |
| **Sidepath-Check-Ergebnis** | Ausgabe eines Listing-Befehls | Bestätigung: kein Shadow-Store, keine unerwarteten Content-Dateien |
| **Teststatus-Eintrag** | In PROMPT_TEST_BASELINE oder separatem Lauf-Protokoll | Genau einer von: `bestanden`, `nicht bestanden`, `blockiert`, `Vorbedingung fehlt` |

`bestanden` darf nur eingetragen werden, wenn alle vier Artefakte vorliegen und
den erwarteten Befund zeigen. Kein Artefakt, kein `bestanden`.

---

## 5. Minimale Inspektionsschritte nach Testlauf

Für jeden Lauf, in dem mindestens ein Safety-Event, Guard-Block, System-Error
oder fail-closed-Übergang aufgetreten ist:

1. SQLite-Event-Store auf Content prüfen:
   Kein Nutzertext, kein LLM-Output, kein Auslösetext in irgendeinem
   Event-Feld.

2. Host-Logs prüfen:
   Kein Content in App-Logs, kein Raw-Payload, keine Session-ID in
   Kombination mit Content.

3. Sidepath-Check:
   Kein Datei-Shadow-Store neben SQLite; kein Debug-Dump im Prozess-Workdir.

4. Fail-Closed-Nachweis:
   Belegter Safe-State-Übergang im Event-Log; vordefinierte Kernel-Antwort
   sichtbar; kein ungeprüfter Output an UI durch Log-Auswertung bestätigt.

5. Nach Prozessstopp:
   Keine WAL-/SHM-Datei mit Content neben SQLite-Datei; sauberes Volume-Listing.

---

## 6. No-Go- und Abbruchkriterien

Wenn eines dieser Kriterien zutrifft: Testlauf sofort abbrechen oder nicht
starten; Befund dokumentieren; Vorbedingung schließen.

| # | Kriterium | Konsequenz |
|---|---|---|
| 1 | Prozess startet nicht oder terminiert unerwartet beim Start | Kein Testlauf; Ursache diagnostizieren |
| 2 | Smoke-Check schlägt fehl (ENTRY-Phase nicht erreichbar) | Kein Testlauf; Prozess und Konfiguration prüfen |
| 3 | SQLite-Datei nicht auf Hetzner Volume auffindbar | Kein Testlauf; Volume-Mount und Initialisierung prüfen |
| 4 | Shadow-Store (Datei neben SQLite) existiert | Testlauf abbrechen; Shadow-Store-Quelle identifizieren und entfernen |
| 5 | Nutzertext, LLM-Output oder Auslösetext im SQLite-Event nach Testlauf | Lauf gilt als `nicht bestanden`; Privacy-Verletzung; Logging-Pfad prüfen |
| 6 | Nutzertext oder Raw-Payload in Host-Log nach Testlauf | Lauf gilt als `nicht bestanden`; Logging-Konfiguration prüfen |
| 7 | Kein Safe-State-Übergang im Event-Log nach erwarteter Guard-Auslösung | Lauf gilt als `nicht bestanden`; Kernel-/Guard-Verhalten prüfen |
| 8 | WAL-Datei mit Content-Artefakten nach Prozessstopp | Lauf gilt als `nicht bestanden`; SQLite-Close-Verhalten prüfen |
| 9 | Fault-Injection-Stub nicht steuerbar ohne Kernel-/Guard-Änderung | Fault-Injection-Fälle auf `Vorbedingung fehlt` belassen |

---

## 7. Was dieses Runbook aktuell nicht leisten kann

| Lücke | Ursache | Konsequenz |
|---|---|---|
| Kanonischer Hetzner Path Contract | Bootstrap-Serverprozess und Operator-Tooling trennen repo-seitig jetzt explizit zwischen Codepfad (`app_root`) und Laufpfad (`workdir`), aber die konkreten Zielwerte für `app_root`, `workdir`, `volume_mount`, `db_path`, `log_path`, `pid_file`, `bind_host` und `bind_port` sind auf Hetzner noch nicht festgezogen | §3.1–§3.5 auf Hetzner weiterhin `Vorbedingung fehlt` |
| Konkrete Dateipfade auf Hetzner Volume | Kein aktiver Deploy und kein belegter `volume_mount`-/`db_path`-Wert | §3.5 vollständig auf `Vorbedingung fehlt` |
| TTL-Purge-Verifikation | Kein laufender Hetzner-Prozess und kein aktiver Ziel-Store | §3.5 vollständig auf `Vorbedingung fehlt` |
| Fault-Injection-Stub (Hetzner-Deployment) | Bootstrap-Prozess lokal vorhanden, aber kein an Hetzner gebundener Lauf; lokales Harness ist kein Deployment | T18–T20 im Deployment-Kontext auf `Vorbedingung fehlt`; lokal via harness/ ausführbar |
| LLM-gekoppelte Testfälle (T01–T17) | Kein freigegebener externer LLM-Pfad (TB-2-Gate offen) | Status `blockiert` per PROMPT_TEST_BASELINE §3.1; T21 teilweise ebenfalls `blockiert` |
| Automatisierte Testausführung | Kein CI-/Testframework vorhanden | Alle Läufe sind manuelle Review-Sessions |
| Retention-Automatisierung auditieren | Kein laufender TTL-Purge-Job | Muss vor Pilot-Start als aktiv nachgewiesen werden |

Dieses Runbook beschreibt den Soll-Stand für evidenzfähige Läufe. Es setzt
keine Implementierung voraus und erfindet keine. Sobald einzelne Punkte aus §3
geschlossen sind, können die entsprechenden Testfälle von `Vorbedingung fehlt`
in `bestanden` oder `nicht bestanden` überführt werden.

---

## 8. Operative Referenzen

| Dokument | Relevanz |
|---|---|
| `DEPLOYMENT_ENVELOPE.md` §2–§7 | Topologie, Trust Boundaries, Fail-Closed im Deployment-Kontext |
| `KERNEL_GUARD_CONTRACTS.md` §3–§10 | Guard-Entscheidungsklassen, Safe States, Fail-Closed-Logik |
| `TEXT_FIRST_RUNTIME_FLOW.md` §2–§8 | Happy Path, Safe-State-Übergänge, Session-Lifecycle |
| `PROMPT_TEST_BASELINE.md` §3–§5 | Testmatrix, Ergebnisstatus, Triage-Logik, Harness-Fallgruppen (§3.2) |
| `PILOT_READINESS.md` §3.3–§3.4 | Go/No-Go-Kriterien inkl. `Vorbedingung fehlt`-Klärung |
| `PROVIDER_DPA_INPUT_MATRIX.md` §7–§8 | Provider-Gate (TB-2); bleibt offen bis freigabefähiger LLM-Pfad |
| `DATA_LIFECYCLE.md` §4–§7 | Retention-Logik, erlaubte Event-Felder |
| `harness/README.md` | Harness-Übersicht, Ausführung, Testfall-Abdeckungstabelle |

---

## 9. Lokaler Harness-Betrieb

Das lokale Harness (`harness/`) ist ein eigenständiger Ausführungskontext für
nicht-provider-gekoppelte Baseline-Fälle. Es ist **kein deployed Prozess, kein
Pilot-Scope und kein Ersatz für den Hetzner-/SQLite-Pilotpfad**.

**Zweck:** Deterministische, reproduzierbare Prüfung von Guard-Logik,
Kernel-Transitionen und Fail-Closed-Verhalten ohne externen LLM-Provider,
ohne Deployment und ohne echte Nutzer.

**Was damit prüfbar ist:**

| Prüfpunkt | Harness-Tool | Erwartetes Ergebnis |
|---|---|---|
| Guard-Entscheidungsklassen (BLOCK_EXIT, BLOCK_REFER, BLOCK_PAUSE, BLOCK_BOUNDARY, RESTRICT_OUTPUT) | `run_session.py` | korrekte Enum-Entscheide; SQLite-Events |
| Output-Guard-Blocking (TRUTH_CLAIM, DIAGNOSIS, COMPANION, EFFICACY_CLAIM, DEEPENING_ON_DISTRESS) | `run_session.py` | Stub-Output blockiert; state → GUARD_BLOCK |
| Kernel-Safe-State-Transitionen und Re-Entry-Schutz | `run_session.py` | korrekte SAFE_STATE_TRANSITION-Events |
| Fail-Closed bei Guard-Fehler (T18) | `run_session.py --scenario T18` | state → EXIT; SYSTEM_ERROR im Event-Log |
| Fail-Closed bei Malformed Output (T19) | `run_session.py --scenario T19` | state → EXIT; SYSTEM_ERROR im Event-Log |
| Kein Content im Event-Store (Schema-Check) | `inspect_events.py --check-only` | Exit-Code 0; keine Freitext-Spalten |
| Harness-Startbarkeit und Grundverhalten | `smoke_check.py` | Exit-Code 0; 7/7 Checks |

**Artefakte pro Harness-Lauf:**
- `harness/data/events.db` (gitignored): content-freie SQLite-Events; session_id Pseudonym,
  Timestamp, Enums — kein Nutzertext, kein LLM-Output
- Smoke-Check-Protokoll: stdout + Exit-Code
- Szenarien-Laufprotokoll: stdout + Exit-Code pro Szenario

**Grenzen — kein Ersatz für:**
- Hetzner-Deployment, Volume-gebundene SQLite-Datei und Host-Log-Inspektion (§3.4–§3.5)
- Reales LLM-Provider-Antwortverhalten: T10, T12 ALLOW-Pfade, T16 LLM-Output-Pfad, T20 real (→ `blockiert`)
- Sidepath-/WAL-/Retention-Nachweis auf Produktionsinfrastruktur: T21 vollständig (→ `Vorbedingung fehlt`)
- Prozess-Lifecycle-Garantien auf Zielsystem: Start/Stop/Health/SIGTERM (§3.1–§3.3)

**No-Go — lokaler Harness ist kein Pilot-Nachweis:**
Harness-Laufartefakte zählen nicht als Pilot-bestanden-Nachweis im Sinne von
`PROMPT_TEST_BASELINE §3.1` und `PILOT_READINESS §3.3`. Für Pilotfreigabe sind
ausschließlich Nachweise gegen den freigegebenen Pilotpfad (Hetzner Cloud Server
`nbg1` + Hetzner Volume + SQLite) zulässig. Die Fallgruppen-Zuordnung ist in
`PROMPT_TEST_BASELINE §3.2` dokumentiert.
