# Termux-Befund: Python 3.14 und cryptography

Der auf dem Gerät gemeldete Fehler `dlopen failed: cannot locate symbol "PyLong_Type"` stammt aus der per `pip` in der Virtualenv installierten `cryptography`-Rust-Bindung. Die Termux-Projektberichte dokumentieren denselben Fehler unter Python 3.14.

Die aktuelle Empfehlung im Termux-Tracker lautet, `cryptography` aus dem Paket `python-cryptography` zu beziehen, nicht aus einem pip-Android-Wheel. Ein älterer Trackerfall nennt `LD_PRELOAD=$PREFIX/lib/libpython3.so` lediglich als Übergangs-Workaround; der Termux-Paketfix linkt die Systembibliothek stattdessen gegen `libpython`. Der Projektfix sollte deshalb keine globale Preload-Variable erzwingen, sondern zuerst das Termux-Systempaket installieren und die Virtualenv ohne pip-`cryptography` verwenden.

## Quellen

- Termux, [Issue #30705](https://github.com/termux/termux-packages/issues/30705): `python-cryptography` statt pip-Installation.
- Termux, [Issue #30187](https://github.com/termux/termux-packages/issues/30187): Python-3.14-Symbolfehler, Zwischen-Workaround und Paketfix.
