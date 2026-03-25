# TEXT_FIRST_RUNTIME_FLOW

Status: aktiv | Owner: Jannek Büngener | Zuletzt geprüft: 2026-03-25

Basis: KERNEL_GUARD_CONTRACTS §3–§10, ARCHITECTURE_OVERVIEW §4–§8,
GUARDRAILS_CONTENT_POLICY §3–§7, UX_CORE_SEQUENCE §3–§7, SAFETY_PLAYBOOK §3–§6

---

## 1. Zweck und Geltungsbereich

Dieses Dokument spezifiziert den minimalen Laufzeitfluss einer text-first Session für
den Traumtänzer MVP. Es baut direkt auf KERNEL_GUARD_CONTRACTS auf und operationalisiert:

- den Happy-Path durch alle Phasen (ENTRY → CHECK_IN → REFLECTION → EXIT)
- alle relevanten Safe-State-Pfade (Safeword, Referral, Pause, Guard-Block, Fehler)
- die minimalen Laufzeit-Payloads zwischen den Schichten
- den Constraint-Flag-Mechanismus für erhöhten Output-Guard-Maßstab
- vordefinierte neutrale Antwortklassen für Safe States
- Re-Entry- und Fortsetzungslogik

Es ist keine vollständige Runtime-Implementierung und kein Infrastrukturentscheid.
Kein Runtime-Code. Provider-agnostisch. Framework-neutral.

---

## 2. Happy Path der text-first Session

### Phasenzuordnung

```
SESSION_STARTED
     ↓
  [ENTRY]          Predefined Kernel-Text, kein LLM-Call
     ↓  (explizites Nutzer-Opt-in)
  [CHECK_IN]       Frage an Nutzer (predefined oder LLM+Guards)
     ↓  (explizite Nutzerbestätigung)
  [REFLECTION]     LLM + vollständiger Guard-Zyklus (wiederholbar)
     ↓  (Nutzer beendet oder System schließt)
  [EXIT]
     ↓
SESSION_ENDED
```

Jeder Phasenübergang erfordert eine explizite Nutzeraktion. Ausbleibendes Signal ist kein Go.

---

### ENTRY

| Dimension | Wert |
|---|---|
| Auslöser | Neue Session initialisiert (`SESSION_STARTED` geloggt) |
| Kernel-Aktion | Predefined Onboarding-Text ausgeben (kein LLM-Call) |
| Guard-Prüfung | Input Guard prüft Nutzer-Antwort auf Opt-in |
| Erlaubtes Ergebnis | `ALLOW` (Opt-in erkannt) → Transition zu `CHECK_IN`; `BLOCK_EXIT` → `EXIT` |
| Verbotenes Verhalten | Auto-Weiter ohne Nutzerbestätigung |
| Kernel-Entscheidung | Übergang zu `CHECK_IN` erst nach ALLOW + `PHASE_TRANSITION_PENDING`-Auflösung |

Entry-Text ist ein Predefined Kernel-String, nicht LLM-generiert. Er enthält KI-Transparenz, Systemgrenzen, Safeword-Einführung und Opt-in-Frage (→ UX_CORE_SEQUENCE §4).

---

### CHECK_IN

| Dimension | Wert |
|---|---|
| Auslöser | Transition aus ENTRY nach Nutzer-Opt-in |
| Kernel-Aktion | Check-in-Frage ausgeben (predefined oder LLM mit Guards) |
| Guard-Prüfung | Input Guard prüft Nutzerantwort vollständig |
| Erlaubtes Ergebnis | `ALLOW` → Transition zu `REFLECTION`; `BLOCK_PAUSE` → `PAUSED`; `BLOCK_REFER` → `EXTERNAL_REFERRAL`; `BLOCK_EXIT` → `EXIT` |
| Verbotenes Verhalten | Weiter nach Belastungssignal; Auto-Weiter ohne Bestätigung |
| Kernel-Entscheidung | `PHASE_TRANSITION_PENDING`-Flag aktiv, bis Nutzerantwort explizit Bereitschaft signalisiert |

---

### REFLECTION (wiederholbar)

