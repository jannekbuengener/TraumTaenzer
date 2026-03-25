# KERNEL_GUARD_CONTRACTS

Status: aktiv | Owner: Jannek Büngener | Zuletzt geprüft: 2026-03-25

Basis: ARCHITECTURE_OVERVIEW §3–§8, GUARDRAILS_CONTENT_POLICY §2–§7,
SAFETY_PLAYBOOK §3–§6, PRIVACY_BY_DESIGN §4–§5, SYSTEM_INVARIANTS A-1–A-4, S-1–S-2

---

## 1. Zweck und Geltungsbereich

Dieses Dokument definiert die minimalen technischen Contracts für Kernel, Guard Layer,
Safe States, Event-Log und Adapter-Übergänge des text-first MVP.

Es ist:
- eine Implementierungsvorlage – kein Runtime-Code
- provider-agnostisch und framework-neutral
- auf text-first MVP begrenzt (Voice/3D: explizit nachgelagert)
- keine vollständige Runtime-Architektur und kein Infrastrukturentscheid

Es dient als direkte technische Grundlage für:
- Kernel-Implementierung
- deterministischen Guard Layer
- Safe-State-Steuerung
- Event-Log-Disziplin
- LLM-Adapter-Abgrenzung

---

## 2. Systemgrenze / Verantwortungsgrenze

| Schicht | Minimale Verantwortung | Darf nicht |
|---|---|---|
| **UI / Client** | Eingaben entgegennehmen, Ausgaben darstellen, Exit jederzeit zugänglich halten | Safety-Entscheidungen treffen, Session-State halten, Logs schreiben, Safe States überschreiben |
| **Kernel** | Session-State halten und übergeben, Guards aufrufen, Safe-State-Übergänge auslösen, Prompt-Konstruktion | LLM direkt aufrufen ohne Guard-Prüfung, Inhalte persistieren, Safety durch Inference entscheiden |
| **Guard Layer** | Input/Output regelbasiert und deterministisch prüfen, Guard-Entscheidung zurückgeben | Modell aufrufen, Inference nutzen, Session-State halten, Persistenz veranlassen |
| **LLM-Adapter** | Text auf Basis des zugeführten Kontexts generieren | Session steuern, Safety entscheiden, Logs schreiben, Persistenz veranlassen, Prompt selbst konstruieren |
| **Event-Log** | Systemereignisse append-only, redacted, content-free erfassen | Nutzerinhalte loggen, Content zu Safety-Events verknüpfen |
| **Voice-Adapter** | Audio-I/O (optional, MVP-nachgelagert) | Safety-Logik übernehmen, Kernel umgehen, Guards ersetzen |

---

## 3. Minimales Zustandsmodell

Sieben Zustände für text-first MVP. Ergänzungen nur bei belegtem technischen Bedarf.

| Zustand | Bedeutung | Erlaubte Eingänge (von) | Erlaubte Übergänge (nach) | Verbotene Übergänge | Minimale Systemreaktion |
|---|---|---|---|---|---|
| `ENTRY` | Onboarding: KI-Info, Safeword, Opt-in-Frage | `SESSION_STARTED` | `CHECK_IN` (nach Opt-in), `EXIT` | Auto-Weiter ohne Nutzerbestätigung | Onboarding-Text ausgeben, auf explizites Opt-in warten |
| `CHECK_IN` | Bereitschaftsprüfung, Tempo-Anpassung | `ENTRY` (nach Opt-in) | `REFLECTION` (nach Bestätigung), `PAUSED`, `EXIT`, `EXTERNAL_REFERRAL` | Auto-Weiter ohne Bestätigung; Weiter bei Belastungssignal | Offene Frage, warten – kein Druck |
| `REFLECTION` | Reflexionskern: Nutzer bringt Material ein, System rahmt und spiegelt | `CHECK_IN` (nach Bestätigung), `PAUSED` (nach Nutzer-Go) | `PAUSED`, `EXIT`, `EXTERNAL_REFERRAL`, `GUARD_BLOCK`, zyklisch `REFLECTION` | Vertiefung ohne Nutzerinitiative; Weiter nach Überforderungssignal | Auf Nutzereingabe reagieren, Perspektiven anbieten – nie deuten |
| `PAUSED` | Safety-Pause: Überforderung, Distress oder Desorientierung | `REFLECTION`, `CHECK_IN` | `REFLECTION` (nur mit explizitem Nutzer-Go), `EXIT` | Auto-Weiter; neue Inhalte ausgeben | Verlangsamung, Orientierungsangebot, Exit anbieten – kein neues Material |
| `EXIT` | Session beendet (normal, Safeword oder Abbruch) | Jeder Zustand | `SESSION_ENDED` | Re-Entry ohne explizite Nutzeraktion | Neutrale Bestätigung, kein Kommentar zur Unterbrechung, kein weiterer Inhalt |
| `EXTERNAL_REFERRAL` | Krisensprache oder akute Gefährdung erkannt | Jeder Zustand | `SESSION_ENDED` | Weiterführung jeglichen Inhalts | Externer Verweis (Notruf 112, TelefonSeelsorge 0800 111 0 111), kein inhaltlicher Kommentar |
| `GUARD_BLOCK` | Output-Guard hat Antwort zurückgehalten | `REFLECTION` (Output-Prüfung) | `REFLECTION` (nach Kernel-Freigabe + Nutzer-Go), `EXIT`, `PAUSED` | Retry ohne Kernel-Entscheidung; blockierten Output ausgeben | Neutrale Systemmeldung, kein Inhalt aus dem verworfenen Output |

