# ARCHITECTURE_OVERVIEW

Status: aktiv | Owner: Jannek Büngener | Zuletzt geprüft: 2026-03-25

---

## 1. Zweck und Architekturziel

Dieses Dokument definiert den MVP-Architektur-Canon für Traumtänzer: welche Komponenten es gibt, was sie dürfen und was nicht, wie Kontrolle verteilt ist, und wie das System bei Unsicherheit reagiert.

Es ist kein Implementierungsplan und kein Infrastrukturdesign. Es ist operativer Canon: verbindlich für technische Entscheidungen, Prompt-Design, Logging-Konzepte und Provider-Auswahl.

Standardpfad: text-first MVP. Voice ist optional und explizit nachgelagert.

---

## 2. Kernprinzipien

**Kernel ist Single Source of Control.**
Alle sicherheitsrelevanten Entscheidungen laufen durch den Kernel. Weder UI noch LLM treffen finale Safety-Entscheidungen.

**Guards sind deterministisch.**
Der Guard Layer prüft Ein- und Ausgänge mit regelbasierter Logik – nicht durch Modell-Inference. Guardrails, die nur im Prompt leben, sind keine Architektur.

**LLM ist austauschbarer Inferenz-Adapter.**
Das Sprachmodell ist ein Adapter, kein Orchestrator. Es generiert Text auf Basis des zugeführten Kontexts. Es steuert keine Session-Logik, keine Safety-Entscheidungen, keine Persistenz.

**Fail-closed, nicht fail-open.**
Bei Unsicherheit, Guard-Verstoß oder fehlendem Signal fällt das System in einen definierten sicheren Zustand. Es improvisiert nicht.

**Privacy-by-Default strukturell erzwingen.**
Session-Inhalte sind ephemer. Kein Systemteil persistiert Inhalte ohne explizite, dokumentierte Entscheidung. Redaction-first gilt auch für Logs.

**Provider-Agnostik als Strukturprinzip.**
Das System ist so aufgebaut, dass LLM-Provider, Storage-Provider und Infrastruktur wechselbar bleiben. Keine Hartkopplung an einen Provider in Kernel- oder Guard-Logik.

---

## 3. Komponentenmodell

```
[UI / Client]
      |
      v
[Kernel] <---> [Guard Layer]
      |
      v
[LLM-Adapter]   [Voice-Adapter (optional)]
      |
      v
[Event-Log]
```

| Komponente | Rolle | Darf nicht |
|---|---|---|
| **UI / Client** | Eingabe entgegennehmen, Ausgabe darstellen, Exit zugänglich halten | Safety-Entscheidungen treffen, Logs schreiben, Session-State halten |
| **Kernel** | Session-State, Kontrollfluss, Guard-Aufrufe, Safe-State-Übergänge | LLM direkt ansprechen ohne Guard-Prüfung, Inhalte persistieren |
| **Guard Layer** | Input/Output deterministisch prüfen, Safeword erkennen, Trigger-Signale klassifizieren | Modell aufrufen, Entscheidungen per Inference treffen |
| **LLM-Adapter** | Text generieren auf Basis zugeführten Kontexts | Session steuern, Safety entscheiden, Logs schreiben, Persistenz veranlassen |
| **Voice-Adapter** | Audio-Input/Output (optional, MVP-nachgelagert) | Safety-Logik übernehmen, Kernel umgehen |
| **Event-Log** | Systerereignisse append-only und minimal erfassen | Nutzerinhalte loggen, Safety-Events mit Content verknüpfen |

---

## 4. Kernel-Verantwortung

Der Kernel ist die einzige Instanz, die:

- den Session-State hält und übergibt
- Guards vor und nach jeder LLM-Interaktion aufruft
- Safe-State-Übergänge auslöst (Exit, Pause, Session-Abbruch)
- Safeword-Signale verarbeitet und durchsetzt
- entscheidet, was an den LLM-Adapter übergeben wird

