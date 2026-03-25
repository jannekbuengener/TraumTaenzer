# Security Policy – Traumtänzer

## Scope

Dieses Repository enthält ausschließlich Governance-Dokumentation und CI-Konfiguration. Es gibt keinen Runtime-Code, keine API, keine Nutzerdaten, kein Deployment.

Sicherheitsrelevant in diesem Repo:

- CI/CD-Konfiguration (`.github/workflows/`)
- Secrets oder Credentials, die versehentlich committed wurden
- Schwachstellen in GitHub Actions oder verwendeten Actions-Versionen
- Abhängigkeiten (sobald vorhanden)

Nicht in Scope für dieses Repo (weil nicht vorhanden):

- Produkt-Runtime, API-Endpunkte, Authentifizierung
- Nutzerdaten, Datenbanken, Infrastruktur

---

## Meldung

Bitte melde Sicherheitsprobleme **nicht** als öffentliches Issue.

Nutze stattdessen GitHub's Private Vulnerability Reporting:
**[github.com/jannekbuengener/TraumTaenzer/security/advisories/new](https://github.com/jannekbuengener/TraumTaenzer/security/advisories/new)**

Alternativ: GitHub-Direktnachricht an [@jannekbuengener](https://github.com/jannekbuengener).

---

## Was beim Melden helfen

- kurze Beschreibung des Problems
- betroffene Datei oder Konfiguration
- reproduzierbarer Schritt oder Beispiel (wenn möglich)
- eingeschätztes Risiko (niedrig / mittel / hoch)

---

## Baseline

- Secret Scanning via Gitleaks (CI)
- Code Scanning via CodeQL (CI)
- Dependency Review bei PRs
- Keine Bug-Bounty – dies ist ein privates Einzelprojekt

---

## Antwortzeit

Da dies ein Solo-Projekt ist, gibt es keine SLA. Gemeldete Probleme werden so schnell wie möglich gesichtet.
