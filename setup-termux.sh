#!/data/data/com.termux/files/usr/bin/sh
set -eu
pkg install -y python nodejs-lts pnpm
exec "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)/setup.sh"