Der Kernel ruft das Modell **nicht** auf, ohne vorher den Guard Layer zu passieren. Die Reihenfolge ist fix:

```
Eingabe → Input-Guard → Kernel-Entscheidung → LLM-Adapter → Output-Guard → Ausgabe
```

Wenn der Input-Guard einen Abbruch auslöst, erreicht die Eingabe den LLM-Adapter nicht.
Wenn der Output-Guard eine Antwort zurückhält, erreicht sie die UI nicht.

---

## 5. Guard Layer

Guards sind deterministisch und regelbasiert. Sie treffen Ja/Nein-Entscheidungen auf Basis expliziter Kriterien – keine Inference, kein Probabilistik.

### Input-Guards prüfen:

- Safeword-Erkennung (Wortliste, konfigurierbar)
- Explizite Notfall- oder Krisensprache (Muster, nicht Diagnose)
- Zeichen akuter Dissoziation oder Realitätsverlust (Signalmuster)
- Anfragen nach klinischer Diagnose oder Krisenintervention

### Output-Guards prüfen:

- Enthält die Antwort diagnoseähnliche Aussagen über den Nutzer?
- Enthält die Antwort Bindungssprache oder Companion-Rhetorik?
- Enthält die Antwort Wirksamkeitsbehauptungen?
- Entspricht die Antwort dem aktuellen Session-Safe-State?

### Guard-Entscheidungen:

| Ergebnis | Konsequenz |
|---|---|
| Input: Safeword erkannt | Sofortiger Session-Abbruch, kein LLM-Call |
| Input: Krisensprache erkannt | Session stoppen, Safe State, externer Verweis |
| Input: klar | LLM-Call freigegeben |
| Output: Guard-Verstoß | Antwort zurückhalten, Safe State, neutrale Systemmeldung |
| Output: klar | Antwort an UI weitergeben |

Guards protokollieren nur Ereignistyp und Zeitstempel – keinen Auslösetext, keinen Content.

---

## 6. Adapter-Grenzen

### LLM-Adapter

- Nimmt strukturierten Prompt-Kontext entgegen, gibt generierten Text zurück.
- Kennt keinen Session-State, keine Nutzerhistorie, keine Safety-Entscheidungen.
- Provider-agnostisch: Adapter-Schnittstelle ist unabhängig von konkretem Anbieter.
- Kein LLM-Provider erhält unredacted Session-Inhalte über das für Inference nötige Minimum hinaus.
- Prompt-Konstruktion ist Kernel-Aufgabe, nicht Adapter-Aufgabe.

### Voice-Adapter (optional, MVP-nachgelagert)

- Übernimmt Audio-zu-Text und Text-zu-Audio – nichts weiter.
- Kernel und Guards bleiben identisch, Voice ändert nur den Input/Output-Kanal.
- Voice wird nicht als Standardpfad angenommen. Kein MVP-Architekturentscheid setzt Voice voraus.
- Eigene Datenschutzprüfung für Voice-Provider erforderlich, bevor dieser Adapter aktiviert wird.

### Externe Module (später)

- Neue Adapter (z. B. Journal, Benachrichtigungen) werden nur über definierte Kernel-Schnittstellen angebunden.
- Kein Adapter darf Guards umgehen oder Session-State direkt lesen.

---

## 7. Event-Log-Prinzipien

Der Event-Log ist **append-only**, **redaction-first** und **content-free**.

### Erlaubte Event-Klassen:

| Klasse | Inhalt | Verboten |
|---|---|---|
| `SESSION_START` | Session-ID (pseudonym), Zeitstempel | Nutzeridentität, Eingabetext |
| `SESSION_END` | Session-ID, Zeitstempel, Abschlusstyp (normal/abgebrochen) | Abbruchgrund als Text |
| `GUARD_EVENT` | Session-ID, Zeitstempel, Guard-Typ, Ergebnis (pass/block) | Auslösetext, Nutzerformulierung |
| `SAFE_STATE_TRANSITION` | Session-ID, Zeitstempel, Zielzustand | Ursachen-Text |
| `SYSTEM_ERROR` | Fehler-Code, Zeitstempel | Nutzerinhalte, Prompt-Inhalte |