| Dimension | Wert |
|---|---|
| Auslöser | Transition aus CHECK_IN nach Nutzerbestätigung |
| Kernel-Aktion | Nutzereingabe → Input Guard → (ALLOW) → Prompt konstruieren → LLM → Output Guard → UI |
| Guard-Prüfung | Input Guard + Output Guard bei jedem Zyklus |
| Constraint-Flags | Aktive Flags aus vorherigen Guard-Entscheidungen fließen in Output Guard |
| Erlaubtes Ergebnis | `ALLOW`+`ALLOW` → Ausgabe an UI; alle anderen → Safe State (→ §6) |
| Verbotenes Verhalten | Vertiefung ohne Nutzerinitiative; Vertiefung bei Überforderungssignal |
| Zyklus | Jede Nutzereingabe startet einen neuen vollständigen Guard-Zyklus |

---

### EXIT

| Dimension | Wert |
|---|---|
| Auslöser | Jede `BLOCK_EXIT`-Entscheidung, expliziter Nutzerabbruch, normaler Sessionabschluss |
| Kernel-Aktion | `SESSION_ENDED` loggen, `NEUTRAL_EXIT_CONFIRMATION` ausgeben |
| Guard-Prüfung | keine weitere |
| Re-Entry | Nur über neue Session-Initiierung (neues `SESSION_STARTED`) |
| Verbotenes Verhalten | Inhaltlicher Kommentar zur Unterbrechung; Auto-Reentry |

---

## 3. Laufzeit-Payloads zwischen Schichten

Alle Payloads, die Nutzertext oder LLM-Output enthalten, sind **transient** (nur Kernel-RAM). Sie dürfen den Event-Log nicht erreichen.

---

### UI → Kernel

```
{
  session_id:   string,      // pseudonym
  input_text:   string,      // TRANSIENT – niemals persistieren
  timestamp:    ISO8601
}
```

Verboten: Nutzeridentität, Metadaten über den Nutzer, vorherige Eingaben als Kontext.

---

### Kernel → Input Guard

```
{
  session_id:      string,
  current_state:   StateEnum,
  input_text:      string,          // TRANSIENT – nur für Guard-Prüfung
  constraint_flags: ConstraintFlagEnum[]  // aktive Flags aus Session-State
}
```

Verboten: Nutzeridentität, LLM-Historien, Safety-Event-Inhalte.

---

### Input Guard → Kernel

```
{
  decision:        InputGuardDecisionEnum,
  guard_category:  CategoryEnum | null
}
```

Kein Freitext. Kein Nutzerinhalt. Nur enums.

---

### Kernel → LLM-Adapter

```
{
  prompt_context:  string,          // TRANSIENT – Kernel-konstruierter Kontext, kein Rohtext
  session_phase:   StateEnum,       // für Prompt-Framing (keine Safety-Entscheidungen)
  constraint_flags: ConstraintFlagEnum[]  // Framing-Hinweise, keine Guard-Entscheidungen
}
```

Verboten: session_id, Nutzeridentität, Safety-Event-Daten, Guard-Ergebnisse,
Safeword-Konfiguration, roher Nutzertext ohne Kernel-Verarbeitung.

Der LLM-Adapter nimmt `constraint_flags` nur als Framing-Hinweis für den Prompt entgegen.
Er trifft keine Safety-Entscheidung auf ihrer Basis.

---

### LLM-Adapter → Kernel

```
{
  generated_text: string   // TRANSIENT – nur für Output-Guard
}
```

Verboten: Session-State-Änderungen, Log-Writes, Persistenzoperationen.

---

### Kernel → Output Guard

```
{
  session_id:      string,
  current_state:   StateEnum,
  generated_text:  string,          // TRANSIENT
  constraint_flags: ConstraintFlagEnum[]  // erhöhter Maßstab wenn gesetzt
}
```

Verboten: Nutzeridentität, Input-Guard-Rohdaten, Safety-Event-Inhalte.

---

### Output Guard → Kernel

```
{
  decision:        OutputGuardDecisionEnum,
  violation_type:  ViolationTypeEnum | null
}
```

Kein Freitext. Kein Nutzerinhalt. Nur enums.

---

### Kernel → UI (Happy Path)

