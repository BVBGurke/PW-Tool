# Geprüfte Open-Source-Kandidaten

Die Recherche bewertet nur Komponenten für **Benchmarking, CUDA-Diagnose und GPU-Metriken**. Passworterzeugung, CSPRNG und Secret-Handling bleiben projektintern und auf Standardbibliotheken gestützt. Keine externe Bibliothek erhält Passwort-, Seed- oder Systemmix-Inhalte.

| Projekt | Qualitätssignale | Technischer Nutzen | Entscheidung |
|---|---|---|---|
| [psf/pyperf](https://github.com/psf/pyperf) | 950 Sterne, aktiv bis 5. August 2026, MIT; Python-Software-Foundation-Projekt | Kalibrierte wiederholte Messungen, Worker-Prozesse, Instabilitätsprüfung, JSON-Ergebnisse, Speichertracking und Vergleichsläufe | **Übernehmen als optionale Benchmark-Extra**, nicht als Laufzeitabhängigkeit der CLI. |
| [cupy/cupy](https://github.com/cupy/cupy) | 12.256 Sterne, aktiv bis 18. August 2026, MIT; CUDA-/ROCm-Array-Bibliothek mit Streams, RawKernels und CUDA-Runtime-APIs | Bereits konzeptionell Teil des Projekts; ermöglicht CUDA-Events und RawKernel-Prototypen | **Beibehalten als optionale CUDA-Extra**. Nur für nachweislich parallele, große Batches. Kein GPU-KDF-Versprechen ohne echten Kernel-/Benchmark-Nachweis. |
| [XuehaiPan/nvitop](https://github.com/XuehaiPan/nvitop) | 7.111 Sterne, aktiv bis 27. Juli 2026, Apache-2.0; NVML-basierte Linux-/Windows-Metriken | GPU-Auslastung, Speicher, Prozesse und NVML-basierte Metriken, ohne `nvidia-smi` parsen zu müssen | **Nicht als Runtime-Abhängigkeit übernehmen.** Optionales, externes Diagnosewerkzeug für RTX-Hardware und manuelle Profiling-Sitzungen empfehlen. |

## Entscheidungslogik

`pyperf` eignet sich für reproduzierbare CPU- und End-to-End-Messungen, weil es Warm-ups, wiederholte Worker-Läufe und statistische Auswertung unterstützt. Es wird bewusst nicht für die normale Passwortausgabe importiert.

CuPy bleibt das bevorzugte optionale CUDA-Fundament, weil das Projekt bereits CuPy nutzt und es CUDA-Events, Streams sowie RawKernel-Unterstützung bereitstellt. Die aktuelle Implementierung verwendet jedoch nur GPU-Zufallsbytes und führt PBKDF2 per `hashlib` auf der CPU aus. Dieser Fakt bestimmt die weitere Umsetzung: Ein CUDA-Backend wird zunächst sauber messen und dispatchen; ein echter GPU-Kernel wird nur für Workloads und Funktionen geplant, die Sicherheits- und Performancekriterien erfüllen.

`nvitop` dient als bewährtes externes Analysewerkzeug auf echter NVIDIA-Hardware. Seine NVML-Nutzung ist nützlich, jedoch für eine schlanke Passwort-CLI als eingebettete Abhängigkeit unnötig. Im `-log`-Modus implementiert PW-Tool daher nur eine geringe, optionale eigene NVML-Probe, sofern die minimale NVML-Bindung verfügbar ist; andernfalls bleibt die Energie-/GPU-Metrik klar als nicht verfügbar markiert.

## Quellen

[1] [psf/pyperf – Toolkit to run Python benchmarks](https://github.com/psf/pyperf)

[2] [cupy/cupy – NumPy & SciPy for GPU](https://github.com/cupy/cupy)

[3] [XuehaiPan/nvitop – NVIDIA GPU monitor and APIs](https://github.com/XuehaiPan/nvitop)
