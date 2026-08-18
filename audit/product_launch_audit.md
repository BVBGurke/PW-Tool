# Product-Launch-Audit: PW-Tool Private Beta

**Auditmodus:** Audit + kontrollierte Umsetzung  
**Releasekontext:** Private Beta für technisch versierte Desktop-/Terminal-Nutzer  
**Auditdatum:** 18. August 2026  
**Prüfumgebung:** Linux x86-64, CPython 3.12.3, keine NVIDIA-GPU, kein Windows/macOS/Android-Gerät verfügbar

## Executive Summary

PW-Tool ist als lokaler Python-CLI-Passwortgenerator für eine begrenzte technische Beta grundsätzlich nachvollziehbar aufgebaut: Die CPU-Referenzfunktion arbeitet lokal, Tests decken zentrale Erzeugungs-, Dispatcher- und Log-Redaktionspfade ab, die Diagnose ist explizites Opt-in und die bisherige CUDA-Übertreibung wurde im Code und in der Dokumentation eingegrenzt. Der lokale CPU-Workflow und die vorhandenen Benchmarks liefern ausreichende erste Evidenz für eine weitere kontrollierte Beta-Prüfung.

Die aktuelle Beta ist jedoch **noch nicht releasebereit**, weil mehrere Nutzer sichtbare Profile keine Laufzeitwirkung besitzen, die Batchgröße keine Obergrenze hat und damit eine lokale Ressourcenerschöpfung auslösen kann, der „Overkill“-Text eine nicht belegte Entropiesteigerung suggeriert und Delivery-Grundlagen wie ein reproduzierbares Paket-/CI-Verfahren fehlen. Zusätzlich sind CUDA/RTX, Windows, macOS und Android/ARM64 nicht verifiziert. Die nachfolgenden P0/P1-Maßnahmen werden diese Risiken gezielt schließen oder als explizite Beta-Bedingung dokumentieren.

| Bereich | Belegter Zustand | Größtes Risiko bzw. Chance | Priorität | Evidenz/Prüfstatus |
|---|---|---|---|---|
| Architektur | CPU-Backend, Dispatcher, optionale CUDA-Gate-Logik und Rich-TUI sind klar getrennt | Mehrere Profilflags sind bisher nur UI-Zustand ohne Laufzeitwirkung | P1 | bestätigt durch `profiles.py`, `pw.py`, `dispatcher.py` |
| Produktqualität | Lokale Passworterzeugung und transparente CPU-Fallbackausgabe funktionieren | Produktversprechen und tatsächliche Profilfunktionen müssen deckungsgleich werden | P1 | bestätigt durch Code/README/TUI-Abgleich |
| Performance | Reproduzierbare Linux-CPU-Baseline vorhanden | RTX/ARM64 und Energie nicht verifiziert; keine echte sichere CUDA-KDF | P1 | CPU: verifiziert; Zielhardware: nicht geprüft |
| UX/UI & Accessibility | Interaktiver Rich-Flow mit Validierung und Spinner vorhanden | Deutsche Zielansprache, aber gemischte Sprache sowie unklare „Overkill“-Semantik | P2 | bestätigt durch `tui.py` |
| Security & Privacy | OS-CSPRNG, Log-Whitelist und lokaler Zugriffspfad vorhanden | Unbegrenzte Batchgröße kann Speicher/CPU lokal erschöpfen | P1 | bestätigt durch `tui.py`, `backends/base.py`, `password_engine.py` |
| Tests & Delivery | 19 Unit-Tests und bestehende Regressionstests liefen zuvor grün | Kein projektkonfiguriertes Linting, keine CI, kein installierbares Paket-/Versionierungsmodell | P1 | bestätigt durch Tool-/Konfigurationsinventar |

## Problem Matrix

