# Release Readiness: PW-Tool Private Beta 0.1.0b1

## Launch-Checkliste

| Kriterium | Status | Evidenz / Begründung | Owner / Restmaßnahme |
|---|---|---|---|
| Alle P0-Probleme sind behoben oder der Release ist ausdrücklich gestoppt. | erfüllt | Im Audit wurden keine P0-Befunde festgestellt. | — |
| Kritische P1-Probleme sind behoben oder mit begründetem Risiko akzeptiert. | mit Restrisiko akzeptiert | Batchlimit, wirksame Optionen, korrekte Entropiekommunikation, Version/CI und Dokumentationskorrekturen umgesetzt. Zielhardwarelücken bleiben. | Projektinhaber: Linux-only Beta-Scope einhalten. |
| Der relevante Production Build wurde erfolgreich erzeugt und geprüft. | erfüllt im Beta-Scope | Lokaler Wheel-Build `pw_tool-0.1.0b1-py3-none-any.whl` erfolgreich; Inhalt geprüft. | Vor breiter Verteilung Fresh-install-Test wiederholen. |
| Relevante automatische Tests sind ausgeführt; Fehler sind bewertet. | erfüllt | 22 Unit-Tests; 7/7 und 5/5 bestehende Regressionstests bestanden. | CI wird erst mit späterem Push aktiv. |
| Es sind keine bekannten kritischen Crashes in Kern-Journeys offen. | erfüllt im Linux-Scope | Interaktiver Start, Eingabefehler, Erzeugung, CPU-Fallback und Exit erfolgreich geprüft. | Windows/macOS nachtesten. |
| Performance ist für kritische Journeys geprüft oder die Testlücke akzeptiert. | mit Restrisiko akzeptiert | Linux-CPU-Benchmarks vorhanden; RTX/ARM64/Energie nicht geprüft. | Keine GPU-/Energieclaims; Zielhardwareprotokoll nachholen. |
| Security- und Dependency-Risiken sind geprüft und angemessen behandelt. | erfüllt im verfügbaren Scope | CSPRNG-/Fallback-/Logger-Tests, `pip-audit` ohne bekannte Befunde, Secret-Scan ohne Befunde. | Vor GA unabhängigen Security-Review erwägen. |
| Datenschutzrelevante Datenflüsse und sensible Logs sind im verfügbaren Scope geprüft. | erfüllt im statischen Scope | Keine statischen Netzwerkaufrufe im Produktpfad; `-log` ist Opt-in und redigiert Metadaten. | Logdateien nach Diagnosen manuell löschen. |
| UI, Accessibility und Design-System-Konsistenz sind für zentrale Journeys geprüft. | mit Restrisiko akzeptiert | Deutsche Kerntexte, Tastaturflow und Terminalfeedback geprüft. | Screenreader/Windows Terminal/kleine Terminals nicht geprüft. |
| Onboarding, Empty-, Loading- und Error-States sind für zentrale Journeys geprüft. | erfüllt im Linux-Scope | Installation dokumentiert; Spinner, Eingabefehler und CUDA-CPU-Fallback beobachtet. | Fresh-install- und Ziel-OS-Test ergänzen. |
| Offline-, Timeout- und Netzwerkfehlerverhalten ist geprüft, soweit relevant. | nicht zutreffend | Produktpfad hat keine Netzwerkabhängigkeit. | Statischen Netzaufruf-Scan bei künftigen Änderungen wiederholen. |
| Zielplattformen, Geräteklassen und Eingabemethoden sind angemessen geprüft. | nicht erfüllt für Multi-Plattform | Nur Linux x86-64 geprüft. | Beta zunächst Linux x86-64; Windows/macOS/Android als Expansionsbedingung. |
| Release-Konfiguration, Versionierung, Umgebungsvariablen und Signing sind geprüft, soweit relevant. | mit Restrisiko akzeptiert | `pyproject.toml`, `--version`, Wheel und CI-Workflow vorhanden; keine Signierung im privaten Beta-Scope. | Vor öffentlicher Verteilung Versionierungs-/Signierentscheidung treffen. |
| Monitoring, Crash Reporting, Logging und Supportfähigkeit sind bewertet, soweit vorgesehen. | mit Restrisiko akzeptiert | Opt-in Diagnoseprotokoll mit Rechten/Whitelist vorhanden; kein Crash Reporting geplant. | Beta-Feedbackkanal und Supportowner vor Einladungen festlegen. |
| Produkt- und technische Dokumentation sind für den Release aktualisiert. | erfüllt | README, Audit-, Strategie-, Roadmap- und Benchmarkdokumente aktualisiert. | Hardwarecheckliste mit Zielmessungen ergänzen. |
| Es existieren keine als fertig dargestellten Fake-, Dummy- oder Placeholder-Funktionen. | erfüllt im Beta-UI | Nicht wirksame Profile wurden entfernt; CUDA wird klar als nicht verifizierte/gesperrte Option dokumentiert. | Bei neuen Profilen Wirkung und Tests vor UI-Freigabe nachweisen. |

## Entscheidung: Conditional Go

PW-Tool ist **realistisch marktfähig für eine eingeschränkte private Beta**, wenn die folgenden Bedingungen erfüllt sind:

1. Die Einladung beschränkt sich zunächst auf **Linux-x86-64-Nutzer mit Python 3.10+** und erklärt den CPU-Pfad als Referenz.
2. Kommunikation und README enthalten **keine** Zusage zu CUDA-/RTX- oder ARM64-Performance und **keine** Aussage über native Android-App-Unterstützung.
3. Vor jeder externen Verteilung wird der erzeugte Wheel in einer frischen Linux-Python-Umgebung installiert und die Kernjourney dort durchlaufen.
4. Ein Projektowner legt einen privaten Feedback-/Bugkanal, erwartete Reaktionszeiten und die Beta-Nutzungsgrenze fest.
5. Windows, macOS, Android/ARM64 und RTX/CUDA bleiben bis zu echten Tests ausdrücklich `NOT VERIFIED` und werden erst nach dokumentierten Zielhardwaremessungen zum unterstützten Scope hinzugefügt.

## Rückfallplan

Wenn ein P0-Sicherheitsproblem, ein reproduzierbarer Kern-Journey-Crash oder ein Secret-Leak im `-log`-Pfad gemeldet wird, wird die Beta-Verteilung gestoppt. Der CPU-Referenzpfad bleibt die Rückfallbasis; CUDA bleibt deaktiviert, bis eine sichere, gemessene und geprüfte Implementierung vorliegt.