### Verboten im Event-Log:

- Nutzerinhalte jeder Art (Texte, Reflexionen, Eingaben)
- Prompt-Inhalte oder LLM-Antworten
- Content-Kontext zu Safety-Events
- Verknüpfung von Nutzeridentität mit Inhaltsereignissen

### Retention:

Safety- und Guard-Events: maximal 90 Tage (gemäß Privacy-Canon). System-Error-Logs: maximal 30 Tage.

---

## 8. Safe States und fail-closed Verhalten

### Definierte Safe States:

| Zustand | Auslöser | Systemverhalten |
|---|---|---|
| `PAUSED` | Überforderungssignal erkannt | Session pausieren, keine neuen Inhalte, Orientierungsangebot |
| `EXIT` | Safeword, expliziter Abbruch | Sofortige Session-Beendigung, neutrale Bestätigung, kein Re-Entry ohne Nutzeraktion |
| `EXTERNAL_REFERRAL` | Krisensprache, akute Gefährdung | Session stoppen, externer Verweis, kein inhaltlicher Kommentar |
| `GUARD_BLOCK` | Output-Guard schlägt an | Antwort zurückhalten, neutrale Systemmeldung, kein Retry ohne Kernel-Entscheidung |

### Fail-closed-Regel:

Wenn der Kernel keinen eindeutigen Safe State ermitteln kann – weil ein Guard kein klares Signal liefert, ein Adapter nicht antwortet oder ein unerwarteter Zustand eintritt – fällt das System in `EXIT`. Es gibt keinen Fallback auf „weiter wie bisher".

### Was UI nicht darf:

- Safe States überschreiben oder ignorieren
- Safeword-Verarbeitung übernehmen
- Session nach `EXIT` automatisch fortführen
- Dem Nutzer suggerieren, das System habe „entschieden, dass alles okay ist"

---

## 9. Was explizit nicht Teil des MVP-Canon ist

| Nicht-Ziel | Begründung |
|---|---|
| Runtime-Code oder Build-System | Governance-first; Implementierung folgt dem Canon |
| Konkrete Infrastruktur- oder Hosting-Entscheidung | Provider-agnostisch; wird bei Produktionsstart definiert |
| UI-Design oder UX-Flows | Separater Scope (P1-Roadmap) |
| Voice als Standardpfad | Optional; MVP ist text-first |
| Persistenz von Session-Inhalten | Privacy-Canon: kein Default-Speichern |
| LLM-Provider-Festlegung | Adapter-Grenze hält Optionen offen |
| Guardrails ausschließlich im Prompt | Prompt-only Safety ist keine Architektur |
| Companion-Design oder Bindungsmechanik | Verboten per Claims-Canon |

---

## 10. Operativer Kurz-Check für künftige Architekturentscheidungen

Vor jeder neuen Komponente, Schnittstelle, Integration oder technischen Entscheidung:

1. Ist klar, welche Komponente diese Entscheidung trifft – und dass es nicht UI oder LLM ist?
2. Läuft jede LLM-Interaktion durch Input- und Output-Guard?
3. Ist fail-closed definiert: Was passiert, wenn diese Komponente versagt oder kein Signal liefert?
4. Bleibt der LLM-Adapter austauschbar – gibt es eine Provider-Hartkopplung?
5. Enthält kein Log in diesem Flow Nutzerinhalte oder Content-Kontext?
6. Ist Session-Content ephemer – oder gibt es eine explizite, dokumentierte Persistenzentscheidung?
7. Ist Voice eine optionale Erweiterung, nicht eine Grundannahme?
8. Respektiert diese Entscheidung Claims-, Safety- und Privacy-Canon?

Wenn eine dieser Fragen nicht sauber beantwortet werden kann: Entscheidung zurückstellen und Canon-Konflikt klären.
