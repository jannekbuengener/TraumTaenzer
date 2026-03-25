# PROMPT_CONSTRUCTION_RULES

Status: aktiv | Owner: Jannek Büngener | Zuletzt geprüft: 2026-03-25

Basis: TEXT_FIRST_RUNTIME_FLOW §3–§4, KERNEL_GUARD_CONTRACTS §5–§8,
ARCHITECTURE_OVERVIEW §6, PRIVACY_BY_DESIGN §2–§5, GUARDRAILS_CONTENT_POLICY §2–§3,
CLAIMS_FRAMEWORK §1–§8, SYSTEM_INVARIANTS A-1–A-4, P-1–P-3

---

## 1. Zweck und Geltungsbereich

Dieses Dokument beschreibt die minimale Prompt-Konstruktionslogik für den text-first MVP.
Es definiert, wie der Kernel den Prompt-Kontext vor dem LLM-Adapter-Call zusammenbaut,
welche Inhalte reduziert oder entfernt werden müssen, und wann kein Prompt gebaut
werden darf.

Es ist:
- eine Implementierungsvorlage – kein Runtime-Code
- provider-agnostisch und framework-neutral
- kein Prompt-Optimierungsrezept für einen bestimmten Anbieter
- kein Ersatz für Guards (Safety-Logik gehört in Guards, nicht in Prompts)

Es setzt direkt auf KERNEL_GUARD_CONTRACTS §5–§8 und TEXT_FIRST_RUNTIME_FLOW §3–§4 auf.

---

## 2. Grundprinzipien der Prompt-Konstruktion

| Prinzip | Bedeutung |
|---|---|
| **minimal necessary context only** | Nur was für den aktuellen LLM-Call technisch nötig ist. Kein „könnte nützlich sein". |
| **redaction before adapter** | Alles wird vor Adapter-Übergabe auf Notwendigkeit geprüft. Im Zweifel: weglassen. |
| **kernel constructs, adapter does not** | Der Adapter bekommt fertigen Kontext. Er erfindet keine Prompt-Struktur. |
| **static rules > improvisation** | Systeminstruktionen sind feste Regeln, kein freier Text. Keine kreativen Selbst-Prompt-Erweiterungen. |
| **no memory illusion** | Der Kernel erzeugt keine Illusion von Gedächtnis über Sitzungsgrenzen. |
| **no hidden user profiling** | Keine akkumulierten Nutzercharakterisierungen, keine impliziten Profile im Prompt. |
| **no prompt-only safety dependency** | Guards prüfen Output. Sicherheitsregeln im Prompt sind Unterstützung, kein Ersatz für Guards. |
| **fail-closed on unclear context** | Unvollständiger, unsauberer oder widersprüchlicher Kontext → kein Prompt, kein LLM-Call. |

---

## 3. Zulässige Prompt-Bausteine

| Baustein | Zweck | Statisch/Dynamisch | Quelle | Minimierungsregel | Transient-only |
|---|---|---|---|---|---|
| **system_rule_block** | System-Charakter, Nicht-Therapie-Stance, Meaning-through-Experience, Perspektiven-Rahmung | Statisch (pro Phase-Typ) | Kernel-Konfiguration | Keine Nutzeranpassung; feste Regeln | ja |
| **phase_context** | Aktuelle Phase als Kontextmarker | Dynamisch (Phase) | Kernel Session-State | Nur Phase-Name und Phase-Typ; kein Nutzerinhalt | ja |
| **guard_constraint_block** | Aktive Verhaltensbeschränkungen aus Constraint-Flags | Dynamisch (Flags) | Kernel Session-State | Nur Verhaltenslimits, keine Diagnosen (→ §6) | ja |
| **user_input_excerpt** | Eng begrenzter Ausschnitt der aktuellen Nutzereingabe | Dynamisch (Input) | Kernel nach Redaction | Nur aktuelle Nachricht; keine Vorgeschichte; max. Längenbegrenzung | ja |
| **response_shape_instruction** | Minimale Anweisung zur Antwortform (Frage, Perspektive, Rahmung) | Statisch (pro Phase-Typ) | Kernel-Konfiguration | Keine nutzer- oder sessionspezifischen Anweisungen | ja |

**Alle Bausteine sind transient.** Kein Baustein darf persistiert oder geloggt werden.

---

## 4. Verbotene Prompt-Bausteine

Was **nicht** in einen Prompt darf – ohne Ausnahme:

| Verbotener Baustein | Warum verboten |
|---|---|
| Rohhistorie mehrerer Nachrichten ohne enge Notwendigkeit | Implizites Profiling, unnötige Datenmenge |
| Akkumulierte Nutzercharakterisierung | Profiling, Diagnose-Nähe |
| Psychologische oder diagnostische Zuschreibungen | CLAIMS §3, GUARDRAILS §4 |
| Guard-/Safety-Event-Inhalte mit Content-Bezug | Privacy-Canon P-3, KERNEL_GUARD §4 |
| Companion- oder Bindungsinstruktionen | CLAIMS §4, SAFETY §2 |
| Wahrheitsbehauptungen über Nutzer oder Symbolik | CLAIMS §8, GUARDRAILS §4 |
| Personenbezogene oder sensible Metaattribute (Alter, Diagnosen, Lebenssituation) | Privacy-Canon P-1, DSGVO Art. 9-Risiko |
| Unredigierte Traumtext-Sammlungen mehrerer Sessions | PRIVACY §4, ephemere Content-Pflicht |
| Anweisungen, die Guards ersetzen sollen | ARCHITECTURE §2; Guards sind nicht im Prompt |
| Alles, was nur „nice to have" statt technisch notwendig ist | minimal necessary context |

---

## 5. Redaction- und Minimierungsregeln vor Adapter-Übergabe

Dies ist die operative Kernregel für Prompt-Konstruktion.

### 5.1 user_input_excerpt

| Regel | Vorgabe |
|---|---|
| Umfang | Nur aktuelle Nutzereingabe (eine Nachricht) |
| Vorgeschichte | Nicht erlaubt, außer ein eng begrenztes, zwingend nötiges Kontextzitat (maximal 1–2 Sätze, explizit als Kontext markiert) |
| Länge | Begrenzt auf implementierungsseitig festgelegte Maximallänge (z. B. 1000 Zeichen) |
| Wenn Rohtext sicherheitskritische Signale enthält | Kein Prompt; Input Guard hätte zuerst zu blockieren; falls trotzdem erreicht → fail-closed |
| Wenn Rohtext eindeutig Art.-9-relevante Inhalte enthält | Nicht in Prompt; Redaction durch Kürzung oder Abstraktion; im Zweifel kein LLM-Call |

### 5.2 session_history (Keine Standardpersistenz)

Standardmäßig enthält der Prompt **keine** Sitzungshistorie. Jeder LLM-Call arbeitet auf Basis der aktuellen Eingabe und des Systemkontexts.

Ausnahme: Wenn ein begrenzter, eng notwendiger Kontext aus der laufenden Session (kein persistierter Inhalt) benötigt wird, gilt:
- maximal 1–2 vorherige Austausche
- nur strukturell notwendig, nicht als Vertiefungskontext
- niemals als Nutzer-Profil oder akkumulierte Charakterisierung

### 5.3 Redaction-Entscheidungsbaum

```
Kann dieser Inhalt weglassen werden?
  → Ja: weglassen (minimal necessary)
  → Nein: Ist er roh oder sensitiv?
      → Ja: Kann er abstrahiert/gekürzt werden?
          → Ja: abstrahieren/kürzen
          → Nein: kein Prompt, kein LLM-Call
      → Nein: In zugehörigen Slot einfügen
```

### 5.4 Wann kein Prompt gebaut werden darf

- Aktiver Safe State (`EXIT`, `EXTERNAL_REFERRAL`, `GUARD_BLOCK`, `PAUSED` ohne Nutzer-Go)
- `PHASE_TRANSITION_PENDING` aktiv und kein Opt-in bestätigt
- Pflichtslot `user_input_excerpt` nicht safe reduzierbar
- Phase unbekannt oder undefined
- Widersprüchliche Constraint-Flags ohne auflösbare Priorität
- Redaction schlägt fehl oder ist unsicher

---

## 6. Umgang mit Constraint-Flags im Prompt

Constraint-Flags (→ TEXT_FIRST_RUNTIME_FLOW §4) steuern Begrenzungen im guard_constraint_block.
Sie werden niemals als Nutzercharakterisierungen oder psychologische Zustandsbeschreibungen formuliert.

| Flag | Erlaubte Formulierung im guard_constraint_block | Verbotene Formulierung |
|---|---|---|
| `INTERPRETATION_REQUEST_ACTIVE` | „Biete ausschließlich als mögliche Perspektive an, niemals als Wahrheit." | „Der Nutzer möchte Deutungen – geh darauf ein." |
| `DISTRESS_CONTEXT_ACTIVE` | „Kein neues Inhaltsmaterial. Nur ruhige, orientierende Sprache. Kein Vertiefen." | „Der Nutzer ist belastet – sei einfühlsam." |
| `BOUNDARY_CONTEXT_ACTIVE` | „Lehne Diagnose- oder Therapieanfragen ohne Bewertung ab. Weise auf Systemgrenzen hin." | „Der Nutzer ist in einer Grenzsituation – handle vorsichtig." |
| `PHASE_TRANSITION_PENDING` | Kein LLM-Call. Predefined-Text-Pfad. | – |

