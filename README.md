# PW-Tool

PW-Tool ist eine **reine Python-CLI** für lokale Passworterzeugung. Das Projekt enthält keine APK, keine native Mobile-App und keine Telemetrie. Es läuft auf macOS, Windows, Linux sowie geeigneten Android-Python-Terminalumgebungen. NVIDIA/CUDA bleibt als optionaler, messbasierter Kandidat vorgesehen; ein sicherer CPU-/ARM64-Pfad ist immer vorhanden.

> Die GPU-Präferenz wird respektiert, aber keine GPU wird blind erzwungen. PW-Tool wählt CUDA nur dann für einen konkreten Workload, wenn eine echte Messung einen sicheren End-to-End-Vorteil zeigt. Auf Android-ARM64 ohne NVIDIA-CUDA bleibt der CPU-Fallback aktiv.

## Installation und Start

PW-Tool benötigt Python 3.10 oder neuer. Die reguläre Oberfläche ist eine lokale **Textual-TUI**; `rich` bleibt ausschließlich für den vorhandenen Legacy-/Fallback-Code installiert. Die Abhängigkeiten werden aus `requirements.txt` beziehungsweise den Paketmetadaten installiert.

```bash
python -m pip install .
pw-tool --version
pw-tool

# Alternativ direkt aus dem geklonten Arbeitsbaum:
python -m pip install -r requirements.txt
python pw.py
```

Für einen vollständig optionalen Benchmark-Werkzeugsatz:

```bash
python -m pip install -r requirements-benchmark.txt
```

`pyperf` ist nur für externe, statistische Benchmarks vorgesehen. CuPy und NVML-Werkzeuge bleiben bewusst optional und werden nicht zur normalen Passwortausgabe importiert.

## Sitzungskonfiguration und Bedienung

Beim Start zeigt PW-Tool ein Textual-Formular. Passwortlänge, Anzahl, Zeichensatz, optionale Systemmischung, zusätzliche KDF-Arbeit sowie die wirksamen Beta-Optionen werden dort **einmal pro Sitzung** festgelegt. Jede weitere Erzeugung verwendet diese Auswahl unverändert und erzeugt ausschließlich neue lokale Werte; die Konfiguration wird weder gespeichert noch erneut abgefragt.

| Feld oder Option | Standard | Wirkung |
|---|---:|---|
| Passwortlänge | 64 | Erlaubt Werte von 8 bis 256 Zeichen. |
| Anzahl | 1 | Erlaubt 1 bis 10.000 Passwörter pro Lauf. |
| Zeichensatz | `alphanumeric` | Wählt den Zeichenvorrat der Passwortableitung. |
| CUDA als Kandidat | Aktiv | Prüft CUDA für große Batches; der sichere CPU-/ARM64-Fallback bleibt verfügbar. |
| Ergebnis-Metriken | Inaktiv | Zeigt nur nicht sensitive Phasenzeiten in der Ergebnisansicht. |
| Systemmischung | Inaktiv | Aktiviert die dokumentierte, optionale lokale Zusatzmischung. |
| Zusätzliche KDF-Arbeit | Inaktiv | Erhöht die lokale Rechenarbeit bewusst und kann die Laufzeit verlängern. |

Nicht sichtbare Zukunftsthemen wie Hybrid-Pipeline, Energieprofil oder CUDA-Warm-up sind **nicht** als Beta-Funktion implementiert und werden daher nicht auswählbar dargestellt.

### Schmale und mobile Terminals

Bei einer Terminalbreite unter 72 Zeichen schaltet die Textual-Oberfläche auf eine **Kompaktansicht** mit vertikal angeordneten Bereichen. Status, Backendentscheidung und Ergebnisse bleiben verfügbar. Lange Passwörter werden gefaltet statt durch eine Ellipse abgeschnitten, sodass alle Zeichen sichtbar bleiben. Breite Terminals verwenden ein mehrspaltiges Desktop-Layout.

