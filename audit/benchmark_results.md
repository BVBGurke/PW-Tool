# Benchmark-Ergebnisse und Vergleich

**Umgebung:** Linux x86-64, CPython 3.12.3, virtuelle Intel-Xeon-CPU mit 6 logischen CPUs.  
**Messmethode:** `benchmark/run_profiles.py`, ein Warm-up, fünf Messläufe je Profil, CPU-only, Systemmix im Benchmark deaktiviert, Python-Allokationsmessung aktiv.  
**Nicht vorhanden:** NVIDIA-Treiber, `nvidia-smi`, CuPy, RTX 4070 SUPER und ARM64-Hardware.

## Aktuelle End-to-End-CPU-Messung

| Profil | Batch | Median | p95 | Durchsatz | Python-Allokationsspitze |
|---|---:|---:|---:|---:|---:|
| `single` | 1 | 0,162615 s | 0,178756 s | 6,15 Passwörter/s | 892 B |
| `small` | 8 | 0,157145 s | 0,159790 s | 50,91 Passwörter/s | 1.411 B |
| `medium` | 128 | 0,161424 s | 0,163982 s | 792,95 Passwörter/s | 11.259 B |
| `large` | 1.024 | 0,173824 s | 0,178566 s | 5.891,01 Passwörter/s | 84.475 B |

## Gemessene Phasenmediane

| Profil | CPU-PBKDF2 | Passwortableitung | Systemmix-Schalterprüfung |
|---|---:|---:|---:|
| `single` | 0,162456 s | 0,000091 s | 0,000009 s |
| `small` | 0,156893 s | 0,000208 s | 0,000008 s |
| `medium` | 0,159183 s | 0,002155 s | 0,000008 s |
| `large` | 0,156841 s | 0,017051 s | 0,000009 s |

Die Daten zeigen in dieser Umgebung, dass die PBKDF2-HMAC-SHA-512-Ableitung die End-to-End-Latenz klar dominiert. Die Passwortableitung bleibt selbst beim großen Batch klein gegenüber der KDF. Der große Batch amortisiert die einmalige KDF über viele Passwörter; deshalb steigt der Durchsatz stark, während die Einzel-Latenz ungefähr auf dem KDF-Niveau bleibt.

## Vorher-/Nachher-Kontext

| Backend / Aspekt | Vor Audit | Nach Audit | Interpretation |
|---|---:|---:|---|
| Linux-CPU, 200.000 Iterationen | 0,16 s in der bestehenden Einzeldurchlauf-Suite | 0,162615 s Median im neuen wiederholten Einzelprofil | Vergleichbar; der neue Wert enthält Warm-up-/Messstruktur und zusätzliche Trennung der Phasen. |
| Linux-CPU, 1.000.000 Iterationen | 0,79–0,80 s in bestehender Suite | Unverändert als optionaler Zusatzmodus | Kein Performanceversprechen; der Modus bleibt absichtlich langsamer. |
| Backendentscheidung | Nur GPU-Verfügbarkeit/Fallback | GPU-first-Kandidat mit Batchschwelle und messbasierter Kalibrierung | **Architekturverbesserung verifiziert** durch Dispatcher-Unit-Tests. |
| CUDA-Phasen | Nicht getrennt | Profil-Schnittstelle für OS-CSPRNG, Systemmix, CUDA-Abschnitt und CPU-PBKDF2 vorhanden | **CUDA-Hardwareausführung nicht verifiziert.** |
| RTX 4070 SUPER | Nutzerbeobachtung ca. 70 s | Nicht messbar | **NOT VERIFIED.** Keine Behauptung über Verbesserung oder Ursache auf der Ziel-GPU. |
| ARM64-Smartphone | Nutzerbeobachtung ca. 4,5 s | Nicht messbar | **NOT VERIFIED.** CPU-/ARM64-Fallback ist durch Architektur und Tests abgedeckt, aber nicht auf einem Gerät gemessen. |

## CUDA-Entscheidung

Die aktuelle CUDA-Implementierung hat keine echte GPU-PBKDF2 implementiert. Ein nicht auditierter GPU-Zufallsweg darf wegen der Passwortsicherheit nicht als Primärentropie verwendet werden. Daher wird CUDA gegenwärtig nicht als sicheres Passwortbackend freigeschaltet. Der Dispatcher meldet transparent den CPU-Fallback, bis auf realer NVIDIA-Hardware ein auditierter sicherer CUDA-Pfad sowie ein positiver End-to-End-Benchmark nachgewiesen sind.

Das ist kein pauschales Entfernen von CUDA: Die Diagnose- und Dispatcherstruktur bleibt vorbereitet. Sobald ein sicherer, geprüfter GPU-Workload vorhanden ist, misst der Dispatcher die reale GPU-/CPU-Latenz und setzt CUDA nur bei mindestens 10 % End-to-End-Gewinn für große Batches ein.

## Reproduzieren

```bash
for profile in single small medium large; do
  python benchmark/run_profiles.py --profile "$profile" --backend cpu \
    --warmups 1 --repeats 5 --memory --json
done
```

Für NVIDIA-Hardware:

```bash
nvidia-smi
python benchmark/run_profiles.py --profile large --backend auto --warmups 1 --repeats 7 --memory
python pw.py -log
```

Die resultierenden `-log`-Dateien enthalten nur Backend- und Phasenmetadaten, niemals Passwörter, Seeds oder Hashwerte.
