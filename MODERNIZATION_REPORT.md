# Modernisierungsbericht: PW-Tool

**Stand:** 19. August 2026

**Repository:** `BVBGurke/PW-Tool`
**Hauptmodernisierung:** `a2cea9c` – `Professional full-stack modernization`

## Ergebnis

PW-Tool wurde von der bisherigen flachen Python-Anwendungsstruktur zu einer klar geschichteten lokalen Full-Stack-Anwendung weiterentwickelt. Das Backend bleibt Python/FastAPI; die produktive Benutzungsoberfläche ist React mit TypeScript. Die getrennte React-Projektwebsite bleibt von der lokalen API isoliert.

Der sichere Passwortpfad bleibt unverändert konservativ: OS-CSPRNG auf CPU/ARM64, garantierte Zeichenklassen, Rejection Sampling und CSPRNG-Shuffle. CUDA ist sichtbar als nicht verwendeter Status, aber weder Entropie-, Passwort- noch Hash-Demo-Komponente. Die Hash-Demo akzeptiert keine Fremdhashes, Kandidatenlisten oder Rateversuche.

| Bereich | Gelieferter Stand |
|---|---|
| Backendstruktur | `app/api`, `core`, `middleware`, `models`, `repositories`, `schemas`, `security` und `services` mit eindeutigen Zuständigkeiten. |
| API | Versionierte `/api/v1`-Routen für Authentisierung, Generator, Verlauf, Hash-Demo, Capability und Health. |
| Konten und Sitzung | Gesalzene scrypt-KDF, serverseitig gespeicherte Sitzung, HTTP-only-Cookie, Token-Digest, Ablauf, Logout-Widerruf und Login-Rotation. |
| Verlauf | Opt-in, SQLite, AES-GCM, Kontokennung als zusätzliche Bindung sowie kontogebundene Abfrage und Löschung. |
| Browserhärtung | Konkrete CORS-Origin(s), Origin-Schutz für Zustandsänderungen, Request-ID, Rate Limit, Security Header und `no-store` für sensible API-Daten. |
| React-App | Getrennte API-Clients, Hooks und Features für Auth, Generator, Ergebnisse, Verlauf, Hash-Demo und Capability-Status. |
| React Bits | Quellbasierte `AnimatedContent`, `FadeContent` und `SpotlightCard`; GSAP nur bei nicht reduzierter Bewegung. |
| Responsive/A11y | Semantische Felder, Labels, Statusrollen, Tastaturfokus, Reduced Motion und geprüfte 375-Pixel-Ansicht. |
| Website/Dokumentation | Aktualisierte Projektwebsite, Architektur-, Migrations-, Konfigurations- und Betriebsdokumentation. |

## Qualitätsnachweis

Die abschließende Regression umfasste **11 Backend-Tests**. Sie decken Kontoerstellung, CSPRNG-Generierung, verschlüsselten Verlauf, kontoübergreifende Löschabwehr, Logout-Widerruf, Session-Rotation, Sicherheitsheader, Request-ID, Cross-Origin-Abwehr, Hash-Demo-Grenzen und TLS-LAN-Konfiguration ab. Frontend und Website bauen mit TypeScript und Vite ohne Fehler. Der Arbeitsbaum wurde vor dem Hauptcommit mit `git diff --check` geprüft; ein anschließender Scan fand keine getrackten Laufzeitkonfigurationen, privaten Schlüssel oder offensichtlichen Zugangstoken.

Die Browserprüfung bestätigte eine echte lokale Registrierung, cookie-gebundene Folgerouten, Runtime-Status und Passwortgenerierung gegen das FastAPI-Backend. Eine zunächst sichtbare SameSite-Grenze zwischen `localhost` und `127.0.0.1` wurde behoben: Im lokalen Entwicklungsmodus leitet der API-Client seinen Standardhost aus dem im Browser aufgerufenen Hostnamen ab. Für TLS-/Reverse-Proxy-Betrieb bleibt `VITE_API_BASE_URL=/api/v1` als explizite, nicht geheime Konfiguration vorgesehen.

## Verbindliche Betriebsgrenzen

| Bereich | Grenze |
|---|---|
| Standardbetrieb | Backend und Dev-Frontend binden an `127.0.0.1`; keine automatische Netzwerkfreigabe. |
| LAN | Nur hinter TLS-Reverse-Proxy, konkreten HTTPS-Origin(s), `cookie_secure=true`, `cookie_samesite=strict` und `lan_enabled=true`. |
| Internet | Nicht unterstützt; kein Multi-Tenant-Hosting, E-Mail-Reset oder öffentliche Passwort-API. |
| Geheimnisse | Lokale `.pwtool.local.json`, Datenbank und Buildartefakte sind ignoriert; keine Secrets im Frontend oder Repository. |
| Verlauf | Bewusstes Opt-in; Verschlüsselung ersetzt kein professionelles Passwortmanagement. |

## Verbleibende Risiken und sinnvolle nächste Schritte

Der TLS-Reverse-Proxy ist bewusst eine Betreiberaufgabe. Vor jedem tatsächlichen LAN-Einsatz müssen Zertifikatsverwaltung, Proxy-Header, Firewall und konkrete DNS-/HTTPS-Origin geprüft werden. Eine lokale SQLite-Datei benötigt Betriebssystemzugriffsschutz und regelmäßige, verschlüsselte Backups, falls der freiwillige Verlauf verwendet wird.

Die React-App besitzt einen Build- und Browser-Smoke-Test, aber noch keine eigene Komponenten-/End-to-End-Test-Suite. Eine spätere Erweiterung kann Playwright-Tests für Registrierung, CORS-Fehler, Sitzungsauslauf, Ergebnislöschung und Reduced Motion ergänzen. Diese Erweiterung ist kein Blocker für den jetzt geprüften lokalen Einsatz, erhöht jedoch die Release-Absicherung.

## Verweise

Die ausführliche Zielarchitektur steht in [`TARGET_ARCHITECTURE.md`](TARGET_ARCHITECTURE.md), die Bestandsaufnahme in [`MODERNIZATION_BASELINE.md`](MODERNIZATION_BASELINE.md), die React-Bits-Entscheidungen in [`REACT_BITS_RESEARCH.md`](REACT_BITS_RESEARCH.md) und die Browserdetails in [`VALIDATION_NOTES.md`](VALIDATION_NOTES.md).