**Fail-Closed-Regel:** Kann der Kernel keinen eindeutigen Zielzustand ermitteln → sofort `EXIT`. Kein Fallback auf „weiter wie bisher".

---

## 4. Event-Contracts

Alle Events: append-only, content-free, redaction-first.

### Gemeinsame Pflichtfelder (alle Events)

```
session_id:   string   // pseudonym, kein direkter Nutzerbezug
event_type:   string   // einer der definierten Typen unten
timestamp:    ISO8601
```

**Verboten in allen Events ohne Ausnahme:**
Nutzertext, LLM-Prompt, LLM-Output, Safeword-Text, Trigger-Formulierung,
personenbezogene Identifikatoren, Inhaltskontexte.

---

### `SESSION_STARTED`
Zweck: Session-Initialisierung dokumentieren.

| Feld | Status |
|---|---|
| session_id, timestamp | erforderlich |
| Nutzer-ID (nicht-pseudonym) | **verboten** |
| Startinhalt / Nutzereingabe | **verboten** |

---

### `SESSION_ENDED`
Zweck: Session-Abschluss dokumentieren.

| Feld | Status |
|---|---|
| session_id, timestamp | erforderlich |
| end_type | erforderlich – enum: `NORMAL` / `SAFEWORD` / `GUARD_ABORT` / `REFERRAL` / `SYSTEM_ERROR` |
| last_state | optional – nur Safe-State-Name |
| Abbruchursache als Text | **verboten** |
| Nutzerinhalt | **verboten** |

---

### `USER_INPUT_RECEIVED`
Zweck: Eingabeereignis im Kernel für Guard-Aufruf auslösen.
**Nicht persistent** – nur Kernel-internes Signal, darf den Event-Log nicht erreichen.

| Feld | Status |
|---|---|
| session_id, timestamp, current_state | nur Kernel-intern |
| Eingabetext | nur Kernel-RAM für Guard-Prüfung – **niemals persistieren** |

---

### `INPUT_GUARD_RESULT`
Zweck: Guard-Entscheidung für Input dokumentieren.

| Feld | Status |
|---|---|
| session_id, timestamp | erforderlich |
| decision | erforderlich – Guard-Entscheidungsklasse (→ §5) |
| guard_category | erforderlich – enum ohne Text: `SAFEWORD` / `CRISIS` / `DISTRESS` / `DISSOCIATION` / `BOUNDARY_REQUEST` / `INTERPRETATION_REQUEST` / `ALLOW` / `ERROR` |
| Auslösetext / Nutzerformulierung | **verboten** |

---

### `LLM_OUTPUT_RECEIVED`
Zweck: Modellantwort im Kernel für Output-Guard bereitstellen.
**Nicht persistent** – nur Kernel-internes Signal.

| Feld | Status |
|---|---|
| session_id, timestamp | nur Kernel-intern |
| LLM-Ausgabetext | nur Kernel-RAM für Output-Guard – **niemals persistieren** |

---

### `OUTPUT_GUARD_RESULT`
Zweck: Guard-Entscheidung für Output dokumentieren.

| Feld | Status |
|---|---|
| session_id, timestamp | erforderlich |
| decision | erforderlich – enum: `ALLOW` / `BLOCK` |
| violation_type | erforderlich bei `BLOCK` – enum ohne Text: `DIAGNOSIS` / `COMPANION` / `EFFICACY_CLAIM` / `REFRAME_AFTER_EXIT` / `DEEPENING_ON_DISTRESS` / `TRUTH_CLAIM` / `OTHER` |
| Ausgabetext / LLM-Output | **verboten** |

