# Modernisierungsbaseline und Feature-Matrix

## Prüfgegenstand

Die Baseline wurde am Arbeitsstand `9f3c359` (`Activate CI and Pages workflows`) erfasst. Als Vergleichsbasis für die frühere, sichere CLI-/Textual-Version dient die Revision `8d2cdde` (`Simplify secure TUI and add Pages site`). Zu diesem Zeitpunkt enthält der aktuelle Arbeitsbaum nur die beabsichtigte Ergänzung von `todo.md`; funktionaler Code wurde vor dem Testlauf nicht verändert.

| Prüfschritt | Ergebnis |
|---|---|
| Backend-Regressionen | 7 von 7 `unittest`-Tests bestanden. |
| Frontend | TypeScript- und Vite-Produktionsbuild bestanden; 17 Module, rund 404 kB JavaScript vor Gzip. |
| Website | TypeScript- und Vite-Produktionsbuild bestanden; 16 Module, rund 401 kB JavaScript vor Gzip. |
| Backend-Struktur | Funktional, aber noch flach: Routen, Pydantic-Modelle, Rate Limit, Authentisierung und Orchestrierung liegen in `backend/pwtool/app.py`. |
| Frontend-Struktur | Funktional, aber monolithisch: Authentisierung, Generator, Verlauf und Hash-Demo liegen überwiegend in `frontend/src/App.tsx`. |

## Historische Funktionszuordnung

| Historische Funktion aus `8d2cdde` | Aktuelles Gegenstück | Status | Nächster Umgang |
|---|---|---|---|
| Direkte OS-CSPRNG-Passworterzeugung | `backend/pwtool/core/passwords.py` | Erhalten | Als reine Core-Policy und durch zusätzliche Tests absichern. |
| Normal-/Vollzeichensatz und garantierte Zeichenklassen | `validate_request`, `generate_one`, Generator-Formular | Erhalten | API-Schema und UI-Typen zentralisieren. |
| Mindestlänge 16, Batch-Grenze und valide Werte | `GenerationInput` und `validate_request` | Erhalten | Doppelte Grenzen in Schema und Core gezielt testen. |
| Maximales Sicherheitsprofil | Default: 64 Zeichen, vollständiger Zeichensatz | Teilweise erhalten | Als sichtbare, erklärte Preset-Auswahl ergänzen; nicht nur als impliziter Default. |
| Konservative Entropie-/Sicherheitsbewertung | `security_summary`, Ergebnisstreifen | Teilweise erhalten | Methodik, Grenzen und keine Scheingenauigkeit dokumentieren; Status-UI verbessern. |
| Einmalige sichtbare Ergebnisbehandlung und Löschung | Ausgabe nur im Komponentenstatus; Logout leert Werte | Teilweise erhalten | Explizite Schaltfläche zum Verwerfen und sensible Clipboard-/UI-Hinweise ergänzen. |
| Kopieren des erzeugten Batches | `navigator.clipboard` | Erhalten | Fehler- und Erfolgsmeldungen komponentisiert behandeln. |
| Verschlüsselter opt-in Verlauf | AES-GCM-geschützte Werte in SQLite, kontogebundene Abfrage/Löschung | Erhalten | Repository-/Service-Layer, IDOR-Tests, Löschung, Log-Redaktion und Schlüsselrotation dokumentieren. |
| Selbstbezogene lokale scrypt-Hash-Demo | `/api/security/hash-demo` | Erhalten | In `HashDemoService` extrahieren und explizit gegen Fremdhash-/Kandidatenparameter testen. |
| Keine allgemeine Crack-Funktion, keine Fremdhashes | API nimmt nur Länge/Zeichensatz an | Erhalten | Als Architekturgrenze und Testfall erhalten. |
| CPU-/ARM64-freundlicher Hauptpfad | `secrets`-/OS-CSPRNG-Pfad im Backend | Erhalten | Termux-/ARM64-Start und Laufzeit im CI-/Dokumentscope ausdrücklich prüfen. |
| CUDA nur Diagnostik/Benchmark, nie sichtbarer Passwortpfad | Kein gleichwertiger API-/UI-Status im aktuellen Stand | Fehlend | Harmlosen, nicht beschleunigenden Capability-/Benchmark-Metadatenservice nur nach Bedarf ergänzen; keine GPU-Entropie oder Cracklogik. |
| Plattformstarter für lokale Nutzung | `setup.*`, `start.*`, `scripts/` | Vorhanden, ungeprüft | Syntax, Konfiguration, Bindungsschutz und Dokumentation über alle unterstützten Plattformen testen. |
| Textual-TUI | Ersetzt durch React-Webapp | Bewusst ersetzt | In Migrationsdokumentation als nicht mehr ausgelieferter Client ausweisen, nicht stillschweigend als entfernt behandeln. |
| Getrennte Projektwebsite | `website/` und Pages-Workflow | Erhalten | Inhalts- und Build-Behauptungen an den tatsächlichen LAN-/Sicherheitsgrenzen ausrichten. |

