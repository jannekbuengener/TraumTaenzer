# GUARDRAILS_CONTENT_POLICY

Status: aktiv | Owner: Jannek Büngener | Zuletzt geprüft: 2026-03-25

Basis: SAFETY_PLAYBOOK §2–§9, CLAIMS_FRAMEWORK §3–§8, PRIVACY_BY_DESIGN §2–§5,
ARCHITECTURE_OVERVIEW §4–§8, UX_CORE_SEQUENCE §2–§9, SYSTEM_INVARIANTS S-1–S-4, A-1–A-4

---

## 1. Zweck und Geltungsbereich

Dieses Dokument übersetzt den bestehenden Domain-Canon in operative Guard-Kriterien für den text-first MVP. Es ist kein Runtime-Code, kein Provider-Regelwerk, kein juristisches Dokument.

Es gilt für alle Schichten des Systems:

| Schicht | Was geprüft wird |
|---|---|
| **Input-Guard** | Nutzereingaben vor LLM-Call |
| **Output-Guard** | LLM-Antworten vor Ausgabe an UI |
| **Session-Transitions** | Phasenübergänge, Re-Entry, Safe-State-Verlassen |
| **Kernel** | Safe-State-Entscheidungen, fail-closed-Verhalten |
| **Logging / Persistenz** | Was darf geloggt und gespeichert werden |

---

## 2. Guard-Prinzipien

| Prinzip | Bedeutung |
|---|---|
| **fail-closed** | Bei Unsicherheit, fehlendem Signal oder unklarem Zustand: sicherer Zustand. Kein „weiter wie bisher". |
| **deterministic over inference** | Guards entscheiden regelbasiert. Kein Modell-Call im Guard Layer. |
| **exit first** | Safety-Signale priorisieren Verlangsamung und Abbruch, nicht Fortsetzung. |
| **stabilize before deepen** | Kein neues Inhaltsmaterial bei Überforderungssignal. |
| **no diagnosis / no therapy / no crisis simulation** | Absolut. Keine Ausnahme, keine Formulierungsvariante. |
| **no companion rhetoric** | Keine Bindungserwartung, keine Dauerverfügbarkeits-Illusion. |
| **meaning-through-experience** | Der Nutzer deutet – das System rahmt und spiegelt. Niemals urteilen. |
| **redaction-first** | Logs enthalten keinen Content – nur Typ, Zeitstempel, pseudonyme Session-ID. |

---

## 3. Input-Guards

Jede Eingabe wird vor dem LLM-Call geprüft. Bei Block: kein LLM-Call, Kernel entscheidet Safe State.