```
{
  response_text:      string,       // LLM-Output der Guards passiert hat
  current_state:      StateEnum,
  available_actions:  ActionEnum[]  // z. B. [EXIT_AVAILABLE, CONTINUE_AVAILABLE]
}
```

---

### Kernel → UI (Safe State)

```
{
  response_class: NeutralResponseClassEnum,  // predefinierter Kernel-Text, KEIN LLM
  response_text:  string,                    // aus Kernel-Textbank, nicht generiert
  current_state:  StateEnum
}
```

---

### Kernel → Event-Log

Gemäß Event-Contracts (KERNEL_GUARD_CONTRACTS §4). Nur persistierbare Events:
`SESSION_STARTED`, `SESSION_ENDED`, `INPUT_GUARD_RESULT`, `OUTPUT_GUARD_RESULT`,
`SAFE_STATE_TRANSITION`, `SYSTEM_ERROR`.

Nicht persistierbar: `USER_INPUT_RECEIVED`, `LLM_OUTPUT_RECEIVED`.

---

## 4. Guard-Flags / Constraint-Annotation

Constraint-Flags sind transiente Session-State-Felder im Kernel. Sie werden nicht persistiert und nicht geloggt.

### Definierte Flags

| Flag | Gesetzt wenn | Wirkung |
|---|---|---|
| `INTERPRETATION_REQUEST_ACTIVE` | Input Guard gibt `RESTRICT_OUTPUT` zurück | Output Guard prüft auf Wahrheitsanspruch und Deutungsautorität mit erhöhtem Maßstab |
| `DISTRESS_CONTEXT_ACTIVE` | Input Guard gibt `BLOCK_PAUSE` zurück und Session wird aus `PAUSED` fortgesetzt | Output Guard blockiert jede Vertiefung; nur Orientierungsangebote erlaubt |
| `BOUNDARY_CONTEXT_ACTIVE` | Input Guard gibt `BLOCK_BOUNDARY` zurück und Kernel entscheidet `PAUSED` statt `EXIT` | Output Guard prüft auf Diagnose-Nähe und Grenzüberschreitung besonders streng |
| `PHASE_TRANSITION_PENDING` | Kernel wartet auf explizites Nutzer-Opt-in vor Phasenübergang | Input Guard prüft Eingabe primär auf Opt-in-Signal; kein LLM-Call bis Opt-in bestätigt |

### Lebenszyklus

- Flags werden beim Eintritt in einen Safe State gesetzt.
- Flags werden beim Eintritt in `EXIT` oder `EXTERNAL_REFERRAL` vollständig gelöscht.
- `PHASE_TRANSITION_PENDING` wird nach bestätigtem Opt-in gelöscht.
- Flags überleben `PAUSED` → `REFLECTION`-Transition (der Kontext bleibt aktiv).

---

## 5. Neutrale Systemantwortklassen

Neutrale Antworten kommen **niemals vom LLM**. Sie sind vordefinierte Kernel-Strings.
Sie werden nicht durch Guards geleitet (sie enthalten keinen LLM-Output).

| Klasse | Zweck | Erlaubter Ton | Was nie enthalten sein darf | Einsatzbedingung |
|---|---|---|---|---|
| `NEUTRAL_EXIT_CONFIRMATION` | Session-Abschluss bestätigen | Ruhig, neutral, kurz | Kommentar zur Unterbrechung, Bindungsrhetorik, Cliffhanger | Safeword, expliziter Abbruch, normaler Exit |
| `NEUTRAL_PAUSE_RESPONSE` | Pause einleiten, Orientierung anbieten | Ruhig, klar, offen | Neue Inhalte, Deutungen, Diagnose-Nähe | `BLOCK_PAUSE`, `DISTRESS_CONTEXT_ACTIVE` |
| `NEUTRAL_REFERRAL_RESPONSE` | Auf externe Hilfe verweisen | Sachlich, ohne Dringlichkeitsbewertung | Inhaltlicher Kommentar, Einschätzung des Zustands | `BLOCK_REFER`, Krisensprache erkannt |
| `NEUTRAL_GUARD_BLOCK_RESPONSE` | Blockierten Output ohne Erklärung ersetzen | Neutral, unspezifisch | Hinweis auf was geblockt wurde, Entschuldigung, Retry-Aufforderung | Output Guard `BLOCK` |
| `NEUTRAL_ERROR_FAIL_CLOSED_RESPONSE` | Systemfehler ohne Nutzerinhalt kommunizieren | Neutral, schlicht | Fehlerbeschreibung, Systeminterna | Guard-Timeout, Adapter-Fehler, `ERROR_FAIL_CLOSED` |