**Regel:** Flags benennen Verhaltenslimits – keine Aussagen über den Nutzer, seinen Zustand oder seine Absicht.

---

## 7. Minimale Prompt-Slots für text-first MVP

Provider-agnostischer Slot-Rahmen. Die genaue technische Repräsentation (Rollen, Formate) ist implementierungsseitig zu entscheiden.

### `system_rule_block` (Pflicht)

| Dimension | Vorgabe |
|---|---|
| Zweck | Systemidentität, Rolle, Grenzen, Nicht-Therapie-Stance, Perspektiven-Rahmungsregel |
| Statisch/Dynamisch | Statisch pro Phase-Typ |
| Zulässiger Inhalt | Was das System ist (KI-Reflexionsformat), was es nicht ist (kein Therapeut, kein Krisenformat), Grundregeln für Perspektiven-Framing |
| Verbotener Inhalt | Companion-Sprache, Heilversprechen, Wahrheitsansprüche, Diagnose-Sprache, emotionale Bindungsanweisungen |

---

### `phase_context` (Pflicht)

| Dimension | Vorgabe |
|---|---|
| Zweck | Aktuelle Phase als minimaler Framing-Marker |
| Statisch/Dynamisch | Dynamisch (Phase) |
| Zulässiger Inhalt | Phase-Name (z. B. „CHECK_IN", „REFLECTION"), kurzer neutraler Phasen-Hint |
| Verbotener Inhalt | Nutzerinhalte, frühere Antworten, Session-Muster |

---

### `guard_constraint_block` (Optional; Pflicht wenn Flags aktiv)

| Dimension | Vorgabe |
|---|---|
| Zweck | Aktive Verhaltenslimits aus Constraint-Flags |
| Statisch/Dynamisch | Dynamisch (Flags) |
| Zulässiger Inhalt | Verhaltensregeln als technische Direktiven (→ §6) |
| Verbotener Inhalt | Psychologische Zustandsaussagen über den Nutzer, Diagnose-Nähe, freie Interpretation der Flags |

Wenn keine Flags aktiv: Slot leer lassen oder weglassen.

---

### `user_input_excerpt` (Pflicht für REFLECTION; optional für CHECK_IN)

| Dimension | Vorgabe |
|---|---|
| Zweck | Minimale aktuelle Nutzereingabe als Reaktionsbasis |
| Statisch/Dynamisch | Dynamisch (Input nach Redaction) |
| Zulässiger Inhalt | Reduzierter, aktueller Eingabeausschnitt (→ §5.1) |
| Verbotener Inhalt | Rohhistorie, akkumulierter Kontext, Art.-9-relevanter Rohtext, sicherheitskritische Signale |

---

### `response_shape_instruction` (Pflicht)

| Dimension | Vorgabe |
|---|---|
| Zweck | Minimale Anweisung zur Antwortform |
| Statisch/Dynamisch | Statisch pro Phase-Typ |
| Zulässiger Inhalt | Formregeln: Fragen bevorzugen, Perspektiven als Hypothesen rahmen, kurze Antworten, kein Urteil |
| Verbotener Inhalt | Nutzer- oder sessionspezifische Stilanweisungen, Wärme-Imitations-Anweisungen, Tiefgangs-Aufforderungen |

---

## 8. Prompt-Bau nach Phase

| Phase | LLM-Call? | Prompt-Slots | Besonderheit |
|---|---|---|---|
| `ENTRY` | Nein | – | Predefined Kernel-Text; kein Prompt gebaut |
| `CHECK_IN` | Optional | system_rule_block, phase_context, [guard_constraint_block], response_shape_instruction | user_input_excerpt nur wenn Nutzerantwort vorliegt und reduzierbar; kann auch mit predefined Fragen arbeiten |
| `REFLECTION` | Ja | system_rule_block, phase_context, [guard_constraint_block], user_input_excerpt, response_shape_instruction | Vollständiger Guard-Zyklus vor und nach LLM; Constraint-Flags aus Session aktiv |
| `PAUSED` | Nein | – | NEUTRAL_PAUSE_RESPONSE (predefined); kein Prompt |
| `EXIT` | Nein | – | NEUTRAL_EXIT_CONFIRMATION (predefined); kein Prompt |
| `EXTERNAL_REFERRAL` | Nein | – | NEUTRAL_REFERRAL_RESPONSE (predefined); kein Prompt |
| `GUARD_BLOCK` | Nein | – | NEUTRAL_GUARD_BLOCK_RESPONSE (predefined); kein Prompt; kein Retry |
| Fehler / ERROR | Nein | – | NEUTRAL_ERROR_FAIL_CLOSED_RESPONSE (predefined); kein Prompt |