---

### `SAFE_STATE_TRANSITION`
Zweck: Zustandsübergang dokumentieren.

| Feld | Status |
|---|---|
| session_id, timestamp | erforderlich |
| from_state | erforderlich |
| to_state | erforderlich |
| trigger_event | erforderlich – Event-Typ, der den Übergang auslöste |
| Ursachentext | **verboten** |

---

### `SYSTEM_ERROR`
Zweck: Systemfehler ohne Nutzerinhalt dokumentieren.

| Feld | Status |
|---|---|
| session_id, timestamp | erforderlich |
| error_code | erforderlich |
| component | erforderlich – enum: `KERNEL` / `GUARD` / `LLM_ADAPTER` / `EVENT_LOG` |
| Nutzerinhalt, LLM-Prompt/-Output | **verboten** |

---

## 5. Guard-Decision-Contract

### Schnittstelle: Kernel → Guard Layer

Der Kernel übergibt dem Guard:
- `session_id`
- `current_state`
- zu prüfenden Text – **nur im Arbeitsspeicher, nicht persistent, nicht geloggt**

Der Guard gibt zurück:
- Entscheidungsklasse (enum)
- optional: `guard_category` (enum, kein Freitext)

Der Guard darf nicht:
- den LLM aufrufen oder Inference nutzen
- den Session-State ändern
- Persistenz- oder Log-Operationen auslösen

---

### Input-Guard-Entscheidungsklassen

| Klasse | Bedeutung | LLM-Call? | Safe-State-Transition |
|---|---|---|---|
| `ALLOW` | Eingabe unauffällig | ja | keine |
| `BLOCK_EXIT` | Safeword oder expliziter Abbruch | nein | → `EXIT` |
| `BLOCK_REFER` | Krisensprache / akute Gefährdung | nein | → `EXTERNAL_REFERRAL` |
| `BLOCK_PAUSE` | Dissoziation oder eskalierender Distress | nein | → `PAUSED` |
| `BLOCK_BOUNDARY` | Diagnose- oder Therapieanfrage | nein | → `EXIT` oder `PAUSED` (Kernel entscheidet nach Schwere) |
| `RESTRICT_OUTPUT` | Unzulässige Deutungsanforderung; LLM erlaubt, Output-Guard mit erhöhtem Maßstab | ja, mit Constraint-Annotation | keine (Output-Guard entscheidet) |
| `ERROR_FAIL_CLOSED` | Guard liefert kein Ergebnis / Fehler | nein | → `EXIT` |

---

### Output-Guard-Entscheidungsklassen

| Klasse | Bedeutung | Output an UI? | Safe-State-Transition |
|---|---|---|---|
| `ALLOW` | Ausgabe regelkonform | ja | keine |
| `BLOCK` | Verbotenes Muster erkannt (→ GUARDRAILS §4, §8) | nein | → `GUARD_BLOCK` |
| `ERROR_FAIL_CLOSED` | Guard liefert kein Ergebnis / Fehler | nein | → `EXIT` |

---

## 6. Input-Guard- und Output-Guard-Fluss

```
USER_INPUT_RECEIVED
  │
  ▼
[Input Guard] ─── deterministisch, regelbasiert, kein LLM
  │
  ├─ ALLOW         → Kernel konstruiert Prompt → [LLM Adapter]
  │                        │
  │                        ▼
  │                  LLM_OUTPUT_RECEIVED (nur Kernel-RAM)
  │                        │
  │                        ▼
  │                  [Output Guard] ─── deterministisch, regelbasiert
  │                    ├─ ALLOW          → Ausgabe an UI
  │                    ├─ BLOCK          → GUARD_BLOCK → neutrale Systemmeldung
  │                    └─ ERROR_FC       → EXIT → neutrale Systemmeldung
  │
  ├─ BLOCK_EXIT    → EXIT → neutrale Bestätigung         [kein LLM-Call]
  ├─ BLOCK_REFER   → EXTERNAL_REFERRAL → externer Verweis [kein LLM-Call]
  ├─ BLOCK_PAUSE   → PAUSED → Orientierungsangebot        [kein LLM-Call]
  ├─ BLOCK_BOUNDARY→ EXIT oder PAUSED → Grenzenverweis    [kein LLM-Call]
  ├─ RESTRICT_OUT  → LLM mit Constraint → Output Guard (erhöhter Maßstab)
  └─ ERROR_FC      → EXIT → neutrale Systemmeldung        [kein LLM-Call]
```