## Festgestellte technische Schuld

Die folgenden Punkte sind nicht als Produktionstauglichkeit zu werten; sie bilden den verbindlichen Umfang der folgenden Migrationsphasen.

| Priorität | Befund | Auswirkung | Geplante Gegenmaßnahme |
|---|---|---|---|
| Kritisch | Sitzungs-Cookie wird derzeit pauschal mit `secure=False` gesetzt. | Eine versehentliche LAN-HTTP-Nutzung kann Authentisierungsdaten schwächen. | TLS-/Bindungsmodell definieren; `Secure` für TLS erzwingen und LAN ohne sichere Konfiguration nicht als gleichwertig behandeln. |
| Hoch | `app.py` bündelt Routen, Schemata, Authentisierung, Rate-Limit, Krypto-Orchestrierung und Datenzugriff. | Sicherheits- und Regressionstests bleiben unnötig schwer isolierbar. | API-, Service-, Schema-, Middleware- und Repository-Layer einführen. |
| Hoch | Der Frontend-Flow ist ein einzelnes, großes Komponentenmodul. | Keine verlässliche Zustandskapselung, erschwerte Accessibility- und Fehlertests. | Feature-Struktur, zentralen Client, Typen, Hooks und wiederverwendbare Statuskomponenten einführen. |
| Mittel | React Bits ist noch nicht produktiv integriert. | Die verpflichtende visuelle Komponentenanforderung ist nicht erfüllt. | Komponenten nur aus der dokumentierten Matrix übernehmen und Reduced Motion respektieren. |
| Mittel | Security Header, zentrale Fehlerbehandlung, Request-ID und erweiterte API-Grenzen fehlen. | Geringere Transparenz und uneinheitliche Sicherheitsantworten. | Middleware- und Ausnahme-Architektur implementieren. |
| Mittel | Ergebnis kann nicht aktiv sofort verworfen werden. | Sensible Werte können länger als notwendig sichtbar bleiben. | Löschaktion mit Fokus- und Zwischenablagehinweisen bereitstellen. |
| Niedrig | Testumfang deckt Kern-API ab, aber nicht die modularen Services, UI-Zustände, Keyboard- und mobile Flows. | Modernisierungsregressionen sind nur teilweise abgesichert. | Unit-, API-, Sicherheits- und React-Tests ausbauen. |

## Sicherheitsgrenzen, die unverändert bleiben

PW-Tool bleibt ein lokales beziehungsweise bewusst konfiguriertes LAN-System und wird nicht als öffentlicher Passwortdienst entwickelt. Die Anwendung verarbeitet keine hochgeladenen Fremdhashes, Wortlisten, Kandidatenlisten oder Angriffsschritte. CUDA/GPU darf keinerlei Quelle für Passwortzufall sein und ist nur als optionale, klar begrenzte Geräte- oder Benchmark-Metadaten zulässig. Lokale Daten sind keine Cloud-Synchronisierung und dürfen niemals unverschlüsselt als Demo-, Log- oder Website-Inhalt erscheinen.
