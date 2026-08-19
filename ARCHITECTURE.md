# Bestätigter Arbeitsbrief: PW-Tool als LAN-Full-Stack-Anwendung

## Ziel und Umfang

PW-Tool wird von einer reinen lokalen Textual-CLI zu einem strukturierten Repository mit einem Python-Backend, einem praktischen React-Frontend und einer getrennten React-Projektwebsite. Die bisherige Textual-CLI entfällt als eigenständige Produktoberfläche. Die Passworterzeugung bleibt lokal zum betriebenen Server; die React-App kommuniziert per REST mit dem Python-Backend.

| Bereich | Festlegung |
|---|---|
| Backend | Python mit FastAPI, strukturierte REST-API, eigene Datenbank und Nutzerkonten. |
| Frontend | Vite, React und TypeScript mit fokussierter Generator-Ansicht im Technical-Field-Manual-Stil. |
| Website | Eigenes React-Projekt in `website/`; GitHub Actions bereitet GitHub Pages nach Aktivierung durch den Repository-Owner vor. |
| Repository | `backend/`, `frontend/`, `website/` sowie plattformübergreifende Starter im Hauptordner. |
| Paketmanager | `pnpm` für React-Projekte; Python-Abhängigkeiten getrennt im Backend. |
| Sprache | Deutsch für UI, Website und Dokumentation; technische API-Felder bleiben Englisch. |

## LAN-Betriebsmodell

Die Anwendung wird **nicht** als öffentlicher Internetdienst entwickelt. Sie darf lokal laufen und kann nach bewusster Konfiguration in einem vertrauenswürdigen LAN erreichbar sein. Für LAN-Betrieb sind Nutzerkonten und eine Datenbank vorgesehen.

| Sicherheitsgrenze | Verbindliche Umsetzung |
|---|---|
| Standardbindung | `127.0.0.1`; LAN-Bindung ist ein expliziter Startmodus. |
| LAN-Bindung | `0.0.0.0` nur mit konfigurierten erlaubten Origins und expliziter LAN-Konfiguration. |
| Konten | Lokale Registrierung/Anmeldung; Passwörter werden gesalzen und mit einer langsamen KDF gespeichert. |
| Sitzungen | Nicht vorhersehbare, serverseitig gespeicherte Sitzungstokens; Cookie- und Ablaufregeln werden dokumentiert. |
| Datenbank | Lokale SQLite-Datenbank im ersten Release; Datenmodell bleibt auf eine spätere PostgreSQL-Migration vorbereitbar. |
| Verlauf | Opt-in; Passwortwerte werden nur verschlüsselt gespeichert. Die Verschlüsselung verwendet einen separaten lokalen Schlüssel, nicht das Kontopasswort allein. |
| CORS | Kein Wildcard-CORS; localhost und explizit konfigurierte LAN-Origin(s) sind die einzigen erlaubten Ziele. |
| Rate Limits | Login- und erzeugungsbezogene Rate Limits sowie fehlertolerante, nicht sensitive Fehlermeldungen. |
| Öffentlicher Betrieb | Nicht Teil dieses Auftrags. TLS, Internet-Exposure, Mail-Reset und Multi-Tenant-Betrieb bleiben ausgeschlossen. |

> Die bestehende Hash-Demo bleibt eine lokale, selbstbezogene Schulungs- und Prüfungsfunktion. Sie akzeptiert keine fremden Hashes, Wortlisten oder Kandidaten und führt keine Rateversuche aus.

## Zielstruktur

```text
backend/                 FastAPI-Anwendung, Datenmodell, API, Tests und Python-Abhängigkeiten
frontend/                Vite/React/TypeScript-App für lokale und LAN-gebundene Nutzung
website/                 getrennte Vite/React-Projektwebsite für GitHub Pages
scripts/                 Hilfsskripte für Entwicklung, Migration und Qualitätsprüfung
start.sh                 Linux/macOS: Startet die gewünschte Komponente ohne Installation
start.bat                Windows: Startet die gewünschte Komponente ohne Installation
start-termux.sh          Android/Termux: Startet die kompatiblen lokalen Komponenten
setup.sh / setup.bat / setup-termux.sh
                          Bewusste Einrichtung der jeweiligen Laufzeitabhängigkeiten
```

## Funktionsumfang des ersten Full-Stack-Release

Die React-App umfasst Länge, Anzahl, Zeichenauswahl, Erzeugung, Kopieren, lokalen Sicherheitscheck, Ergebnislöschung, die sichere Hash-Demo, Registrierung, Anmeldung und eine opt-in-verschlüsselte Verlaufsliste. GPU/CUDA bleibt eine Status- und Benchmark-Metadatenfunktion; Passwort- und Hash-Erzeugung bleiben im auditierbaren CPU-/ARM64-Pfad.

## Abnahme und Ausschlüsse

Die Arbeit gilt als abgenommen, wenn die Starter funktionieren, Benutzerkonten und Datenbank lokal/LAN-konfiguriert arbeiten, CLI und React-App die vereinbarten sicheren Werte erzeugen, CORS und LAN-Grenzen geprüft sind, Tests und Builds erfolgreich durchlaufen und der Stand auf GitHub liegt.

Ausgeschlossen sind ein öffentlicher Internetdienst, eine allgemeine Crack-Funktion, die Verarbeitung fremder Hashes, unbeaufsichtigte Installationen in `start.*`, Cloud-Synchronisierung und eine mobile APK.
