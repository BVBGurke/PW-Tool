# PW-Tool

PW-Tool ist jetzt ein **Python- und React-Monorepo** für lokale Passworterzeugung und einen bewusst konfigurierten Betrieb in einem vertrauenswürdigen LAN. Das Repository trennt die FastAPI-Anwendung, die praktische React-Generator-App und die öffentliche Projektwebsite klar voneinander.

> **Sicherheitsmodell:** Standardmäßig lauscht das Backend nur auf `127.0.0.1`. Ein LAN-Betrieb ist möglich, aber ausschließlich nach expliziter Konfiguration von Konten, Datenbank und erlaubten Origins. Ein öffentlicher Internetdienst ist nicht Teil dieses Projekts.

| Ordner | Zweck |
|---|---|
| `backend/` | FastAPI, OS-CSPRNG-Passwortpolicy, Konten, serverseitige Sitzungen, SQLite und verschlüsselter Opt-in-Verlauf. |
| `frontend/` | Vite/React/TypeScript-App für Passworterzeugung, Kopieren, Sicherheitscheck, Verlauf und Hash-Demo. |
| `website/` | Unabhängige Vite/React-Projektwebsite für GitHub Pages. |
| `scripts/` | Konfigurations- und Qualitätshelfer. |

## Lokale Einrichtung

Für Linux und macOS richtet `setup.sh` eine Python-Virtualenv, die Backend-Abhängigkeiten, beide pnpm-Projekte sowie eine lokale Geheimniskonfiguration ein. Die Startskripte führen absichtlich keine Installation durch.

```bash
git clone https://github.com/BVBGurke/PW-Tool.git
cd PW-Tool
./setup.sh
./start.sh
```

Danach läuft die API standardmäßig unter `http://127.0.0.1:8000` und die React-App unter `http://127.0.0.1:5173`. Die FastAPI-Dokumentation ist lokal unter `http://127.0.0.1:8000/api/docs` erreichbar.

| Plattform | Einrichten | Starten |
|---|---|---|
| Linux/macOS | `./setup.sh` | `./start.sh [backend|frontend|stack]` |
| Windows | `setup.bat` | `start.bat [backend|frontend|stack]` |
| Android/Termux | `./setup-termux.sh` | `./start-termux.sh [backend|frontend]` |

`stack` startet das Backend im Hintergrund und hält das Frontend im Vordergrund. Android/Termux verwendet absichtlich den CPU-/ARM64-Pfad; CUDA ist nie Teil der Passwort- oder Hash-Erzeugung.

## Konten, Datenbank und Verlauf

Die erste Person kann über die React-App ein lokales Konto anlegen. Kontokennwörter werden mit einer gesalzenen `scrypt`-KDF gespeichert. Die Anmeldung erstellt ein zufälliges, serverseitig gespeichertes Sitzungstoken, das der Browser nur über ein HTTP-only-Cookie erhält.

Der Verlauf ist bewusst deaktiviert, bis die Checkbox beim Erzeugen aktiviert wird. Bei Aktivierung werden Passwortwerte mit einem separaten lokalen AEAD-Schlüssel verschlüsselt in SQLite abgelegt und erst nach erneuter authentisierter Abfrage entschlüsselt. Die lokale Konfiguration `.pwtool.local.json` enthält diese Schlüssel und wird nicht eingecheckt.

> Lösche einen Verlaufseintrag, sobald er nicht mehr benötigt wird. Ein verschlüsselter lokaler Verlauf ist kein Ersatz für ein professionell betriebenes Passwortmanagement.

## LAN-Betrieb

Ein LAN-Server benötigt eine bewusste Änderung der lokal erzeugten Konfiguration. Trage die konkrete React-Origin ein und setze `lan_enabled` auf `true`; Wildcard-CORS ist absichtlich ungültig.

```json
{
  "allowed_origins": "http://192.168.1.50:5173",
  "lan_enabled": true
}
```

Danach startet `PWTOOL_BIND=lan ./start.sh backend` den Server auf `0.0.0.0`. Verwende diesen Modus nur in einem vertrauenswürdigen Netz. Für sensible LAN-Umgebungen muss der Betreiber zusätzlich einen TLS-terminierenden Reverse Proxy bereitstellen; ein öffentlicher Internetbetrieb, E-Mail-Reset und Multi-Tenant-Hosting sind ausgeschlossen.

## Passwort- und Hash-Grenzen

Die sichtbare Policy zieht direkt aus dem OS-CSPRNG, erzwingt Zeichenklassen, verwendet Rejection Sampling gegen Modulo-Bias und mischt Positionen per CSPRNG-basiertem Fisher-Yates-Shuffle. Die Auswahl **Vollständig** garantiert Klein-/Großbuchstaben, Ziffern und Sonderzeichen; **Kompatibel** garantiert Klein-/Großbuchstaben und Ziffern.

Die lokale Hash-Demo erzeugt ausschließlich einen frischen, nicht angezeigten Demo-Wert. Sie führt eine begrenzte scrypt-Ableitung und eine einmalige Selbstverifikation aus und zeigt nur Metadaten. Das Projekt enthält keine allgemeine Crack-Funktion, verarbeitet keine Fremdhashes und verwendet keine Kandidatenlisten oder Rateversuche.

## Entwicklung und Qualität

```bash
# Backendtests
PYTHONPATH=backend python -m unittest discover -v backend/tests

# React-Generator bauen
pnpm --dir frontend install
pnpm --dir frontend build

# Projektwebsite für GitHub Pages bauen
pnpm --dir website install
GITHUB_ACTIONS=true pnpm --dir website build
```

GitHub Actions prüft Backend, Frontend und Website. Der Pages-Workflow baut `website/` und kann erst nach Aktivierung von GitHub Pages in den Repository-Einstellungen tatsächlich veröffentlichen.

## Zusätzliche Architekturinformationen

Der bestätigte Sicherheits- und Produktbrief steht in [`ARCHITECTURE.md`](ARCHITECTURE.md). Die genaue Ordner- und Migrationsstrategie steht in [`MIGRATION.md`](MIGRATION.md). Beide Dokumente grenzen den lokalen/LAN-Betrieb ausdrücklich gegen ein öffentliches Passwortservice-Angebot ab.
