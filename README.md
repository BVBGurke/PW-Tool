# PW-Tool

PW-Tool ist ein **lokales Python- und React-Monorepo** für nachvollziehbare Passworterzeugung. Es verbindet eine FastAPI-API, eine React-/TypeScript-Anwendung und eine getrennte React-Projektwebsite. Der sichtbare Passwortpfad arbeitet direkt mit OS-CSPRNG auf der CPU; Cloud-Synchronisierung, öffentliche Bereitstellung und Crackfunktionen sind ausdrücklich ausgeschlossen.

> **Betriebsgrenze:** Standardmäßig bindet PW-Tool nur an `127.0.0.1`. LAN-Nutzung ist nur hinter einem TLS-Reverse-Proxy, mit konkreten HTTPS-Origin(s), sicheren Cookies und lokaler Konten-/Datenbankkonfiguration zulässig. Der Starter bindet deshalb auch im LAN-Modus nicht direkt an das Netzwerkinterface.

| Bereich | Inhalt |
|---|---|
| `backend/app/` | FastAPI v1, API-Routen, Services, reine CSPRNG-Policy, Security-, Middleware- und Repository-Schichten. |
| `frontend/` | Vite, React und TypeScript; kontogeschützter Generator, Ergebnislöschung, opt-in Verlauf, Hash-Demo und Runtime-Status. |
| `website/` | Unabhängige React-Projektwebsite für GitHub Pages; sie ruft keine lokale API auf. |
| `scripts/` | Erzeugung der ignorierten lokalen Konfiguration und kontrollierte Laufzeitprüfung. |

## Sicherheits- und Produktgrenzen

Passwörter werden serverseitig über OS-CSPRNG erzeugt. Die Profile **Vollständig** und **Kompatibel** erzwingen Zeichenklassen, vermeiden Modulo-Bias durch Rejection Sampling und mischen Zeichenpositionen per CSPRNG-basiertem Fisher-Yates-Verfahren. Die sichtbare Maximalvoreinstellung nutzt 64 Zeichen mit vollständigem Zeichensatz.

Kontokennwörter werden mit gesalzener speicherharter `scrypt`-KDF gespeichert. Browser erhalten ausschließlich ein zufälliges, serverseitig widerrufbares Sessiontoken als HTTP-only-Cookie; Rohwerte werden nicht im Client gespeichert. Der verschlüsselte Verlauf ist opt-in und bindet AES-GCM-Ciphertexte zusätzlich an das jeweilige Konto. API-Antworten mit sensiblen Daten erhalten `no-store`-Header.

Die Hash-Demo akzeptiert nur Länge und Zeichensatz. Sie erzeugt einen frischen, nicht sichtbaren Demo-Wert, leitet einmalig `scrypt` ab und gibt ausschließlich Metadaten zurück. Sie verarbeitet keine Fremdhashes, Wortlisten oder Kandidatenlisten und bietet keine Rateversuche. CUDA ist keine Entropiequelle und kein Hash- oder Passwortpfad; der Runtime-Status weist dies explizit aus.

## Architektur und UI

Eine Anforderung fließt über **React-Feature → API-Client → FastAPI-Route → Service → Core/Security → Repository → SQLite**. Routen enthalten keine Krypto- oder SQL-Logik; Repositories kennen keine HTTP-Objekte. Domänenfehler werden zentral als redigierte `application/problem+json`-Antworten mit Request-ID übersetzt.

Das Frontend ist nach Features und API-Bereichen gegliedert. Es verwendet quellbasiert übernommene, auf `prefers-reduced-motion` begrenzte React-Bits-Komponenten für ruhige Inhaltsübergänge, Statusbereiche und die Runtime-Sicherheitskarte. Semantische Felder, Dialoge und Fehlermeldungen bleiben bewusst zugänglich und tastaturbedienbar.

## Lokale Einrichtung

