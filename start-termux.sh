#!/data/data/com.termux/files/usr/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if [ "${1:-backend}" = "frontend" ]; then exec "$ROOT/start.sh" frontend; fi
exec "$ROOT/start.sh" backend
