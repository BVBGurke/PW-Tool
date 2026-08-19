# PW-Tool

PW-Tool ist eine **lokale Python-CLI** zur Passworterzeugung mit einer vollständigen **Textual-TUI**. Das Projekt erzeugt Passwörter ohne Konto, Cloud, Telemetrie oder Netzwerkzugriff. Es enthält keine APK und keine native Mobile-App; Android wird über geeignete Python-Terminals wie Termux mit dem sicheren CPU-/ARM64-Pfad unterstützt.

> **Grundsatz:** Für die sichtbare Passworterzeugung gibt es einen klaren Weg: OS-CSPRNG, bias-freie Zeichenauswahl, garantierte Zeichenklassen und ein CSPRNG-basierter Shuffle. Es gibt keinen zufälligen Wechsel zwischen Sicherheitsalgorithmen.

## Installation und Start

PW-Tool benötigt Python 3.10 oder neuer und nutzt Textual für die Terminaloberfläche.

```bash
# Aus dem geklonten Arbeitsbaum
python -m pip install -r requirements.txt
python pw.py

# Oder als Paket
python -m pip install .
pw-tool
```

In Termux wird derselbe lokale CPU-Pfad verwendet:

```bash
pkg install python git
git clone https://github.com/BVBGurke/PW-Tool.git
cd PW-Tool
python -m pip install -r requirements.txt
python pw.py
```

## Vereinfachte Textual-TUI

Die TUI erfasst drei nicht sensible Werte einmal pro Sitzung. Jede weitere Erzeugung nutzt diese Werte erneut, erzeugt aber neue lokale Zufallswerte.

| Einstellung | Standard | Verhalten |
|---|---:|---|
| Passwortlänge | 64 | Erlaubt nur 16 bis 256 Zeichen. |
| Anzahl | 1 | Erlaubt 1 bis 10.000 Werte pro Batch. |
| Zeichenauswahl | Vollständig | Vollständig garantiert Klein-/Großbuchstaben, Ziffern und Sonderzeichen. Kompatibel garantiert Klein-/Großbuchstaben und Ziffern. |

Lange Passwörter bleiben vollständig sichtbar und werden nicht mit Ellipsen gekürzt. Unter 72 Terminalspalten wird das Formular vertikal, großflächig und scrollbar dargestellt.

| Tastenkürzel | Funktion |
|---|---|
| `Strg+G` | Neue Passwörter mit der aktuellen Sitzungsauswahl erzeugen. |
| `Strg+C` | Letzte Ergebnisse kopieren, sofern die Zwischenablage verfügbar ist. |
| `Strg+S` | Lokalen Sicherheitscheck des letzten Batches anzeigen. |
| `Strg+H` | Lokale Hash-Demo starten. |
| `Strg+L` | Sichtbare Ergebnisse und den lokalen UI-Zustand löschen. |
| `Strg+Q` | Anwendung beenden. |

## Direkter Passwortpfad

Das sichtbare Passwortprofil nutzt den Betriebssystem-Zufallsgenerator über Python. Für jede Zeichenklasse wird mindestens ein Zeichen gezogen; die restlichen Positionen werden aus der gewählten Zeichenmenge gewählt. Rejection Sampling vermeidet Modulo-Bias, anschließend mischt ein CSPRNG-basierter Fisher-Yates-Algorithmus die Positionen.

| Auswahl | Garantierte Klassen | Zweck |
|---|---|---|
| **Vollständig** | Kleinbuchstabe, Großbuchstabe, Ziffer, Sonderzeichen | Standard für Dienste, die Sonderzeichen akzeptieren. |
| **Kompatibel** | Kleinbuchstabe, Großbuchstabe, Ziffer | Für restriktive Eingabefelder ohne Sonderzeichen. |

Der Sicherheitscheck zeigt ausschließlich nicht sensitive Metadaten: Auswahl, Batchgröße, kürzeste Länge, Zeichenvorrat, konservative Entropieuntergrenze, Zeichenklassen und Duplikate. Er zeigt, schreibt und überträgt keine Passwortwerte.

## Hash-Demo: lokale Selbstprüfung, kein Crack-Tool

Die Schaltfläche **Hash-Demo** ist eine begrenzte Lehr- und Prüfungsfunktion. Sie akzeptiert keine fremden Hashes, Passwörter, Wortlisten oder Angriffsstrategien. Stattdessen erzeugt sie im Prozess einen frischen, nicht angezeigten Demo-Wert und verarbeitet ihn lokal:

1. Ein frischer Demo-Wert entsteht über die aktuelle CSPRNG-Policy.
2. Ein neuer 16-Byte-Salt kommt vom OS-CSPRNG.
3. `hashlib.scrypt` leitet mit fest begrenzten Parametern einen 32-Byte-Wert ab.
4. Eine einzige Selbstverifikation vergleicht nur diesen Demo-Wert konstantzeitnah mit dem selbst erzeugten Ergebnis.

