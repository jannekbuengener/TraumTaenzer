# OPERATIONS_RUNBOOK

Status: aktiv | Owner: Jannek Büngener | Zuletzt geprüft: 2026-04-20

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

**Hetzner-deploybare Runtime:** vorhanden; erster Evidence-Lauf 2026-04-19 bestanden
**Lokale Harness-Runtime:** vorhanden (`harness/` — Python stdlib, kein Deployment, kein Provider)

Der Pilotpfad (Hetzner/SQLite) ist infrastrukturell und datenschutzrechtlich
freigegeben (PROVIDER_DPA_INPUT_MATRIX §7, DEPLOYMENT_ENVELOPE §7) und deployed.
Der erste nicht-provider-gekoppelte Evidence-Lauf wurde am 2026-04-19 vollständig
durchgeführt (7/7 Schritte: start → health → session-smoke → stop → inspect-db
→ inspect-log → inspect-sidepaths; alle bestanden). Der konkrete Runtime-Contract
ist in §10 dokumentiert.

Das lokale Harness (`harness/`) implementiert den kanonischen Kernel, die
deterministischen Guards, einen content-freien SQLite-Event-Store und
Fault-Injection-Stubs. Es ermöglicht lokale Evidence-Läufe für
nicht-provider-gekoppelte Testfälle, ist aber kein Ersatz für den
Hetzner-Pilotpfad und kein degraded-Mode-Pilot.

Konsequenz für PROMPT_TEST_BASELINE:
- Nicht-provider-gekoppelte Testfälle mit lokalem Harness: Status `ausführbar`;
  nach tatsächlichem Lauf: `bestanden` oder `nicht bestanden`
- T21 (Hetzner-Volume-Sidepath-Nachweis): `bestanden` (2026-04-19; →§10)
- T17 (Host-Log-Artefakte): Hetzner-Infrastruktur verfügbar; Szenario
  BLOCK_REFER/CRISIS auf Hetzner-Pfad noch nicht ausgeführt; offen
- LLM-gekoppelte Testfälle (TB-2): Status `blockiert` (offenes Provider-Gate)

