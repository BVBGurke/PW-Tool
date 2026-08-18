# Produktstrategie: PW-Tool Private Beta

| Element | Entscheidung | Begründung / Evidenz | Offene Validierung |
|---|---|---|---|
| Zielgruppe | Technikaffine private Beta-Nutzer mit Python-/Terminal-Grundkenntnissen | Produkt ist eine lokale Rich-TUI/CLI ohne grafisches Installer- oder Kontomodell | Bedarf und Verständnis über Beta-Feedback prüfen |
| Kernproblem | Schnelle, lokale Passworterzeugung ohne Netzwerk, Konto oder Persistenz | CPU-Kernjourney, lokale CSPRNG-Nutzung und keine statischen Netzwerkmuster nachgewiesen | Erstnutzungsverständnis und tatsächliche Nutzungsfrequenz |
| Nutzenversprechen | Transparenter lokaler Passwortgenerator mit sicheren Defaults und nachvollziehbarem CPU-Fallback | CSPRNG-/Fallback-/Log-Tests und Dokumentation vorhanden | Usability des Optionsumfangs |
| Wichtigste User Journeys | Installation → Start → Passwort konfigurieren → generieren/anzeigen → wiederholen/beenden; optional `-log`; Benchmark separat | TUI, README und Tests decken Teile der Journeys ab | Frische Installation auf Windows/macOS/Android |
| Kernfeatures | Passwortlänge, zwei Zeichensätze, Batch, optionaler Systemmix, CPU-Fallback, Opt-in-Diagnostik, Benchmark-CLI | Vorhandene Implementierung und Tests | Zeichen-Ausschlüsse, Passphrases und Copy-Integration sind keine Beta-Voraussetzung |
| Differenzierung | Privacy-orientierte lokale CLI mit offen dokumentierten Mess- und Hardwaregrenzen | Keine Netzwerkaufrufe im Produktpfad; Audit-/Benchmarkunterlagen vorhanden | Vergleich mit realen Nutzeralternativen |
| MVP | CPU-first Python-CLI auf Linux mit sauberer Installation, klaren Grenzen und belastbarer Regression | Linux-CPU und Tests liegen als Evidenz vor | Fresh-install-Test auf sauberer Umgebung |
| Launch-Version | Private Beta, nicht allgemeiner öffentlicher Release | CUDA/RTX, Windows, macOS und Android nicht verifiziert; Produktprofile benötigen Bereinigung | Beta-Kriterien nach P1-Umsetzung erneut bewerten |
| Spätere Features | Auditiertes CUDA-Backend, Zielhardware-Tests, optionale mehrsprachige CLI, ausgebauter Generatorumfang | Erfordert Sicherheits-, Performance- und Nutzungsbeleg | Produktpriorisierung nach Beta-Feedback |
| Nicht priorisierte Funktionen | Vault, Cloud-Synchronisation, Passwortmanager, APK/native App, Telemetrie | Außerhalb des vereinbarten Threat Models und der Python-CLI-Grenze | Keine |

## Beta-Positionssatz

> PW-Tool ist ein lokaler Python-Terminalgenerator für private technische Tests. Er erzeugt Passwörter ohne Konten oder Netzwerkpflicht, nutzt einen sicheren CPU-Referenzpfad und zeigt Hardware-/Diagnosegrenzen offen an. CUDA ist keine zugesicherte Beta-Leistungseigenschaft.

## Messaging-Grenzen

| Zulässig | Nicht zulässig |
|---|---|
| „Lokal, CPU-first, mit sicherem Fallback.“ | „GPU-beschleunigte Passworterzeugung auf allen Geräten.“ |
| „CUDA wird nur nach messbarem Vorteil und Sicherheitsprüfung verwendet.“ | „RTX 4070 SUPER ist schneller“ ohne echte Messung. |
| „Android-Terminal kann den CPU-Pfad nutzen, soweit die Umgebung Python ausführt.“ | „Android-GPU-/native App-Unterstützung.“ |
| „`-log` protokolliert redigierte Diagnosemetadaten.“ | „Vollständige Logrotation/Retention“, solange diese nicht implementiert ist. |
