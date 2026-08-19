#!/data/data/com.termux/files/usr/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
. "$ROOT/scripts/termux_python_runtime.sh"
pwtool_configure_termux_python || exit 1
exec "$ROOT/start.sh" "${1:-stack}"
