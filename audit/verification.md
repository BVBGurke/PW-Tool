# Verifikationsprotokoll

## VERIFIED

| Prüfung | Befehl bzw. Nachweis | Ergebnis |
|---|---|---|
| Python-Unit-Suite | `python3 -m unittest discover -v` | 19 Tests bestanden: Systemmix, Benchmarkmetriken, CPU-Backend, Dispatcher, Log-Redaktion und Profile/CLI. |
| Bestehender Kurztest | `python3 quick_verify.py` | 7/7 bestanden: CPU-Entropie, Passwörter, Batch, CUDA-Fallback, Iterationsskalierung, Zeichensätze, lokaler Systemmix. |
| Bestehende Verifikationssuite | `python3 verify_entropy.py` | 5/5 bestanden: CUDA-Fallback, Eindeutigkeit, Verteilungssanitycheck, KDF-Zeit, Zeichensatzvalidierung. |
| CPU-Backend | `tests/test_cpu_backend.py` | Erzeugt valide Batches und liefert getrennte Zeitwerte für Systemmix, CPU-PBKDF2 und Passwortableitung. |
| Dispatcher | `tests/test_dispatcher.py` | Kleine Batches, CPU-only, CUDA-Nichtverfügbarkeit und simulierte profitable große CUDA-Lasten verhalten sich wie spezifiziert. |
| `-log`-Sicherheit | `tests/test_log_redaction.py` und manueller `-log`-Smoke-Test | Ohne `-log` keine Logdatei; mit `-log` JSONL-Datei mit Modus 600 und ohne erlaubte Secret-Felder. |
| Siebenprofil-TUI | Interaktiver Pipe-Smoke-Test | Enter startet die aktuelle Auswahl; Profilübersicht, CPU-Fallback und Passwortausgabe funktionierten. |
| Python-only-Grenze | Artefaktsuche | Keine APK-, Kotlin-, Gradle- oder Wrapper-Artefakte im Projekt. |
| CPU-Benchmarks | Vier Profile, 1 Warm-up, 5 Wiederholungen | Ergebnisse in `audit/benchmarks/` und `audit/benchmark_results.md`. |

## NOT VERIFIED

| Ziel | Grund | Konkreter nächster Schritt |
|---|---|---|
| RTX 4070 SUPER: Ursache der beobachteten ca. 70 s | Keine NVIDIA-GPU, kein Treiber und kein CuPy in der Ausführungsumgebung | Auf dem RTX-System `nvidia-smi`, `python benchmark/run_profiles.py --profile large --backend auto --warmups 1 --repeats 7 --memory` und `python pw.py -log` ausführen. |
| RTX 4070 SUPER: echter CUDA-Gewinn | Der aktuelle sichere Passwortpfad besitzt bewusst keine auditiert sichere GPU-PBKDF2 | Erst einen unabhängig geprüften, sicheren GPU-Workload implementieren; danach CUDA Events, End-to-End-Zeit und NVML messen. |
| ARM64-Android: ca. 4,5 s und Energie | Kein ARM64-Gerät/Android-Terminal verfügbar | Auf Zielgerät die CPU-Benchmarkprofile mit Thermik-/Akkubeobachtung wiederholen. |
| Windows/x86-64 | Keine Windows-Laufzeit verfügbar | Gleiche Unit-Suite und Benchmarks in Python 3.10+ auf Windows ausführen. |
| macOS/ARM64 | Keine macOS-Laufzeit verfügbar | Gleiche Unit-Suite und Benchmarks mit nativer Python-Laufzeit auf Apple Silicon ausführen. |
| Physische Energiekennzahlen | Keine NVML/RAPL-Quelle in dieser Sandbox | Optional `nvitop`/NVML für GPU und RAPL, sofern verfügbar, im `-log`-Modus korrelieren. |

## Sicherheitsreview

| Bereich | Befund |
|---|---|
| CSPRNG | Die CPU-Entropie kommt aus `os.urandom`; Systemdatei-Hashes sind nur optionales HMAC-Zusatzmaterial. |
| GPU-Zufall | Ein nicht auditierter CuPy-Zufallsgenerator wird nicht mehr als Passwort-Primärentropie akzeptiert. |
| Logs | Der Logger hat eine Schema-Whitelist; verbotene Schlüssel und unsichere Ereignisnamen werden verworfen bzw. abgelehnt. |
| Terminal | Die gewünschte Passwortausgabe bleibt sichtbare Produktfunktion. Der Diagnoselog übernimmt keine Passwortwerte. |
| Persistenz | Keine Passwort-, Seed-, Digest- oder Systemmix-Persistenz. |
| Fehlerpfade | Backend-/CUDA-Fehler führen auf den CPU-Pfad zurück; der Dispatcher protokolliert nur den redigierten Grund, wenn `-log` aktiv ist. |
| GPU-Speicher | Keine behauptete sichere Speicherlöschung. CUDA-Passwortausführung bleibt gesperrt, bis eine auditierte Implementierung vorliegt. |
