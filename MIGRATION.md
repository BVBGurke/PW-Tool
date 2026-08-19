# Migrationsarchitektur

## Zielbaum

```text
backend/
  pyproject.toml                 Python-Abhängigkeiten und FastAPI-Entrypoint
  pwtool/
    api/                         Routen für Authentisierung, Passworterzeugung und Verlauf
    core/                        CSPRNG-Policy, Sicherheitscheck und lokale Hash-Demo
    db/                          SQLite-Verbindung, Schema und Migrationslogik
    security/                    Kontokennwort-KDF, Sessions und Verlaufverschlüsselung
    app.py                       FastAPI-Anwendung mit enger CORS-/LAN-Konfiguration
  tests/                         Backend- und API-Tests
frontend/                        Vite/React/TypeScript-Anwendung für den Generator
website/                         Vite/React/TypeScript-Projektwebsite für GitHub Pages
scripts/                         Prüf- und Entwicklungshelfer
start.sh / start.bat             Plattformstarter für Backend, Frontend und Stack
start-termux.sh                  Android/Termux-Starter mit CPU-Kompatibilität
setup.sh / setup.bat / setup-termux.sh
                                 Bewusste Installation, Initialisierung und Secret-Erzeugung
```

## API- und Sicherheitsmodell

| Komponente | Verantwortlichkeit | Begrenzung |
|---|---|---|
| Authentisierung | Registrierung, Anmeldung, Abmeldung und Server-Sitzungen | Kennwörter mit gesalzener `hashlib.scrypt`-KDF; keine Klartextspeicherung. |
| Sitzung | Opaques zufälliges Token im sicheren HTTP-only-Cookie | Token wird nur gehasht in SQLite abgelegt, hat Ablaufzeit und kann widerrufen werden. |
| Passworterzeugung | Direkte OS-CSPRNG-Policy | Immer CPU/ARM64, keine CUDA- oder Fremdhash-Pfade. |
| Verlauf | Opt-in-Speicherung verschlüsselter Passwortwerte | Pro Anwendung eigener lokaler AEAD-Schlüssel; Anzeige nur nach authentisierter Abfrage. |
| CORS/LAN | Standard localhost, LAN nur per expliziter Konfiguration | Keine Wildcards; ein fehlendes LAN-Origin blockiert LAN-Start. |
| GPU | Status und harmlose Benchmarks | Nicht Teil der Passwort-/KDF-Ausführung. |

## Konfigurationsvertrag

`setup.*` erzeugt eine nicht eingecheckte lokale Konfigurationsdatei mit Datenbankpfad, Session- und Verlaufsverschlüsselungsschlüssel. `start.*` installiert keine Abhängigkeiten und startet standardmäßig nur an `127.0.0.1`. Für LAN muss der Betreiber explizit `PWTOOL_BIND=lan` und mindestens eine erlaubte Origin setzen.

## Migrationsregel

Die bisherigen Python-Module werden in das importierbare Paket `backend/pwtool/` überführt. Im Hauptordner bleiben ausschließlich klar gekennzeichnete Starter, Dokumentation, CI-Konfiguration und gegebenenfalls schlanke Kompatibilitätshinweise. `frontend/` und `website/` bekommen jeweils einen eigenen `pnpm-lock.yaml`, damit App- und Marketingabhängigkeiten nicht vermischt werden.
