#!/usr/bin/env sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PYTHON=${PYTHON:-python3}

if ! command -v pnpm >/dev/null 2>&1; then
  printf '%s\n' 'pnpm fehlt. In Termux zuerst ./setup-termux.sh verwenden; auf anderen Systemen pnpm 11 installieren.' >&2
  exit 1
fi

if [ "${PWTOOL_USE_SYSTEM_SITE_PACKAGES:-0}" = "1" ]; then
  "$PYTHON" -m venv --system-site-packages "$ROOT/.venv"
else
  "$PYTHON" -m venv "$ROOT/.venv"
fi
"$ROOT/.venv/bin/python" -m pip install --upgrade pip

if [ "${PWTOOL_USE_SYSTEM_SITE_PACKAGES:-0}" = "1" ]; then
  REQUIREMENTS=$(mktemp)
  trap 'rm -f "$REQUIREMENTS"' EXIT
  sed '/^cryptography[<>=!~]/d' "$ROOT/backend/requirements.txt" > "$REQUIREMENTS"
  "$ROOT/.venv/bin/python" -m pip install -r "$REQUIREMENTS"
else
  "$ROOT/.venv/bin/python" -m pip install -r "$ROOT/backend/requirements.txt"
fi

pnpm --dir "$ROOT/frontend" install
pnpm --dir "$ROOT/website" install
"$ROOT/.venv/bin/python" "$ROOT/scripts/init_config.py" --path "$ROOT/.pwtool.local.json"
printf '%s\n' 'Einrichtung abgeschlossen. Starte lokal mit ./start.sh'