**Offene §3-Punkte nach erstem Evidence-Lauf (2026-04-19; vor Follow-up #80, →§10):**
- §3.5: TTL-Purge-Job nicht konfiguriert; VACUUM nach Purge nicht dokumentiert
- §3.4: Log-Rotation (max. 30 Tage) nicht konfiguriert; Crash-Log-Verhalten nicht getestet
- §3.6: SQLite-Event-Row-Dump (Pflicht-Artefakt §4) noch nicht abgerufen

**Stand nach Follow-up #80 (2026-04-20):**
- §3.5: erfüllt; täglicher `systemd`-Timer + TTL-Purge + `VACUUM` auf `/mnt/tt-volume/events.db` aktiv und manuell verifiziert
- §3.4: Log-Rotation für `/var/log/traumtaenzer/runtime.log` konfiguriert und per `logrotate --debug` geprüft; Crash-Log-Verhalten weiterhin offen

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
externen LLM-Provider geprüft werden, sobald die Runtime existiert:

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

## 7. Was dieses Runbook nach dem ersten Evidence-Lauf (Stand 2026-04-19) noch nicht abdeckte

| Lücke | Ursache | Konsequenz |
|---|---|---|
| SQLite-Event-Row-Dump | `sqlite3`-CLI auf Server nicht installiert; `inspect_events.py` ohne `--check-only` nicht ausgeführt | §4-Pflicht-Artefakt fehlt; kein weiterer Testfall formal `bestanden` (außer T21); separates Follow-up |
| TTL-Purge-Verifikation | Kein konfigurierter Cron-Job oder systemd-Timer auf Server | §3.5 teilweise offen; VACUUM nach Purge ebenfalls undokumentiert |
| Log-Rotation (max. 30 Tage) | Nicht konfiguriert auf Server | §3.4 teilweise offen; DEPLOYMENT_ENVELOPE §7-Anforderung unerfüllt |
| T17-Szenario (BLOCK_REFER/CRISIS) | Im ersten Evidence-Lauf BLOCK_EXIT/SAFEWORD statt BLOCK_REFER/CRISIS | T17 Host-Log-Artefakt-Nachweis für CRISIS-Pfad steht aus |
| Fault-Injection-Stub im Hetzner-Deployment | Kein systemd-Service; kein steuerbarer Deployment-Start für T18–T20 auf Hetzner | T18–T20 im Deployment-Kontext weiter `Vorbedingung fehlt` für exaktes Hetzner-Szenario |
| LLM-gekoppelte Testfälle (T01–T17 vollständig, T21 real) | Kein freigegebener externer LLM-Pfad (TB-2-Gate offen) | Status `blockiert` per PROMPT_TEST_BASELINE §3.1; T21 vollständig ebenfalls |
| Automatisierte Testausführung | Kein CI-/Testframework vorhanden | Alle Läufe sind manuelle Review-Sessions |
| systemd-Service-Unit | Kein Service-Unit für Runtime-Prozess auf Server | Manueller Start/Stop; kein Autostart nach Reboot |

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
- Sidepath-/WAL-/Retention-Nachweis auf Produktionsinfrastruktur (→ T21 `bestanden` 2026-04-19; §10)
- Prozess-Lifecycle-Garantien auf Zielsystem: Start/Stop/Health/SIGTERM (§3.1–§3.3)

---

## 10. Erster Hetzner-Evidence-Lauf (2026-04-19)

Dieser Abschnitt dokumentiert den ersten realen, nicht-provider-gekoppelten
Evidence-Lauf auf dem freigegebenen Hetzner-/SQLite-Pilotpfad. Er ist kein
Pilot-Nachweis, kein Live-Claim und kein Provider-Go-Nachweis.

### 10.1 Infrastruktur-Fakten

| Parameter | Wert |
|---|---|
| Server-Name / ID | `traumtaenzer-core-01` / `125786108` |
| Region | `nbg1` (Nuremberg DC Park 1) |
| Server-Typ | CX23 (2 vCPU, 4 GB RAM, 40 GB Disk) |
| OS | Ubuntu 24.04 LTS |
| IPv4 | `167.235.26.106` (nicht öffentlich exponiert — kein Dienst an 0.0.0.0) |
| Volume-Name / ID | `traumtaenzer-volume-01` / `105320450` |
| Volume-Größe | 10 GB |
| Volume-UUID | `c828977a-0a9b-4a78-92bb-964d6b24bdde` |
| Volume-Mount | `/mnt/tt-volume` (ext4, fstab-persistent, nofail,discard) |
| Python | 3.12.3 (stdlib-only; kein pip benötigt) |
| SSH-Key | `tt-hetzner` (ID 110232430); lokale Datei `~/.ssh/tt_hetzner` |

### 10.2 Runtime-Contract

| Parameter | Wert |
|---|---|
| `app_root` | `/opt/traumtaenzer` |
| `workdir` | `/opt/traumtaenzer` |
| `volume_mount` | `/mnt/tt-volume` |
| `db_path` | `/mnt/tt-volume/events.db` |
| `log_path` | `/var/log/traumtaenzer/runtime.log` |
| `pid_file` | `/run/traumtaenzer.pid` |
| `bind_host` | `127.0.0.1` |
| `bind_port` | `8080` |

### 10.3 Laufergebnis (7 Schritte)

Datum: 2026-04-19. Keine externen Provider. Kein Pilot-Claim.

| Schritt | Befehl / Endpunkt | Ergebnis |
|---|---|---|
| `start` | `python -m harness.runtime_tools start --db /mnt/tt-volume/events.db --log /var/log/traumtaenzer/runtime.log ...` | **bestanden** — PID 240004; `adapter_mode=SAFE`; DB initialisiert |
| `health` | `GET /health` | **bestanden** — `{"status":"ok","adapter_mode":"SAFE","session_count":0}` |
| `session-smoke` | `POST /v1/sessions` + `POST /v1/turns` (×3) | **bestanden** — Sequenz ENTRY→CHECK_IN→REFLECTION→EXIT via Safeword „stopp"; `terminal=true` |
| `stop` | `POST /shutdown` | **bestanden** — Sauberer Shutdown; PID-Datei entfernt; `event_store_closed path=/mnt/tt-volume/events.db` im Log |
| `inspect-db` | `python -m harness.runtime_tools inspect-db --db /mnt/tt-volume/events.db --check-only` | **bestanden** — `{"status":"ok","db_path":"/mnt/tt-volume/events.db"}`; keine Content-Violations im Schema |
| `inspect-log` | `python -m harness.runtime_tools inspect-log --log /var/log/traumtaenzer/runtime.log` | **bestanden** — `{"status":"ok","tail_lines":25}`; 25 Zeilen content-free (nur State-Enums, keine Freitexte) |
| `inspect-sidepaths` | `python -m harness.runtime_tools inspect-sidepaths ...` | **bestanden** — `{"status":"ok","scan_roots":["/mnt/tt-volume","/opt/traumtaenzer","/var/log/traumtaenzer"]}`; kein Shadow-Store; Volume-Listing: nur `events.db` + `lost+found` |

### 10.4 §3-Status nach erstem Lauf

| §3-Block | Status | Offene Punkte |
|---|---|---|
| §3.1 Ausführbare Runtime | **erfüllt** | — |
| §3.2 Start-/Stop-Pfad | **erfüllt** | — |
| §3.3 Health-/Smoke-Check | **erfüllt** | — |
| §3.4 Log-Inspektionspfade | **teilweise erfüllt** | Log-Rotation (max. 30 Tage) nicht konfiguriert; Crash-Log-Eintrag nicht getestet |
| §3.5 SQLite-Event-Store | **teilweise erfüllt** | TTL-Purge-Job nicht konfiguriert; VACUUM nach Purge nicht dokumentiert |
| §3.6 Leak-/Redaction-Artefakte | **teilweise erfüllt** | SQLite-Event-Row-Dump (mit decision/guard-Enums) nicht abgerufen — nur `--check-only` Schema-Check; `sqlite3`-CLI nicht auf Server; Pflicht-Artefakt §4 offen |
| §3.7 Sidepath-/Dateifallback | **erfüllt** | — |

### 10.5 PROMPT_TEST_BASELINE-Status (Hetzner-Pfad)

| Fall | Status | Begründung |
|---|---|---|
| T21 (Hetzner-Volume-Sidepath) | **bestanden** | inspect-sidepaths auf realem Volume bestanden; kein Shadow-Store; kein WAL; Pass-Kriterium vollständig erfüllt |
| T17 (Host-Log-Artefakte) | Infrastruktur verfügbar; **Szenario ausstehend** | Host-Log content-free verifiziert; BLOCK_REFER/CRISIS-Szenario nicht ausgeführt (Lauf verwendete BLOCK_EXIT/SAFEWORD); Event-Row-Dump fehlt |
| T10, T12-ALLOW, T16-LLM, T20-real | **blockiert** | TB-2-Gate offen (unverändert) |

### 10.6 Follow-up #80: TTL-Purge + VACUUM + Log-Rotation (2026-04-20)

| Nachweis | Artefakt / Befehl | Ergebnis |
|---|---|---|
| TTL-Purge-Skript | `/usr/local/sbin/traumtaenzer-events-retention.py` | Python-Stdlib-only; löscht `SYSTEM_ERROR` > 30 Tage und übrige Runtime-Events > 90 Tage; führt danach immer `VACUUM` aus; fail-closed bei fehlender DB, ungültigen Timestamps oder unvollständigem `VACUUM` |
| TTL-Purge-Service | `/etc/systemd/system/traumtaenzer-events-retention.service` | `Type=oneshot`; `ExecStart=/usr/local/sbin/traumtaenzer-events-retention.py --db /mnt/tt-volume/events.db` |
| TTL-Purge-Timer | `/etc/systemd/system/traumtaenzer-events-retention.timer` | `OnCalendar=daily`, `Persistent=true`; auf dem Host registriert; nächster Lauf: `2026-04-20 00:00:00 UTC` |
| Manueller Testlauf | `systemctl start traumtaenzer-events-retention.service` + `systemctl status --no-pager traumtaenzer-events-retention.service` | Exit `0/SUCCESS`; Journal: `status=ok db=/mnt/tt-volume/events.db deleted_90d=0 deleted_30d=0 freelist_before=0 freelist_after=0 total_rows=17` |
| Log-Rotation-Datei | `/etc/logrotate.d/traumtaenzer` | Konfiguriert: `daily`, `rotate 30`, `compress`, `missingok`, `notifempty`, `copytruncate` |
| Logrotate-Debug | `logrotate --debug /etc/logrotate.d/traumtaenzer` | Parser sauber; `/var/log/traumtaenzer/runtime.log` erkannt; Rotation-Regel `after 1 days (30 rotations)` |

Minimalpfad-Entscheid: `systemd`-Timer statt `cron`, weil der Host bereits
native `systemd`-Timer nutzt (`logrotate.timer`, `apt-daily.timer` u. a.), kein
Root-Crontab vorhanden war und Timer-/Service-Status plus Journal ohne
Zusatztool belastbar prüfbar sind.

Dieser Follow-up schließt nur den Ops-Restpunkt aus Issue #80. Das gezielte
Crash-Log-Verhalten bleibt separat offen; die Evidence-Follow-ups aus #78 und
#79 werden hier nicht erneut dokumentiert.

### 10.7 Offene Follow-up-Punkte (Stand 2026-04-20)

1. Crash-Log-Verhalten auf Hetzner gezielt testen; erst dann ist `OPERATIONS_RUNBOOK §3.4` vollständig erfüllt.
2. systemd-Service-Unit für Runtime-Prozess (vor Pilot; kein P0 jetzt).

**No-Go — lokaler Harness ist kein Pilot-Nachweis:**
Harness-Laufartefakte zählen nicht als Pilot-bestanden-Nachweis im Sinne von
`PROMPT_TEST_BASELINE §3.1` und `PILOT_READINESS §3.3`. Für Pilotfreigabe sind
ausschließlich Nachweise gegen den freigegebenen Pilotpfad (Hetzner Cloud Server
`nbg1` + Hetzner Volume + SQLite) zulässig. Die Fallgruppen-Zuordnung ist in
`PROMPT_TEST_BASELINE §3.2` dokumentiert.