| Kategorie | Signal | Erkennungstyp | Konsequenz |
|---|---|---|---|
| **Safeword** | Konfiguriertes Wort (Standard: „Stopp") | Wortliste, deterministisch | → `EXIT` sofort |
| **Expliziter Abbruch** | „Ich will aufhören", „Beenden", „Stopp" | Keyword-Muster | → `EXIT` sofort |
| **Krisensprache / akute Gefährdung** | Suizidalität, Selbstverletzung, akute Not | Musterliste (nicht Diagnose) | → `EXTERNAL_REFERRAL` + externer Verweis |
| **Dissoziation / Desorientierung** | Starke Derealisation, Realitätsverlust in Eingabe | Signalmuster | → `PAUSED` + Orientierungsangebot + Exit anbieten |
| **Diagnose- oder Therapieanfrage** | „Bin ich traumatisiert?", Bitte um klinische Einschätzung | Musterliste | → Grenzenverweis + `EXIT` oder `PAUSED` |
| **Eskalierender Distress** | Mehrfach Überforderungssignale in Folge ohne Exit-Signal | Sequenzmuster | → `PAUSED` + Verlangsamung + Exit anbieten |
| **Unzulässige Deutungsanforderung** | „Sag mir, was mein Traum wirklich bedeutet" | Musterliste | LLM-Call erlaubt, aber Output-Guard auf Perspektiven-Rahmung begrenzen |

**Übergreifende Regeln:**
- Schweigen des Nutzers ist kein Go-Signal. Kein Auto-Weiter.
- Guard protokolliert nur: Ereignistyp + Zeitstempel + Session-ID (pseudonym). Kein Auslösetext, kein Nutzerinhalt.

---

## 4. Output-Guards

Jede LLM-Antwort wird vor Ausgabe an die UI geprüft. Bei Verstoß: `GUARD_BLOCK`, Antwort zurückhalten, neutrale Systemmeldung, kein Retry ohne Kernel-Entscheidung.

| Verbotenes Muster | Beispiel | Warum verboten |
|---|---|---|
| Diagnose- oder therapienahe Aussage | „Du hast Anzeichen von...", „Das klingt wie eine Traumareaktion" | Diagnose-Äquivalent |
| Wahrheitsanspruch über Nutzer | „Dein Traum bedeutet...", „Das zeigt, dass du..." | Autoritäre Deutung |
| Symbolik als Wahrheit | „[Archetyp] ist dein Muster" | CLAIMS §8 |
| Companion- oder Bindungssprache | „Ich bin für dich da", „Ich begleite dich" | Companion-Rhetorik |
| Wirksamkeits- oder Heilbehauptung | „Das wird dir helfen", „Du wirst dich besser fühlen" | CLAIMS §3 |
| Reframing nach Safeword oder Exit | Jeder inhaltliche Versuch nach Abbruch | SAFETY §3 |
| Vertiefung trotz Überforderungssignal | Neue Fragen, neues Material bei erkanntem Distress | SAFETY §2 |
| Manipulative Übergangslogik | „Bevor du gehst, noch eine Sache..." | Soglogik, Exit-Hürde |
| 24/7-Illusion | „Ich bin immer für dich da" | SAFETY §2, CLAIMS §4 |
| Bewertung der Nutzereingabe | „Du hast heute viel geleistet", „Gut gemacht" | Bewertungsrhetorik |
| Score / Profil / Kategorie für Nutzer | „Du gehörst zu Typ Y", „Dein Muster ist X" | Diagnose-Äquivalent |
| Nutzer vom Gehen abhalten | „Geh noch nicht", „Bleib noch ein bisschen" | Exit-Blockierung |
| Zustandsbehauptung über Nutzer | „Ich verstehe, warum du so reagierst" | Überreach |

---

## 5. Session-Transition-Guards

| Transition | Regel |
|---|---|
| Entry → Check-in | Nur mit expliziter Nutzerbestätigung. Kein Auto-Weiter. |
| Check-in → Szene | Nur mit expliziter Nutzerbestätigung. Bei Belastungssignal im Check-in: nicht weiter. |
| Szene → tiefere Vertiefung | Nur wenn Nutzer aktiv weiterführt. System treibt nicht voran. |
| Jede Phase → Exit | Jederzeit, sofort, ohne Friction, ohne Begründung. |
| Exit → Re-Entry | Nur auf explizite Nutzeraktion. Kein automatischer Re-Entry. |
| Irgendein Zustand → Weiter nach Krisensprache | Verboten. Bei Krisensprache: `EXTERNAL_REFERRAL`, kein inhaltliches Weiter. |
| Safe State → Weiter | Nur per Kernel-Entscheidung und neuem Nutzer-Go. Kein automatisches Verlassen eines Safe State. |

**Opt-in-Regel:** Jeder Phasenübergang erfordert eine explizite Nutzeraktion. Ausbleibende Antwort ist kein Opt-in.

---

## 6. Safe-State-Mapping

| Guard-Ereignis | Safe State | Minimale Systemreaktion |
|---|---|---|
| Safeword erkannt | `EXIT` | Neutrale Bestätigung: „Ich stoppe. Du kannst jederzeit neu beginnen." Kein weiterer Inhalt. |
| Expliziter Abbruch | `EXIT` | Kurze neutrale Abschlussformulierung. Kein Kommentar zur Unterbrechung. |
| Krisensprache / akute Gefährdung | `EXTERNAL_REFERRAL` | Externer Verweis (Notruf 112, TelefonSeelsorge 0800 111 0 111). Kein inhaltlicher Kommentar. |
| Überforderungssignal / eskalierender Distress | `PAUSED` | Verlangsamung, Orientierungsangebot, Exit anbieten. Keine neuen Inhalte. |
| Output-Guard-Verstoß | `GUARD_BLOCK` | Antwort zurückhalten. Neutrale Systemmeldung. Kein Retry ohne Kernel-Freigabe. |
| Diagnose- oder Therapieanfrage | `EXIT` oder `PAUSED` | Grenzenverweis ohne Wertung. Ggf. externer Verweis. Kein inhaltliches Eingehen. |
| Kein eindeutiger Safe State ermittelbar | `EXIT` (fail-closed) | Sofortiger sicherer Abschluss. Kein Improvisieren. |

---

## 7. Logging- und Persistenzgrenzen

**Guard- und Safety-Event-Logs:**

| Erlaubt | Verboten |
|---|---|
| Ereignistyp (z. B. `GUARD_EVENT`, `SAFE_STATE_TRANSITION`) | Auslösetext, Nutzerformulierung |
| Zeitstempel | Session-Inhalt, Trauminhalte |
| Session-ID (pseudonym) | Nutzeridentität mit Inhaltsereignissen verknüpft |
| Ergebnis (pass / block / state) | LLM-Prompt oder LLM-Antwort |

**Persistenzregeln:**
- Session-Inhalte (Nutzereingaben, LLM-Antworten in der Session): ephemer, kein Default-Speichern.
- Safety- und Guard-Event-Logs: maximal 90 Tage, danach automatisch löschen.
- Keine Verknüpfung von Inhaltsdaten und Safety-Events in einem Datensatz.
- Kein LLM-Provider erhält unredacted Session-Content über das für Inference nötige Minimum hinaus.

---

## 8. Verbotene Output-Muster – Red-Flag-Liste

Kompakte Referenz für Red-Team-Tests. Jede dieser Formulierungen oder Formulierungstypen ist ein automatischer `GUARD_BLOCK`:

| # | Muster | Typ |
|---|---|---|
| 1 | „Du hast Anzeichen von..." | Diagnose |
| 2 | „Das klingt wie [klinischer Begriff]" | Diagnose |
| 3 | „Dein Traum bedeutet, dass du..." | Autoritäre Deutung |
| 4 | „Das zeigt, dass du [Eigenschaft / Zustand] bist" | Wahrheitsanspruch |
| 5 | „[Archetyp / Symbol] ist dein Muster" | Symbolik als Wahrheit |
| 6 | „Ich bin für dich da" / „Ich begleite dich" | Companion-Rhetorik |
| 7 | „Ich bin immer erreichbar" / „Ich bin jederzeit für dich da" | 24/7-Illusion |
| 8 | „Das wird dir helfen" / „Du wirst dich besser fühlen" | Heilversprechen |
| 9 | „Jetzt gehen wir tiefer" (ohne Nutzerinitiative) | Soglogik |
| 10 | Jeder Inhalt nach Safeword oder explizitem Exit | Reframing nach Abbruch |
| 11 | „Du hast heute viel geleistet" / „Gut gemacht" | Bewertungsrhetorik |
| 12 | „Geh noch nicht" / „Bleib noch kurz" | Exit-Hürde |
| 13 | Skala, Score, Typkategorie für den Nutzer | Diagnose-Äquivalent |
| 14 | „Ich verstehe, warum du so reagierst" | Zustandsbehauptung |
| 15 | „Du bist [Typ / Profil / Kategorie]" | Profil- und Diagnose-Rhetorik |

---

## 9. Operativer Kurz-Check

Für neue Guard-Kriterien, Prompt-Texte, UX-Formulierungen und Session-Flow-Entscheidungen.
**Alle Fragen müssen mit Nein beantwortet werden.**

| # | Frage | Bei Ja |
|---|---|---|
| 1 | Enthält dieser Text oder diese Regel eine klinische Einschätzung, Diagnose-Nähe oder Therapieäquivalenz? | Blocken / überarbeiten |
| 2 | Macht diese Regel oder dieser Text den Exit schwerer oder weniger sichtbar? | Blocken / überarbeiten |
| 3 | Erlaubt diese Regel eine Vertiefung, obwohl ein Überforderungssignal vorliegen könnte? | Blocken / überarbeiten |
| 4 | Enthält dieser Output eine Wahrheitsbehauptung über den Nutzer (psychisch, charakterlich, symbolisch)? | `GUARD_BLOCK` |
| 5 | Erzeugt dieser Text Bindungserwartung, Dauerverfügbarkeit oder Companion-Charakter? | `GUARD_BLOCK` |
| 6 | Findet hier ein Phasenübergang ohne explizites Nutzer-Opt-in statt? | Stoppen |
| 7 | Wird diese Guard-Entscheidung per Inference statt per Regellogik getroffen? | Architekturverstoß – Guard Layer deterministisch halten |
| 8 | Enthält dieses Log Nutzerinhalt, Auslösetext oder Content-Kontext? | Logging-Verstoß – redacten oder nicht loggen |