Beispielformulierungen (illustrativ, kein finaler UX-Text):
- `NEUTRAL_EXIT_CONFIRMATION`: „Ich stoppe hier. Du kannst jederzeit neu beginnen."
- `NEUTRAL_PAUSE_RESPONSE`: „Ich mache hier eine Pause. Wie geht es dir gerade – nicht mit dem Thema, sondern jetzt? Du kannst jederzeit stoppen."
- `NEUTRAL_REFERRAL_RESPONSE`: „Wenn du gerade Unterstützung brauchst, erreichst du die Telefonseelsorge kostenfrei unter 0800 111 0 111. Bei akuter Not: Notruf 112."
- `NEUTRAL_GUARD_BLOCK_RESPONSE`: „Ich kann darauf gerade nicht eingehen. Du kannst weitermachen oder stoppen."
- `NEUTRAL_ERROR_FAIL_CLOSED_RESPONSE`: „Ein Fehler ist aufgetreten. Ich schließe hier."

---

## 6. Guard-Block-, Pause-, Referral- und Exit-Flüsse

### Safeword

```
Trigger:   Nutzer gibt Safeword ein
Guard:     Input Guard → BLOCK_EXIT
Kernel:    Kein LLM-Call; state → EXIT
Antwort:   NEUTRAL_EXIT_CONFIRMATION
Logging:   INPUT_GUARD_RESULT (decision=BLOCK_EXIT, category=SAFEWORD)
           SAFE_STATE_TRANSITION (→EXIT)
           SESSION_ENDED (end_type=SAFEWORD)
Re-Entry:  Nur neue Session (neues SESSION_STARTED)
```

---

### Expliziter Exit

```
Trigger:   Nutzer signalisiert Abbruch explizit (ohne Safeword)
Guard:     Input Guard → BLOCK_EXIT
Kernel:    Kein LLM-Call; state → EXIT
Antwort:   NEUTRAL_EXIT_CONFIRMATION
Logging:   wie Safeword, end_type=NORMAL oder GUARD_ABORT je nach Kontext
Re-Entry:  Nur neue Session
```

---

### Krisensprache / Referral

```
Trigger:   Input Guard erkennt Krisensprache / akute Gefährdung
Guard:     Input Guard → BLOCK_REFER
Kernel:    Kein LLM-Call; state → EXTERNAL_REFERRAL
Antwort:   NEUTRAL_REFERRAL_RESPONSE (enthält Notruf 112, TelefonSeelsorge)
Logging:   INPUT_GUARD_RESULT (decision=BLOCK_REFER, category=CRISIS)
           SAFE_STATE_TRANSITION (→EXTERNAL_REFERRAL)
           SESSION_ENDED (end_type=REFERRAL)
Re-Entry:  Nur über neue Session; kein automatischer Re-Entry
```

---

### Überforderung / Pause

```
Trigger:   Input Guard erkennt Dissoziation oder eskalierende Distress-Signale
Guard:     Input Guard → BLOCK_PAUSE
Kernel:    Kein LLM-Call; state → PAUSED; Flag DISTRESS_CONTEXT_ACTIVE setzen
Antwort:   NEUTRAL_PAUSE_RESPONSE
Logging:   INPUT_GUARD_RESULT (decision=BLOCK_PAUSE, category=DISTRESS/DISSOCIATION)
           SAFE_STATE_TRANSITION (→PAUSED)
Re-Entry:  state → REFLECTION nur nach explizitem Nutzer-Go + Kernel-Freigabe;
           DISTRESS_CONTEXT_ACTIVE bleibt bis EXIT aktiv
```

---

### Output-Guard blockt

