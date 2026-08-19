#!/data/data/com.termux/files/usr/bin/sh
# Termux/Python 3.14: only preload libpython after a normal AESGCM import fails.

pwtool_configure_termux_python() {
  if python -c 'from cryptography.hazmat.primitives.ciphers.aead import AESGCM' >/dev/null 2>&1; then
    unset PWTOOL_PYTHON_LD_PRELOAD
    return 0
  fi

  preload_path="${PREFIX:-/data/data/com.termux/files/usr}/lib/libpython3.so"
  if [ ! -r "$preload_path" ]; then
    printf '%s\n' "Termux-Python kann AESGCM nicht importieren und die benötigte Bibliothek fehlt: $preload_path" >&2
    return 1
  fi

  if ! LD_PRELOAD="$preload_path" python -c 'from cryptography.hazmat.primitives.ciphers.aead import AESGCM' >/dev/null 2>&1; then
    printf '%s\n' 'Termux-Python kann AESGCM auch mit dem gezielten libpython-Preload nicht importieren. Führe pkg update && pkg upgrade aus und installiere python python-cryptography erneut.' >&2
    return 1
  fi

  PWTOOL_PYTHON_LD_PRELOAD="$preload_path"
  export PWTOOL_PYTHON_LD_PRELOAD
  printf '%s\n' 'Termux-Python verwendet für AESGCM den geprüften libpython-Preload-Fallback.'
}