**Unveränderliche Invarianten:**
1. LLM-Adapter wird nie ohne abgeschlossene Input-Guard-Prüfung aufgerufen.
2. LLM-Output erreicht die UI nie ohne abgeschlossene Output-Guard-Prüfung.
3. Neutrale Systemmeldungen kommen nicht vom LLM – sie sind vordefinierte Kernel-Texte.
4. Bei `ERROR_FAIL_CLOSED` an irgendeiner Stelle: sofort `EXIT`, kein Retry.

---

## 7. Safe-State-Transition-Regeln

| Auslöser | Zielzustand | Erlaubte Reaktion | Retry? | Re-Entry-Bedingung |
|---|---|---|---|---|
| `BLOCK_EXIT` / Safeword | `EXIT` | Neutrale Bestätigung | nein | Explizite neue Session-Initiierung |
| `BLOCK_REFER` / Krisensprache | `EXTERNAL_REFERRAL` | Externer Verweis, kein Kommentar | nein | Nur über neue Session nach Nutzeraktion |
| `BLOCK_PAUSE` / Distress | `PAUSED` | Orientierungsangebot, Exit anbieten | nein (neues Nutzer-Signal nötig) | Explizite Nutzerbestätigung + Kernel-Freigabe |
| Output `BLOCK` | `GUARD_BLOCK` | Neutrale Systemmeldung, Output verwerfen | nein (ohne Kernel-Entscheidung) | Kernel-Entscheidung + neues Nutzer-Go |
| Guard `ERROR_FAIL_CLOSED` | `EXIT` | Neutrale Systemmeldung | nein | Neue Session |
| Expliziter Nutzerabbruch | `EXIT` | Neutrale Abschlussformulierung | nein | Neue Session |
| `BLOCK_BOUNDARY` | `EXIT` oder `PAUSED` | Grenzenverweis ohne Wertung | nein | Wie PAUSED oder EXIT |
| Kein ermittelbarer Zielzustand | `EXIT` (fail-closed) | Neutrale Systemmeldung | nein | Neue Session |

**Allgemeine Safe-State-Regeln:**
- Kein automatischer Re-Entry nach `EXIT` oder `EXTERNAL_REFERRAL`.
- Kein „weiter wie bisher" nach Safe-State-Eintritt.
- Ausbleibendes Nutzer-Signal ist kein Go-Signal.
- Sicherheitspräferenz bei Konflikten: `EXIT` > `EXTERNAL_REFERRAL` > `PAUSED` > `GUARD_BLOCK` > `ALLOW`

---

## 8. Adapter-Grenzen

### Was der LLM-Adapter bekommt

- Vom Kernel konstruierten, strukturierten Prompt-Kontext
- Keinen rohen Nutzertext ohne Kernel-Verarbeitung
- Keine Session-Historien über das für Inference nötige Minimum hinaus
- Kein Safeword, keine Guard-Ergebnisse, keine Safety-Entscheidungen

### Was der LLM-Adapter nicht wissen darf

- Session-State
- Guard-Entscheidungen oder -Kategorien
- Safeword-Konfiguration
- Nutzeridentität
- Frühere Safety-Events

### Feste Adapter-Grenzen

| Grenze | Regel |
|---|---|
| Session-State | Liegt ausschließlich beim Kernel |
| Safety-Entscheidung | Trifft niemals der Adapter |
| Prompt-Konstruktion | Kernelaufgabe; Adapter erhält fertigen Kontext |
| Persistenz | Adapter löst keine Speicher- oder Log-Operationen aus |
| Logging | Adapter schreibt keine Events |
| Provider-Agnostik | Adapter-Schnittstelle ist provider-neutral; Kernel-Logik ändert sich bei Provider-Wechsel nicht |

---

## 9. Event-Log- und Persistenzdisziplin

### Im persistenten Log erlaubte Event-Klassen