| ID | Problem | Kategorie | Priorität | Auswirkung | Evidenz/Fundstelle | Empfohlene Lösung | Abnahmebedingung | Status |
|---|---|---|---|---|---|---|---|---|
| P-001 | Batchgröße ist nach oben unbegrenzt | Stabilität / Security | P1 | Ein lokaler Fehleintrag kann sehr viele Passwortobjekte erzeugen und CPU/RAM überlasten | `tui.py:get_batch_count`, `GenerationRequest` und `generate_batch` prüfen nur `>=1` | Produktgrenze als Konstante einführen, in TUI und Request validieren, Fehlertext und Tests ergänzen | Extremwerte werden abgewiesen; zulässiger Großbatch bleibt benchmarkbar | bestätigt |
| P-002 | Die Profile 2–5 und 7 werden als Funktionen gezeigt, steuern die Laufzeit aber nicht | Produkt / UX / Architecture | P1 | Beta-Nutzer können Schutz-, Energie-, Warm-up-, Hybrid- und Diagnostikverhalten erwarten, das nicht stattfindet | `profiles.py` speichert nur Flags; `pw.py` liest faktisch nur 1 und 6; `dispatcher.py` kennt nur GPU-first/CPU-only | Unwirksame Profile bis zur Implementierung aus der TUI entfernen oder ihre Beschreibungen in ehrliche Hinweise ändern; konkrete Laufzeitwirkungen nur bei implementierter Funktion | Jede sichtbare Option verändert beobachtbar das Verhalten oder ist nicht auswählbar | bestätigt |
| P-003 | „Overkill Mode“ suggeriert zusätzliche Entropie | Security-Kommunikation / UX | P1 | Nutzer können langsamere Erzeugung fälschlich als sicherheitsrelevante Entropiesteigerung verstehen | `tui.py` Text „slower, more entropy“; CPU-Code erhöht nur PBKDF2-Iterationen | Text in „zusätzliche Rechenzeit, keine zusätzliche Zufallsentropie“ ändern und Dokumentation anpassen | Text und Test/Review verhindern die irreführende Behauptung | bestätigt |
| P-004 | Launch-Dokumentation verspricht rotierte Logs, Implementierung erzeugt nur zeitgestempelte Dateien | Produkt / Privacy-Dokumentation | P2 | Erwartete Log-Retention/Rotation ist nicht definiert | README Zeile 53; `diagnostics.py` ohne Rotation/Retention | Wort „rotierte“ entfernen oder echte Retention/Rotation klein und getestet implementieren | Dokumentation entspricht Code | bestätigt |
| P-005 | Fehlende Delivery-Automatisierung und Paketmetadaten | Delivery / Maintainability | P1 | Private Beta lässt sich nicht konsistent installieren, testen oder versionieren | Kein `pyproject.toml`, keine CI-/Lint-Konfiguration laut Inventar | Minimalen Paket-/Release-Check und CI-Workflow hinzufügen; Version zentral dokumentieren | Frischer Installations-/Testpfad ist beschreibbar und CI-Konfiguration prüft Tests | bestätigt |
| P-006 | Sprach- und Terminologie-Mix in Kernjourney | UX | P2 | Deutsche Beta-Nutzer erhalten teils englische Labels/Fehler und unpräzise Fachbegriffe | `tui.py` enthält deutsche und englische Prompts/Status | Beta-Sprache konsistent Deutsch; knappe Erklärungen ohne falsche Sicherheitsversprechen | Interaktiver Kernjourney ist konsistent lesbar | bestätigt |
| P-007 | CUDA-, RTX-, Windows-, macOS- und Android-/ARM64-Aussagen nicht auf Zielhardware geprüft | Cross-Platform / Performance | P1 | Kein belegtes Performance- oder Energieversprechen für Zielplattformen | Hardwareinventar, `audit/verification.md`, README | Als Beta-Bedingung dokumentieren; reproduzierbare Hardware-Checkliste bereitstellen | Kein Claim ohne Messung; Zieltestprotokoll liegt vor | bestätigt |
| P-008 | Kein projektkonfiguriertes Linting/Typing und keine CI | Qualität / Delivery | P2 | Künftige Änderungen können Qualitätsregressionen nicht automatisiert erkennen | Kein ruff/mypy/pytest/CI-Konfigurationsfile; Tools lokal nicht installiert | Minimalen, nicht invasiven CI-Testlauf und später optionalen Lint-Standard einführen | CI führt Syntax/Unit-Test aus; Linter-Policy ist dokumentiert | bestätigt |
| P-009 | Secret-Scan meldet einen Test-String als Fehlalarm | Delivery / Security | P3 | Scannerrauschen kann echte Befunde verdecken | `tests/test_log_redaction.py`, Scanergebnis „Secret Keyword“ auf Testplaceholder | Neutralen Testwert verwenden oder dokumentierte Scannerbaseline einführen | Secret-Scan bleibt aussagekräftig ohne echten Befund zu unterdrücken | bestätigt |

## Feature Audit

| Feature / Journey | Status | Qualität | Marktwert | Evidenz | Entscheidung | Begründung | Nächster Schritt |
|---|---|---|---|---|---|---|---|
| Lokale Passworterzeugung | vorhanden | gut | hoch | Unit-/Regressionstests, CPU-Benchmarks | behalten | Kernnutzen der Beta | Korrektheitstests beibehalten |
| Zeichensatz und Länge | vorhanden | ausreichend | hoch | TUI-Validierung und PasswordGenerator | verbessern | Flexible, aber noch begrenzte Konfiguration | Konsistente Sprache und Batchgrenze |
| CPU-Fallback | vorhanden | gut | hoch | Dispatcher-/CPU-Tests | behalten | Entscheidend für breite Terminal-Beta | Plattformcheckliste ergänzen |
| CUDA GPU-first | teilweise | unzureichend für Produktclaim | mittel | Secure-Gate blockiert reale GPU-Ausführung | refactoren / klar begrenzen | Keine echte sichere GPU-KDF und keine RTX-Messung | Experimentell dokumentieren; nicht als Beta-Vorteil vermarkten |
| Siebenprofile | teilweise | unzureichend | mittel | Nur 1 und 6 wirken im Einstieg | verbessern | Nützliche Steuerung nur bei ehrlicher Semantik | Nicht wirksame Profile ausblenden oder implementieren |
| Opt-in-Diagnostik | vorhanden | gut | mittel | Logger-Whitelist, Rechte, Tests | behalten | Hilft technischen Beta-Nutzern | Dokumentationsclaim korrigieren |
| Automatische Systemmix-Zusatzmischung | vorhanden | ausreichend | niedrig bis mittel | Feste Allowlist, Fallbacktests | behalten | Transparent optional; keine Primärentropie | Privacy-Hinweis beibehalten |
| Benchmark-CLI | vorhanden | ausreichend | hoch für Beta | Vier Profile, Metriken, JSON | behalten | Erlaubt reproduzierbare CPU-Nachweise | Zielhardware-Checkliste und CI ergänzen |

## Auditeinschränkungen

Der Audit konnte keinen echten NVIDIA-/RTX-Stack, keine Windows-, macOS- oder Android-ARM64-Laufzeit, keine physische Energie-Telemetrie und keine externen Beta-Nutzer beobachten. Diese Bereiche sind bewusst nicht als bestanden bewertet. Die Abhängigkeitsprüfung meldete keine bekannte Schwachstelle für die reguläre Anforderung `rich`; der Secret-Scanner meldete im Arbeitsbaum einen überprüften Test-Fehlalarm, die geprüfte Historie enthielt keine Befunde.