| Tastenkürzel | Funktion |
|---|---|
| `Strg+G` | Erzeugt Passwörter mit der aktuellen Sitzungskonfiguration. |
| `Strg+C` | Kopiert die zuletzt erzeugten Passwörter, sofern die Zwischenablage verfügbar ist. |
| `Strg+Q` | Beendet die Anwendung. |

## CUDA: aktueller Sicherheits- und Performance-Status

Das vorherige CUDA-Modul erzeugte lediglich Seed-/Salt-Bytes über CuPy und führte PBKDF2 anschließend mit `hashlib.pbkdf2_hmac` auf der **CPU** aus. Es war daher keine echte GPU-PBKDF2-Beschleunigung. Die Architektur misst diesen Unterschied jetzt explizit und behauptet keine GPU-KDF, die nicht existiert.

Passwortseeds müssen kryptografisch sicher sein. Ein nicht explizit auditierter GPU-Zufallsgenerator darf nicht zur primären Passwortentropie werden. Deshalb verwendet PW-Tool weiterhin OS-CSPRNG. CUDA wird erst dann als Passwortbackend freigegeben, wenn ein auditierter sicherer GPU-Pfad und eine echte Leistungsmessung vorliegen. Bis dahin dient der CUDA-Code als Diagnose-/Profiling-Kandidat und der Dispatcher fällt sicher auf CPU zurück.

| Workload | Aktuelle Auswahlregel |
|---|---|
| Einzelpasswort / kleiner Batch | CPU-/ARM64-Pfad; vermeidet CUDA-Initialisierung und Transfer-Overhead. |
| Großer Batch | CUDA wird als Kandidat geprüft. Die Auswahl verlangt eine kalibrierte End-to-End-Geschwindigkeit von mindestens 10 % gegenüber CPU. |
| CUDA fehlt, fehlschlägt oder ist nicht auditiert | Sofortiger CPU-Fallback mit transparenter Begründung. |
| Android-ARM64 ohne NVIDIA-CUDA | Sicherer CPU-Fallback; keine vorgetäuschte GPU-Beschleunigung. |

## Diagnoselog: nur mit `-log`

Ohne Argument entstehen **keine Diagnosedateien**. Erst `-log` oder `--log` aktiviert lokal gespeicherte, zeitgestempelte JSONL-Metadaten. Die aktuelle Beta implementiert keine automatische Retention oder Rotation; Logdateien bleiben lokale Diagnoseartefakte und sollten nach einer Untersuchung manuell gelöscht werden.

```bash
python pw.py -log
python pw.py -log --log-directory ./diagnostics
```

Der Logger verwendet restriktive Dateirechte, soweit die Plattform dies unterstützt. Das Schema erlaubt ausschließlich Backendentscheidung, Workloadklasse, Batchgröße, Iterationszahl, Dauer pro Phase und verfügbare Speicher-/Energiemetriken. Passwörter, Seeds, Entropie, Hashes, Digest-Werte, Dateipfade und Quellinhalte werden verworfen.

## Benchmarking

Das integrierte Harness misst Warm-up, wiederholte Läufe, Median, p95, p99, Durchsatz und optional die Python-Allokationsspitze. Es druckt keine Passwörter oder Entropiematerialien.

```bash
# CPU-Referenz für ein Einzelpasswort
python benchmark/run_profiles.py --profile single --backend cpu --warmups 1 --repeats 7 --memory

# Automatische Backendentscheidung für einen großen Batch
python benchmark/run_profiles.py --profile large --backend auto --warmups 1 --repeats 7 --memory

# JSON-Ergebnis für Vergleich oder CI
python benchmark/run_profiles.py --profile medium --backend auto --json
```

| Profil | Anzahl | Länge | PBKDF2-Iterationen |
|---|---:|---:|---:|
| `single` | 1 | 24 | 200.000 |
| `small` | 8 | 24 | 200.000 |
| `medium` | 128 | 32 | 200.000 |
| `large` | 1.024 | 32 | 200.000 |

