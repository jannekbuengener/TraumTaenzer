# Branch Protection – Traumtänzer

Stand: 2026-03-25 | Gilt für: `main`

---

## Pflicht-Einstellungen

- **Require a pull request before merging** – keine Direktmerges auf `main`
- **Require status checks to pass before merging** – nur wenn der Check unten als Required markiert ist
- **Do not allow bypassing the above settings** – auch für Admins / Owner

---

## Required Status Checks

| Check | Workflow | Was er prüft | Required |
|---|---|---|---|
| `CI` | `ci.yml` | Pflicht-Governance-Dateien existieren und sind nicht leer | **Ja** |
| `Gitleaks` | `gitleaks.yml` | Keine Secrets in Commits | **Ja** |
| `Dependency Review` | `dependency-review.yml` | Keine neuen kritischen Abhängigkeiten in PRs | **Ja** |

---

## Aktive Checks (nicht Required)

| Check | Workflow | Was er prüft | Hinweis |
|---|---|---|---|
| `Trivy` | `trivy.yml` | Filesystem-Scan auf CRITICAL/HIGH CVEs | Läuft, kein Required Gate – kein Paketmanifest vorhanden |
| `CodeQL` | `codeql.yml` | Statische Code-Analyse | Deaktiviert – kein Produktcode; nur `workflow_dispatch` |

---

## Nicht aktiviert (noch kein Bedarf)

- Require approvals: kein Team, Solo-Maintainer-Betrieb
- Require signed commits: optional, nicht erzwungen
- Require linear history: optional

---

## Begründung der Required-Check-Auswahl

**CI (Strukturprüfung):**
Einziger Workflow mit echter Fehlbarkeit für ein docs-only Repo. Prüft, ob Pflicht-Governance-Dateien vorhanden und nicht leer sind. Kann real fehlschlagen.

**Gitleaks:**
Secret Scanning ist für jeden Repo-Typ sinnvoll. Schützt vor versehentlich committierten API-Keys, Tokens oder Credentials. Liefert echten Wert.

**Dependency Review:**
Trivially pass für reine Dokumentation (keine Manifests). Wird automatisch aktiv, sobald Packages hinzukommen. Kein Greenwashing, kein Mehraufwand.

**CodeQL (deaktiviert):**
Python/JavaScript existieren im Repo nicht. Aktivierung mit falschen Sprachen erzeugt entweder Greenwashing (trivial pass) oder unnötige Fehler. Wird reaktiviert, wenn Produktcode vorhanden ist.

**Trivy (nicht Required):**
Filesystem-Scan läuft, findet aber keine Schwachstellen ohne Paketmanifeste. Als passiver Scan behalten, nicht als Merge-Gate.