```
Trigger:   LLM-Output enthält verbotenes Muster (→ GUARDRAILS §4, §8)
Guard:     Output Guard → BLOCK
Kernel:    Output verwerfen; state → GUARD_BLOCK
Antwort:   NEUTRAL_GUARD_BLOCK_RESPONSE
Logging:   OUTPUT_GUARD_RESULT (decision=BLOCK, violation_type=<enum>)
           SAFE_STATE_TRANSITION (→GUARD_BLOCK)
Re-Entry:  state → REFLECTION nach Kernel-Entscheidung + neuem Nutzer-Go;
           kein automatischer Retry; blockierten Output nicht recyceln
```

---

### Adapter- oder Guard-Fehler (fail-closed)

```
Trigger:   Guard gibt kein Ergebnis / Timeout; Adapter gibt keinen Output; Kernel-Fehler
Guard:     ERROR_FAIL_CLOSED (Input oder Output Guard)
Kernel:    Kein LLM-Call (oder Output verwerfen); state → EXIT
Antwort:   NEUTRAL_ERROR_FAIL_CLOSED_RESPONSE
Logging:   SYSTEM_ERROR (error_code=<code>, component=<enum>)
           SAFE_STATE_TRANSITION (→EXIT)
           SESSION_ENDED (end_type=SYSTEM_ERROR)
Re-Entry:  Nur neue Session
```

---

## 7. Re-Entry- und Fortsetzungslogik

| Zustand | Fortsetzung erlaubt? | Bedingung |
|---|---|---|
| `EXIT` | Nein (selbe Session) | Nur neue Session (neues `SESSION_STARTED`) |
| `EXTERNAL_REFERRAL` | Nein (selbe Session) | Nur neue Session |
| `PAUSED` | Ja | Explizite Nutzerbestätigung + Kernel setzt state=REFLECTION; `DISTRESS_CONTEXT_ACTIVE` bleibt |
| `GUARD_BLOCK` | Ja | Kernel-Entscheidung + neues Nutzer-Go; kein Auto-Retry |
| `ERROR_FAIL_CLOSED` | Nein | Nur neue Session |

**Allgemeine Regeln:**
- Ausbleibendes Nutzer-Signal ist kein Go.
- Kein stilles Überspringen von Entry- oder Check-in-Gates, auch bei Fortführung aus `PAUSED`.
- `DISTRESS_CONTEXT_ACTIVE`-Flag überlebt `PAUSED → REFLECTION`-Transition.
- Neue Session = neues `SESSION_STARTED` + Zustand beginnt bei `ENTRY`.

---

## 8. Event-Payload-Disziplin

Operationalisiert KERNEL_GUARD_CONTRACTS §4 für den Laufzeitkontext.

### Persistierbare Events – minimale Felder

| Event | Pflichtfelder | Optionale Felder | Verboten |
|---|---|---|---|
| `SESSION_STARTED` | session_id, timestamp | – | Nutzer-ID, Startinhalt |
| `SESSION_ENDED` | session_id, timestamp, end_type | last_state | Ursachentext, Nutzerinhalt |
| `INPUT_GUARD_RESULT` | session_id, timestamp, decision, guard_category | – | Auslösetext, Nutzerformulierung |
| `OUTPUT_GUARD_RESULT` | session_id, timestamp, decision | violation_type (nur bei BLOCK) | Ausgabetext, LLM-Output |
| `SAFE_STATE_TRANSITION` | session_id, timestamp, from_state, to_state, trigger_event | – | Ursachentext |
| `SYSTEM_ERROR` | session_id, timestamp, error_code, component | – | Nutzerinhalt, Prompt, Output |

### Nur im RAM (niemals persistieren)

| Signal | Warum nicht persistieren |
|---|---|
| `USER_INPUT_RECEIVED` (mit input_text) | Enthält Nutzertext / Trauminhalt |
| `LLM_OUTPUT_RECEIVED` (mit generated_text) | Enthält LLM-Output |
| Kernel → Input Guard (mit input_text) | Enthält Nutzertext |
| Kernel → Output Guard (mit generated_text) | Enthält LLM-Output |
| Kernel → LLM-Adapter (mit prompt_context) | Enthält strukturierten Prompt mit Nutzerinhalt |

### Constraint-Flags

Constraint-Flags sind transient im Session-State des Kernels. Sie werden:
- nicht geloggt
- nicht an externe Systeme übertragen
- nicht persistiert
- beim Session-Ende vollständig gelöscht

