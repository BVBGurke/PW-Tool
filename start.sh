#!/usr/bin/env sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
COMPONENT=${1:-stack}
HOST=127.0.0.1
run_python() {
  if [ -n "${PWTOOL_PYTHON_LD_PRELOAD:-}" ]; then
    LD_PRELOAD="$PWTOOL_PYTHON_LD_PRELOAD" "$@"
  else
    "$@"
  fi
}
if [ "${PWTOOL_BIND:-local}" = "lan" ] && [ "$COMPONENT" != "backend" ]; then
  printf '%s\n' 'LAN-Modus startet nur das lokale Backend für einen TLS-Reverse-Proxy. Nutze: PWTOOL_BIND=lan ./start.sh backend' >&2
  exit 2
fi
if [ ! -x "$ROOT/.venv/bin/python" ]; then printf '%s\n' 'Bitte zuerst ./setup.sh ausführen.' >&2; exit 1; fi
if [ ! -f "$ROOT/.pwtool.local.json" ]; then printf '%s\n' 'Lokale Konfiguration fehlt. Bitte ./setup.sh ausführen.' >&2; exit 1; fi
PWTOOL_CONFIG="$ROOT/.pwtool.local.json" PYTHONPATH="$ROOT/backend" run_python "$ROOT/.venv/bin/python" "$ROOT/scripts/validate_runtime.py" --config "$ROOT/.pwtool.local.json" --bind "${PWTOOL_BIND:-local}"

backend() {
  if [ -n "${PWTOOL_PYTHON_LD_PRELOAD:-}" ]; then
    PWTOOL_CONFIG="$ROOT/.pwtool.local.json" PYTHONPATH="$ROOT/backend" LD_PRELOAD="$PWTOOL_PYTHON_LD_PRELOAD" exec "$ROOT/.venv/bin/python" -m uvicorn main:app --app-dir "$ROOT/backend" --host "$HOST" --port 8000
  else
    PWTOOL_CONFIG="$ROOT/.pwtool.local.json" PYTHONPATH="$ROOT/backend" exec "$ROOT/.venv/bin/python" -m uvicorn main:app --app-dir "$ROOT/backend" --host "$HOST" --port 8000
  fi
}
frontend() { exec pnpm --dir "$ROOT/frontend" dev; }
case "$COMPONENT" in
  backend) backend ;;
  frontend) frontend ;;
  stack) backend & BACKEND_PID=$!; trap 'kill "$BACKEND_PID" 2>/dev/null || true' EXIT INT TERM; frontend ;;
  *) printf '%s\n' 'Nutzung: ./start.sh [backend|frontend|stack]' >&2; exit 2 ;;
esac