Die Oberfläche zeigt nur Algorithmus, öffentliche Kostenparameter, Salt-/Ausgabelänge, Laufzeit und den Selbstprüfstatus. Klartext, Salt und abgeleitete Bytes werden nicht angezeigt, nicht gespeichert, nicht kopiert und nicht geloggt.

> Ein Passwort-Hash ist keine reversible Verschlüsselung und macht ein Login-Passwort nicht automatisch stärker. Der Zweck einer langsamen, gesalzenen KDF ist die sichere Speicherung in einer Anwendung. PW-Tool ersetzt keine Passwortdatenbank oder Authentisierungsarchitektur.

## CPU, CUDA und Android

Die interaktive Passworterzeugung und die lokale scrypt-Demo laufen bewusst auf der CPU. Android/Termux nutzt dadurch denselben transparenten CPU-/ARM64-Fallback wie andere Plattformen.

| Situation | Verhalten |
|---|---|
| Linux, macOS oder Windows | Direkte lokale OS-CSPRNG-Policy auf der CPU. |
| Android / Termux / ARM64 | Direkte lokale OS-CSPRNG-Policy auf der CPU. |
| CUDA erkannt | Nur als Statusinformation. Passwortmaterial und die scrypt-Demo werden nicht an CUDA übergeben. |
| Keine auditiert sichere CUDA-KDF | CPU bleibt aktiv; es wird keine GPU-Beschleunigung behauptet. |

Eine allgemeine Crack-Funktion ist absichtlich nicht Teil des Projekts. Das Tool verarbeitet keine Zielsysteme, fremden Hashes oder Kandidatenlisten.

## Diagnoselog: nur mit `-log`

Ohne Argument entstehen keine Diagnosedateien. Erst `-log` oder `--log` aktiviert lokale JSONL-Metadaten.

```bash
python pw.py -log
python pw.py -log --log-directory ./diagnostics
```

Die Whitelist erlaubt nur nicht sensitive Diagnosewerte wie Laufzeit, Plattform und Backendstatus. Passwörter, Salts, Hashes, Digests, Seeds, Entropie, Dateipfade und Quellinhalte werden verworfen.

## GitHub Pages

Die statische Projektwebsite liegt in [`docs/`](docs/). Um sie über GitHub Pages zu veröffentlichen, wähle im Repository **Settings → Pages → Deploy from a branch → `main` → `/docs`**. GitHub zeigt anschließend die tatsächliche Projekt-URL an.

Die Seite dokumentiert die lokale CSPRNG-Policy, den Android-/Termux-Fallback und die bewusst begrenzte Hash-Demo. Sie bewirbt keine Crack-Funktion.

## Prüfen

```bash
# Syntax
python -m py_compile *.py backends/*.py benchmark/*.py tests/*.py

# Tests
python -m unittest discover -v

# Zusätzliche Generatorprüfungen
python quick_verify.py
python verify_entropy.py

# Installierbares Wheel
python -m pip wheel --no-deps --no-build-isolation .
```

## Projektstruktur

```text
pw.py                    CLI-Einstieg, Textual-Start und -log-Option
textual_ui.py            Responsive Textual-TUI mit Worker-basierter Erzeugung
password_engine.py       Direkte CSPRNG-Policy, Rejection Sampling und Shuffle
hash_demo.py             Begrenzte lokale scrypt-Demo ohne Fremdhash-Eingaben
security_check.py        Passwortwertfreie lokale Sicherheitsbewertung
dispatcher.py            Einheitlicher CPU-/OS-CSPRNG-Entscheidungspfad
backends/                CPU-Backend und optionale CUDA-Statuskomponenten
diagnostics.py           Whitelist-basierter, secret-freier Opt-in-Logger
docs/                    Statische, GitHub-Pages-fähige Projektwebsite
tests/                   Unit- und Textual-Regressionstests
```

## Sicherheits- und Testgrenzen

Die aktuelle Umgebung hatte keine CUDA-Hardware und keine Android-ARM64-Instanz. Deshalb werden keine GPU-, Android- oder Energieversprechen behauptet. Die CPU-/ARM64-Fallbacklogik sowie das Verhalten bei fehlendem CUDA sind durch Unit-Tests abgedeckt; reale Zielhardware sollte zusätzlich lokal geprüft werden.

PW-Tool kann nicht vor kompromittierten Geräten, Bildschirmmitschnitt, unsicherer Zwischenablage, Phishing oder Passwortwiederverwendung schützen. Verwende für jeden Dienst einen neu erzeugten Wert und lösche sichtbare Ergebnisse nach dem Übertragen.

## Quellen

[1] [Python documentation: `secrets`](https://docs.python.org/3/library/secrets.html)

[2] [Python documentation: `os.urandom`](https://docs.python.org/3/library/os.html#os.urandom)

[3] [Python documentation: `hashlib.scrypt`](https://docs.python.org/3/library/hashlib.html#hashlib.scrypt)

[4] [Textual – Python framework for terminal user interfaces](https://textual.textualize.io/)
