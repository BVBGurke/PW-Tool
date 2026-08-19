# PW-Tool-Architektur

## Zweck und Grenze

PW-Tool ist eine lokale beziehungsweise TLS-abgesicherte LAN-Anwendung für Passworterzeugung über den OS-CSPRNG-CPU-Pfad. Das System ist kein öffentlicher Passwortdienst, keine Cloud-Synchronisierung, keine native APK und kein Crackwerkzeug. Die unabhängige `website/` beschreibt das Projekt, ruft jedoch keine lokale API auf.

## Implementierter Zielbaum

```text
backend/
  app/
    api/            versionierte FastAPI-Routen und Abhängigkeiten
    core/           Settings, Fehlerübersetzung, Passwortpolicy
    middleware/     Request-ID, Security Header, Origin- und Rate-Limit-Grenzen
    models/         interne Datenmodelle
    repositories/   parameterisierte SQLite-Zugriffe
    schemas/        Pydantic Request-/Response-Verträge
    security/       scrypt, Sessions, AES-GCM
    services/       Auth, Generator, Verlauf, Hash-Demo, Capability-Status
    main.py         App-Fabrik
  tests/
frontend/
  src/api/          zentraler Cookie-API-Client pro Fachbereich
  src/features/     Auth, Generator, Verlauf, Hash-Demo und Runtime-Status
  src/components/react-bits/
website/
scripts/
```

Eine Nutzungsanforderung folgt der Grenze **React-Feature → Client → Route → Service → Core/Security → Repository → SQLite**. Routen übersetzen ausschließlich HTTP und Abhängigkeiten. Services tragen die Fachlogik. Repositories führen den lokalen Datenzugriff mit Platzhalterparametern aus.

## API und Sicherheitsmodell

Die öffentliche lokale API ist unter `/api/v1` versioniert. Authentisierung, Passworterzeugung, Verlauf, Hash-Demo und Runtime-Capabilities sind getrennte Routen. Fehler werden als `application/problem+json` mit zufälliger Request-ID zurückgegeben; Interne Fehlermeldungen, SQL-Ausnahmen, Schlüssel, Passwortwerte und Sessiontokens gehören nicht in Antworten oder Logs.

| Schutzbereich | Umsetzung |
|---|---|
| Konto | scrypt mit Salt und konstanter Vergleich; Dummy-Ableitung bei unbekanntem Benutzernamen. |
| Sitzung | Zufälliges opaque Token im HTTP-only-Cookie; nur HMAC-Digest wird serverseitig gespeichert; Ablauf und Logout-Widerruf. |
| Verlauf | Opt-in; AES-GCM mit Kontokennung als authentifizierter Zusatzdatenbindung; nur kontogebundene Auswahl/Löschung. |
| Browsergrenze | Kein Wildcard-CORS; zustandsändernde Requests prüfen Origin zusätzlich; API-Daten sind `no-store`. |
| HTTP-Härtung | Request-ID, `nosniff`, Frame- und Referrer-Schutz, Permissions Policy. |
| Passwortkern | OS-CSPRNG und CPU/ARM64; CUDA ist keine Entropie-, KDF- oder Passwortkomponente. |

## Laufzeitmodell

Der lokale Entwicklungsmodus nutzt ausdrücklich konfigurierte `localhost`-/`127.0.0.1`-Origins und ein nicht sicheres Cookie nur in dieser isolierten HTTP-Entwicklungsform. Der Frontend-Client leitet den lokalen API-Host aus dem aufgerufenen Browserhost ab, damit SameSite-Cookies nicht zwischen `localhost` und `127.0.0.1` verloren gehen.

LAN-Konfiguration muss konkrete HTTPS-Origin(s), `lan_enabled=true`, `cookie_secure=true` und einen TLS-Reverse-Proxy enthalten. Der LAN-Starter bindet FastAPI weiter an `127.0.0.1`; der Proxy terminiert TLS und liefert idealerweise die App sowie `/api/v1` unter derselben Origin aus. HTTP-LAN, Wildcards und öffentliche Internetfreigabe sind nicht zulässig.

## Frontend und React Bits

Die App nutzt React und TypeScript mit zentralem API-Client und klaren Loading-, Error-, Empty- und Success-Zuständen. Aus React Bits wurden quellbasiert angepasste `AnimatedContent`, `FadeContent` und `SpotlightCard` eingebunden. GSAP-Bewegungen laufen nur bei nicht reduzierter Bewegung, bleiben kurz und enthalten weder Scrollzwang noch Animationen für Fehlermeldungen. Formularfelder und Statusmeldungen bleiben semantisch und tastaturbedienbar.
