# Technische Roadmap: Private Beta

Diese Roadmap enthält nur bestätigte Befunde. P0 existiert im aktuellen Audit nicht; die Reihenfolge beginnt daher mit P1. Jede Änderung bleibt lokal, klein und rückrollbar.

| Reihenfolge | ID | Problem | Technische Lösung | Betroffene Dateien/Module | Abhängigkeiten & Migration | Risiko | Erwarteter Nutzen | Test-/Rollback-Strategie | Status |
|---:|---|---|---|---|---|---|---|---|---|
| 1 | P-001 | Unbegrenzte Batchgröße | `MAX_BATCH_COUNT` zentral definieren und in TUI sowie `GenerationRequest` validieren | `backends/base.py`, `tui.py`, Tests, README | Keine Datenmigration; bestehende kleine Batches bleiben kompatibel | Niedrig | Verhindert versehentliche lokale CPU-/RAM-Überlastung | Grenzwerttests, vollständige Regression; Rückrollbar durch Entfernen der Obergrenze | geplant |
| 2 | P-002 | Unwirksame Startprofile | Nicht implementierte Profile aus der interaktiven Betaauswahl entfernen; nur GPU-Kandidat, Zusatzmetrik und klarer CPU-Fallback werden angezeigt | `profiles.py`, `tui.py`, `pw.py`, Tests, README | Keine Persistenz; die bisherige Nummernfolge 1–7 ändert sich bewusst für ehrliche Beta-UX | Mittel | Verhindert irreführende Nutzererwartung und reduziert Auswahlkomplexität | Interaktiver Smoke-Test, Profil-/CLI-Tests; Rückrollbar über vorherige UI | geplant |
| 3 | P-003 | Irreführender Overkill-Text | Begriff und Beschreibung zu „Zusätzliche KDF-Arbeit (keine zusätzliche Zufallsentropie)“ ändern | `tui.py`, `README.md`, `verify_entropy.py`-Hinweis | Keine Funktionsmigration | Niedrig | Korrekte Sicherheitskommunikation bei gleichem Verhalten | Text-/Smoke-Review und Regression | geplant |
| 4 | P-004 | Falscher Log-Rotationsclaim | README auf zeitgestempelte Logdatei ohne Retention/Rotation korrigieren | `README.md` | Keine | Niedrig | Dokumentation entspricht Implementierung | Dokumentationsreview | geplant |
| 5 | P-005/P-008 | Fehlende Delivery-Hygiene | Minimalen CI-Workflow für Syntax, Unit-Suite und CLI-Hilfe; zentrale `VERSION`; klarer `--version`-Schalter | `.github/workflows/verify.yml`, `version.py`, `pw.py`, Tests, README | GitHub Actions läuft erst nach späterem Commit; lokal keine Nebenwirkung | Niedrig | Wiederholbare Beta-Prüfung und eindeutig identifizierbarer Stand | Lokale Ausführung der gleichen Befehle, YAML-/CLI-Review | geplant |
| 6 | P-006 | Sprach-/Terminologie-Mix | Kernprompts und Fehlermeldungen konsistent auf Deutsch stellen; bestehende Funktion unverändert lassen | `tui.py`, README | Keine | Niedrig | Verständlicher Erstkontakt für deutsche private Beta | Interaktiver Smoke-Test | geplant |
| 7 | P-007 | Nicht verifizierte Zielhardware | Release-Dokumentation mit Zielhardware-Checkliste und expliziten `NOT VERIFIED`-Grenzen abschließen | `README.md`, `audit/release_readiness.md` | Erfordert echte Zielhardware für spätere Schließung | Niedrig | Keine falschen Cross-Platform-/CUDA-Versprechen | Hardwareprotokoll, wenn verfügbar | geplant |
| 8 | P-009 | Secret-Scan-Fehlalarm | Testplaceholder neutralisieren, ohne die tatsächliche Redaktionsprüfung zu schwächen | `tests/test_log_redaction.py` | Keine | Niedrig | Klarere Security-Scan-Signale | Erneuter Secret-Scan und Unit-Test | geplant |

## Nicht priorisiert für die private Beta

| Thema | Entscheidung | Begründung |
|---|---|---|
| Echte GPU-PBKDF2/CUDA-Passworterzeugung | Später prüfen | Sicherheitsreview, Zielhardware und Performancebeleg fehlen; kein Beta-Blocker für CPU-first-Positionierung. |
| Native Android-App/APK | Ausgeschlossen | Vereinbarte Produktgrenze ist reine Python-CLI. |
| Passwortmanager, Vault oder Synchronisation | Ausgeschlossen | Ändert Threat Model, Datenschutz, Storage und Produktumfang grundlegend. |
| Alle Siebenprofile technisch implementieren | Später | Kein belegter Betanutzen gegenüber einer kleineren, ehrlichen Auswahl. |
| Breiter öffentlicher Launch | Nach privater Beta | Fehlen von Nutzerfeedback, Zielhardwaretests, Lizenz-/Supportentscheidung und Installationspaket für allgemeine Nutzer. |
