#!/usr/bin/env sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
COMPONENT=${1:-stack}
HOST=127.0.0.1
if [ "${PWTOOL_BIND:-local}" = "lan" ]; then HOST=0.0.0.0; fi
if [ ! -x "$ROOT/.venv/bin/python" ]; then printf '%s\n' 'Bitte zuerst ./setup.sh ausführen.' >&2; exit 1; fi
if [ ! -f "$ROOT/.pwtool.local.json" ]; then printf '%s\n' 'Lokale Konfiguration fehlt. Bitte ./setup.sh ausführen.' >&2; exit 1; fi
PWTOOL_CONFIG="$ROOT/.pwtool.local.json" PYTHONPATH="$ROOT/backend" "$ROOT/.venv/bin/python" "$ROOT/scripts/validate_runtime.py" --config "$ROOT/.pwtool.local.json" --bind "${PWTOOL_BIND:-local}"

backend() { PWTOOL_CONFIG="$ROOT/.pwtool.local.json" PYTHONPATH="$ROOT/backend" exec "$ROOT/.venv/bin/python" -m uvicorn main:app --app-dir "$ROOT/backend" --host "$HOST" --port 8000; }
frontend() { exec pnpm --dir "$ROOT/frontend" dev; }
case "$COMPONENT" in
  backend) backend ;;
  frontend) frontend ;;
  stack) backend & BACKEND_PID=$!; trap 'kill "$BACKEND_PID" 2>/dev/null || true' EXIT INT TERM; frontend ;;
  *) printf '%s\n' 'Nutzung: ./start.sh [backend|frontend|stack]' >&2; exit 2 ;;
esac