---

## 9. Minimaler Sequenzablauf

Nummerierte Sequenz für den Happy Path (ENTRY → CHECK_IN → REFLECTION-Zyklus → EXIT):

```
 1. [System]      Session initialisieren → SESSION_STARTED → Event-Log
 2. [Kernel]      state = ENTRY; Predefined Entry-Text → UI (kein LLM)
 3. [UI]          Nutzer liest Onboarding, sendet Opt-in
 4. [Kernel]      Input Guard aufrufen (state=ENTRY, text=opt-in)
 5. [Input Guard] → ALLOW (guard_category=ALLOW)
 6. [Kernel]      INPUT_GUARD_RESULT → Event-Log
                  PHASE_TRANSITION_PENDING auflösen
                  state = CHECK_IN
                  SAFE_STATE_TRANSITION → Event-Log
 7. [Kernel]      Check-in-Frage → UI (predefined oder LLM+Guards)
 8. [UI]          Nutzer antwortet auf Check-in
 9. [Kernel]      Input Guard aufrufen (state=CHECK_IN, text=antwort)
10. [Input Guard] → ALLOW
11. [Kernel]      INPUT_GUARD_RESULT → Event-Log
                  state = REFLECTION
                  SAFE_STATE_TRANSITION → Event-Log
12. [UI]          Nutzer bringt Material ein (Bild, Erinnerung, Eindruck)
13. [Kernel]      Input Guard aufrufen (state=REFLECTION, text=eingabe)
14. [Input Guard] → ALLOW (oder → Safe State, → §6)
15. [Kernel]      INPUT_GUARD_RESULT → Event-Log
                  Prompt konstruieren (strukturierter Kontext)
                  LLM-Adapter aufrufen
16. [LLM-Adapter] → generated_text (TRANSIENT)
17. [Kernel]      Output Guard aufrufen (generated_text, constraint_flags)
18. [Output Guard]→ ALLOW (oder BLOCK → §6)
19. [Kernel]      OUTPUT_GUARD_RESULT → Event-Log
                  response_text → UI
20. [UI]          Nutzer setzt fort oder beendet  ← Zurück zu Schritt 12 oder ↓
21. [Kernel]      Input Guard → BLOCK_EXIT (Exit-Signal erkannt)
22. [Kernel]      INPUT_GUARD_RESULT → Event-Log
                  state = EXIT
                  SAFE_STATE_TRANSITION → Event-Log
                  NEUTRAL_EXIT_CONFIRMATION → UI
                  SESSION_ENDED → Event-Log
```

---

## 10. Implementierungs-Check

**Alle Fragen müssen mit Nein beantwortet werden.**
Bei Ja: Flow nicht implementierungsreif oder Implementierung verletzt Canon.

| # | Frage | Bei Ja |
|---|---|---|
| 1 | Kann eine Nutzereingabe den LLM ohne vorherige Input-Guard-Entscheidung erreichen? | Architekturverstoß |
| 2 | Kann ein blockierter Output trotzdem an die UI gelangen? | Guard-Verletzung |
| 3 | Kann ein Safe State ohne Kernel gesetzt oder überschrieben werden (z. B. durch UI)? | Architekturverstoß |
| 4 | Kann ein persistierter Event Rohinhalt (Nutzertext, LLM-Output) enthalten? | Privacy-Verstoß |
| 5 | Ist nach EXIT oder EXTERNAL_REFERRAL ein automatischer Re-Entry möglich? | Session-Contract-Verletzung |
| 6 | Ist nach GUARD_BLOCK ein automatischer LLM-Retry ohne Kernel-Entscheidung möglich? | Guard-Verletzung |
| 7 | Werden Constraint-Flags persistiert oder geloggt? | Privacy-Verstoß |
| 8 | Kommen neutrale Systemantworten vom LLM statt aus vordefiniertem Kernel-Text? | Architekturverstoß |
| 9 | Gibt es einen Fehlerpfad ohne definierten fail-closed-Fallback? | Spezifikationslücke |
| 10 | Kann die Phase REFLECTION ohne vorherigen expliziten Check-in-Abschluss erreicht werden? | UX-Contract-Verletzung |