| Event-Klasse | Erlaubte Felder | Verbotene Felder |
|---|---|---|
| `SESSION_STARTED` | session_id, timestamp | Nutzer-ID, Startinhalt |
| `SESSION_ENDED` | session_id, timestamp, end_type, last_state | Ursachentext, Nutzerinhalt |
| `INPUT_GUARD_RESULT` | session_id, timestamp, decision, guard_category | Auslösetext, Nutzerformulierung |
| `OUTPUT_GUARD_RESULT` | session_id, timestamp, decision, violation_type | Ausgabetext, LLM-Output |
| `SAFE_STATE_TRANSITION` | session_id, timestamp, from_state, to_state, trigger_event | Ursachentext |
| `SYSTEM_ERROR` | session_id, timestamp, error_code, component | Nutzerinhalt, Prompt, Output |

### Explizit nicht persistent

- `USER_INPUT_RECEIVED` – enthält Eingabetext; verbleibt im Kernel-RAM
- `LLM_OUTPUT_RECEIVED` – enthält LLM-Antwort; verbleibt im Kernel-RAM

### Strenge Verbote (ohne Ausnahme)

- Kein Nutzertext, kein Trauminhalt, kein Reflexionstext in irgendeinem Log
- Kein LLM-Prompt oder LLM-Output in irgendeinem Log
- Keine Verknüpfung von Nutzeridentität mit Inhaltsereignissen
- Kein Content-Kontext zu Safety- oder Guard-Events

### Retention

- Guard-/Safety-Events: maximal 90 Tage → automatisch löschen
- System-Error-Logs: maximal 30 Tage → automatisch löschen
- Keine Archivierung ohne dokumentierten Grund und definierten Löschpfad

---

## 10. Minimaler Fehler- und Fail-Closed-Pfad

| Fehlerszenario | Systemverhalten |
|---|---|
| Guard Layer antwortet nicht / Timeout | `ERROR_FAIL_CLOSED` → `EXIT`; kein LLM-Call |
| LLM-Adapter antwortet nicht / Fehler | Output-Guard ohne Ergebnis → `BLOCK` → `GUARD_BLOCK`, dann `EXIT` |
| Kernel kennt Zielzustand nicht | Sofort `EXIT`; `SYSTEM_ERROR` loggen (kein Inhalt) |
| Widersprüchliche Guard-Signale | Pessimistischstes Signal gewinnt: `EXIT` vor `PAUSED` vor `ALLOW` |
| Event-Log-Fehler | Logging-Fehler blockiert keine Kernel-Entscheidung; Fehler intern vermerken |
| Unbekanntes Eingabemuster | Default: `ALLOW`; Output-Guard prüft mit vollem Maßstab |

**Fail-Closed-Priorität:**
```
EXIT > EXTERNAL_REFERRAL > PAUSED > GUARD_BLOCK > ALLOW
```
Bei Unklarheit wird stets der sicherere Zustand bevorzugt.

---

## 11. Operativer Implementierungs-Check

**Alle Fragen müssen mit Nein beantwortet werden.**
Bei Ja: Implementierung verletzt Canon oder Spezifikation ist unvollständig.

| # | Frage | Bei Ja |
|---|---|---|
| 1 | Gibt es einen Pfad, auf dem der LLM-Adapter ohne vorherige Input-Guard-Entscheidung erreicht wird? | Architekturverstoß – Guard vor LLM erzwingen |
| 2 | Gibt es einen Pfad, auf dem LLM-Output die UI ohne Output-Guard-Entscheidung erreicht? | Architekturverstoß – Guard nach LLM erzwingen |
| 3 | Kann die UI einen Safe State überschreiben oder ignorieren? | Architekturverstoß – Kernel als Single Source of Control |
| 4 | Kann ein blockierter Output ohne Kernel-Freigabe erneut versucht werden? | Guard-Verstoß – kein Auto-Retry nach BLOCK |
| 5 | Kann Rohinhalt (Nutzertext, LLM-Antwort) in den persistenten Event-Log gelangen? | Privacy-Verstoß – redaction-first durchsetzen |
| 6 | Gibt es einen Zustand ohne definierten fail-closed-Fallback? | Spezifikationslücke – EXIT als Default ergänzen |
| 7 | Entscheidet der Guard Layer per Inference statt per Regellogik? | Architekturverstoß – deterministischen Guard erzwingen |
| 8 | Hält der LLM-Adapter Session-State oder Safety-Wissen? | Architekturverstoß – Adapter-Grenzen durchsetzen |
| 9 | Ist ein automatischer Re-Entry nach EXIT möglich? | Session-Contract-Verletzung – explizite Nutzeraktion erzwingen |
| 10 | Trifft UI oder LLM eine Safety-Entscheidung? | Architekturverstoß – Kernel-Verantwortung nicht delegieren |