**Regel:** Neutrale Safe-State-Antworten werden niemals durch LLM „verbessert" oder variiert.

---

## 9. No-LLM-Fälle / Prompt-Verbot

Kein Prompt wird gebaut und kein LLM-Adapter-Call ausgelöst, wenn:

| # | Bedingung |
|---|---|
| 1 | Input Guard hat `BLOCK_EXIT`, `BLOCK_REFER`, `BLOCK_PAUSE`, `BLOCK_BOUNDARY` oder `ERROR_FAIL_CLOSED` zurückgegeben |
| 2 | Aktueller Zustand ist `EXIT`, `EXTERNAL_REFERRAL`, `GUARD_BLOCK`, `PAUSED` (ohne neues Nutzer-Go) |
| 3 | Aktuelle Phase ist `ENTRY` |
| 4 | `PHASE_TRANSITION_PENDING`-Flag aktiv und kein Opt-in bestätigt |
| 5 | `user_input_excerpt` ist nicht sicher reduzierbar |
| 6 | Pflichtslot fehlt oder ist nicht befüllbar |
| 7 | Phase ist unbekannt oder nicht definiert |
| 8 | Constraint-Flags sind widersprüchlich ohne auflösbare Priorität |
| 9 | Redaction schlägt fehl oder Ergebnis ist unsicher |
| 10 | Input enthält nach Redaction immer noch sicherheitskritische Signale |

---

## 10. Fail-Closed-Regeln für Prompt-Konstruktion

| Fehlerszenario | Systemverhalten |
|---|---|
| Pflichtslot fehlt | Kein Prompt; fail-closed → je nach Kontext `GUARD_BLOCK` oder `EXIT` |
| user_input_excerpt nicht safe reduzierbar | Kein Prompt; fall-closed → `EXIT` |
| Constraint-Flags widersprüchlich | Restriktivste Regel gewinnt; wenn keine auflösbar → kein Prompt → `EXIT` |
| Redaction-Unsicherheit | Im Zweifel kein Prompt; fail-closed → `EXIT` |
| Phase unknown oder fehlt | Kein Prompt; fail-closed → `EXIT` |
| system_rule_block nicht verfügbar | Kein Prompt; kein LLM-Call unter keinen Umständen |
| Prompt-Kontext zu groß / nicht begrenzbar | Kürzen; wenn nicht möglich → kein Prompt → `EXIT` |

**Generelle Fail-Closed-Priorität für Prompt-Konstruktion:**
```
Kein Prompt > Unsicherer Prompt
```
Lieber eine neutrale Systemantwort ausgeben als einen Guard-Bypass riskieren.

---

## 11. Operativer Implementierungs-Check

**Alle Fragen müssen mit Nein beantwortet werden.**
Bei Ja: Spezifikation unvollständig oder Implementierung verletzt Canon.

| # | Frage | Bei Ja |
|---|---|---|
| 1 | Kann Rohhistorie mehrerer Sessions ungeprüft in den Prompt gelangen? | Privacy-Verstoß |
| 2 | Kann ein Guard-/Safe-State-Fall trotzdem einen LLM-Call erzeugen? | Architekturverstoß |
| 3 | Kann ein Constraint-Flag als psychologische Aussage über den Nutzer im Prompt landen? | Claims-/Guard-Verletzung |
| 4 | Kann der Adapter selbst Prompt-Struktur erfinden oder ergänzen? | Architekturverstoß – Kernel konstruiert |
| 5 | Kann ein unklarer oder unvollständiger Kontext ohne fail-closed weiterlaufen? | Spezifikationslücke |
| 6 | Kann `user_input_excerpt` unkontrolliert auf beliebige Länge wachsen? | Privacy- und Guard-Risiko |
| 7 | Kann eine Safe-State-Antwort durch den LLM generiert oder variiert werden? | Architekturverstoß |
| 8 | Enthält der Prompt akkumulierte Nutzercharakterisierungen oder implizite Profile? | Privacy-Verstoß / Profiling-Risiko |
| 9 | Hängt Safety-Verhalten ausschließlich von Prompt-Instruktionen ab (keine Guards)? | Architekturverstoß – Guards sind nicht im Prompt |
| 10 | Kann `system_rule_block` fehlen und trotzdem ein LLM-Call erfolgen? | Spezifikationslücke – system_rule_block ist Pflicht |