Die interaktive Beta begrenzt die Batchgröße auf **10.000 Passwörter**, um versehentliche lokale CPU-/RAM-Überlastung zu vermeiden.

## Lokale Systemdatei-Mischung

PW-Tool kann zusätzlich drei bis fünf feste, nicht sensitive lokale Systemdateien lesen, in 64-KiB-Blöcken hashen und über HMAC-SHA-512 mit frischem OS-Zufall kombinieren. Das ist eine **optionale Zusatzmischung**, keine geheime Entropiequelle und kein Ersatz für den OS-CSPRNG. Weniger als drei lesbare Quellen führen zu einem sicheren, sichtbaren Fallback auf OS-Zufall.

| Plattform | Feste Kandidaten |
|---|---|
| macOS | Systemversion, Zeitzonendateien, CoreFoundation, Hosts-Datei |
| Windows | System-DLLs, Hosts-Datei, `win.ini` |
| Linux | `/etc/os-release`, `/proc/version`, Zeitzonendateien, Hosts-Datei |
| Android-Terminal | Öffentliche Systemkonfigurationsdateien, soweit die Sandbox sie erlaubt |

## Prüfen

```bash
# Syntax aller Module
python -m py_compile *.py backends/*.py benchmark/*.py tests/*.py

# Vollständige Unit- und Regressionstests
python -m unittest discover -v

# Bestehende Korrektheits-/Laufzeitprüfung
python verify_entropy.py
```

## Projektstruktur

```text
pw.py                    Interaktiver CLI-Einstieg, -log-Option und --version
textual_ui.py            Responsive Textual-TUI mit Worker-basierter Erzeugung
tui.py                   Veraltete Rich-Oberfläche als Legacy-/Fallback-Code
version.py               Zentrale private-Beta-Version
pyproject.toml           Deklarative Paket- und Konsolenmetadaten
profiles.py              Zwei wirksame, nicht persistierte Beta-Optionen
dispatcher.py            GPU-first-Kandidat mit CPU-/ARM64-Fallback
backends/                Gemeinsame Schnittstelle sowie CPU-/CUDA-Backends
benchmark/               Profile, Perzentile, Warm-up-Runner und Benchmark-CLI
diagnostics.py           Whitelist-basierter, secret-freier Opt-in-Logger
password_engine.py       HMAC-/Rejection-Sampling-Passwortableitung
cpu_engine.py            OS-CSPRNG, Systemmix und CPU-PBKDF2
cuda_engine.py           CUDA-Detection und getrennte Diagnosephasen
system_mix.py            Lokale feste Zusatzmischung
audit/                   Architektur-Baseline und GitHub-Gem-Bewertung
tests/                   Dispatcher-, Logger-, Backend-, Benchmark- und Textual-Tests
```

## Verifizierungsgrenzen

Die im Repository vorhandene Linux-x86-64-CPU wurde getestet. Eine RTX 4070 SUPER, Windows, macOS und Android-ARM64 standen in der aktuellen Ausführungsumgebung nicht zur Verfügung. Für diese Ziele werden daher keine Leistungs- oder Energieversprechen behauptet. Die Benchmark-Befehle und die `-log`-Metriken dienen dazu, die Backendentscheidung auf echter Zielhardware nachzuvollziehen.

## Quellen

[1] [psf/pyperf – Python benchmark toolkit](https://github.com/psf/pyperf)

[2] [CuPy – GPU array library with CUDA events and streams](https://github.com/cupy/cupy)

[3] [nvitop – NVML-based NVIDIA monitoring](https://github.com/XuehaiPan/nvitop)

[4] [Python documentation: `secrets`](https://docs.python.org/3/library/secrets.html)

[5] [Python documentation: `hashlib`](https://docs.python.org/3/library/hashlib.html)

[6] [Textual – Python framework for terminal user interfaces](https://textual.textualize.io/)
