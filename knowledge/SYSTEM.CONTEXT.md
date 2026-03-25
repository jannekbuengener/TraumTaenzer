# SYSTEM.CONTEXT – Traumtänzer

Status: aktiv | Owner: Jannek Büngener | Zuletzt geprüft: 2026-03-25

Realität: Umgebung, Repo-Struktur, Tools, Constraints. Keine Fantasieinfrastruktur.

---

## Repo

- **GitHub:** `github.com/jannekbuengener/TraumTaenzer`
- **Hauptbranch:** `main` (geschützt, PR-only)
- **Aktiver Arbeits-Branch:** `docs/modus-mono-pdf`
- **Sprache:** primär Deutsch; technische Bezeichner bleiben englisch
- **Charakter:** documentation- und governance-first; kein Runtime-Code

---

## Entwicklungsumgebung

- **OS (Entwicklung):** Windows 11 Pro
- **Shell im Claude Code:** bash (Unix-Syntax, nicht Windows-CMD)
- **Primäres KI-Werkzeug:** Claude Code (claude.ai/code) mit Claude Sonnet 4.6

---

## CI / Qualitäts-Gates

Alle via GitHub Actions, ausgelöst bei PR auf `main`:

| Check | Werkzeug | Status |
|---|---|---|
| Secret Scanning | Gitleaks | aktiv |
| Code Scanning | CodeQL | aktiv |
| Dependency Review | GitHub Dependency Review | aktiv |
| CI (allgemein) | `.github/workflows/ci.yml` | Platzhalter – noch kein Produktcode |

CI-Checks sind Merge-Gate, keine Dekoration.

---

## Toolchain

- **Versionskontrolle:** Git / GitHub
- **PR / Issue-Verwaltung:** GitHub CLI (`gh`)
- **Kein Build-System:** kein `package.json`, kein `Makefile`, kein `pyproject.toml`
- **Kein Testframework:** kein Anwendungscode, keine Testsuites
- **Kein Runtime:** kein Server, keine API, kein Deployment

---

## KI-Agenten-Rollen

| Agent | Werkzeug | Rolle |
|---|---|---|
| Claude | Claude Code | Session-Lead: Entscheidungen moderieren, Diffs vorbereiten, Canon prüfen |
| Codex | OpenAI Codex (ggf.) | Execution: deterministische Umsetzung |
| Gemini | Google Gemini (ggf.) | Audit: Compliance, Konsistenzprüfung |

Alle Agenten sind Zuarbeiter. Entscheidungen trifft der Owner.

---

## Secrets und Credentials

- Keine Secrets in diesem Repo.
- Gitleaks scannt bei jedem PR.
- `.env`-Dateien, API-Keys und Credentials dürfen nicht committed werden.

---

## Constraints

- Kein Produktionsbetrieb – keine Nutzerdaten, keine Infrastruktur.
- Kein öffentliches Deployment.
- Provider-DPAs für Produktionsphase noch offen (dokumentiert in `PRIVACY_BY_DESIGN.md §9`).
- SYSTEM_INVARIANTS gelten als Rahmenbedingungen für jede technische Entscheidung.
