#!/usr/bin/env sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PYTHON=${PYTHON:-python3}

"$PYTHON" -m venv "$ROOT/.venv"
"$ROOT/.venv/bin/python" -m pip install --upgrade pip
"$ROOT/.venv/bin/python" -m pip install -r "$ROOT/backend/requirements.txt"
pnpm --dir "$ROOT/frontend" install
pnpm --dir "$ROOT/website" install
"$ROOT/.venv/bin/python" "$ROOT/scripts/init_config.py" --path "$ROOT/.pwtool.local.json"
printf '%s\n' 'Einrichtung abgeschlossen. Starte lokal mit ./start.sh'