Für Linux und macOS richtet `setup.sh` eine Python-Virtualenv, Backend-Abhängigkeiten, beide `pnpm`-Projekte sowie eine lokale, ignorierte Konfiguration ein. Startskripte installieren absichtlich nichts.

```bash
git clone https://github.com/BVBGurke/PW-Tool.git
cd PW-Tool
./setup.sh
./start.sh stack
```

Danach läuft die API standardmäßig unter `http://127.0.0.1:8000`; die React-App startet mit Vite auf Port `5173`. Die API verwendet den Präfix `/api/v1`; die lokale FastAPI-Dokumentation ist unter `http://127.0.0.1:8000/api/docs` erreichbar.

| Plattform | Einrichten | Starten |
|---|---|---|
| Linux/macOS | `./setup.sh` | `./start.sh [backend|frontend|stack]` |
| Windows | `setup.bat` | `start.bat [backend|frontend|stack]` |
| Android/Termux | `./setup-termux.sh` | `./start-termux.sh [backend|frontend]` |

`stack` startet das lokale Backend im Hintergrund und hält den Frontend-Dev-Server im Vordergrund. Termux bleibt absichtlich im CPU-/ARM64-Pfad. Für eine Produktvorschau sollten die erzeugten Passwörter anschließend in einem geeigneten Passwortmanager abgelegt werden.

### Termux-Hinweis

`setup-termux.sh` installiert `pnpm` bei Bedarf über das mit Node.js gelieferte `npm`; ein Paket namens `pnpm` wird in Termux nicht vorausgesetzt. Wenn Node.js bereits vorhanden ist, bleibt es erhalten. Führe daher einfach `bash setup-termux.sh` aus und starte erst danach Backend und Frontend über getrennte Termux-Tabs.

## TLS-geschützter LAN-Betrieb

LAN-Modus ist kein Direkt-Bindungsmodus. Ein Betreiber stellt zuerst einen TLS-Reverse-Proxy bereit, der Browserzugriffe über eine konkrete HTTPS-Origin akzeptiert und das Backend **lokal** auf `127.0.0.1:8000` erreicht. Frontend und API sollten unter derselben HTTPS-Origin liegen; in diesem Fall setzt ein Produktionsfrontend `VITE_API_BASE_URL=/api/v1`.

Die lokale, ignorierte Konfiguration muss mindestens die konkrete HTTPS-Origin und sichere Cookie-Parameter enthalten:

```json
{
  "allowed_origins": "https://pwtool.lan.example",
  "lan_enabled": true,
  "cookie_secure": true,
  "cookie_samesite": "strict"
}
```

Danach prüft `PWTOOL_BIND=lan ./start.sh backend` die Konfiguration und startet das Backend weiter nur lokal für den Reverse-Proxy. HTTP-Origin(s), Wildcard-CORS, unsichere Cookies und öffentlicher Internetbetrieb werden nicht als gültiger LAN-Modus akzeptiert.

## Entwicklung und Qualität

```bash
# Backend- und Sicherheitsregressionen
PYTHONPATH=backend python -m unittest discover -v backend/tests

# React-Anwendung mit React-Bits/GSAP bauen
pnpm --dir frontend install
pnpm --dir frontend build

# Projektwebsite für GitHub Pages bauen
pnpm --dir website install
GITHUB_ACTIONS=true pnpm --dir website build
```

GitHub Actions prüft Backend, Frontend und Website getrennt. Der Pages-Workflow baut ausschließlich `website/`; er enthält keine lokalen API- oder Konfigurationsgeheimnisse. Detaillierte Entscheidungen stehen in [`TARGET_ARCHITECTURE.md`](TARGET_ARCHITECTURE.md), die Migrationsparität in [`MODERNIZATION_BASELINE.md`](MODERNIZATION_BASELINE.md) und die React-Bits-Quellen in [`REACT_BITS_RESEARCH.md`](REACT_BITS_RESEARCH.md).
