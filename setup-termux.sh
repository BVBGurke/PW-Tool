#!/data/data/com.termux/files/usr/bin/sh
set -eu

if ! command -v python >/dev/null 2>&1; then
  pkg install -y python
fi

if ! command -v node >/dev/null 2>&1; then
  pkg install -y nodejs-lts || pkg install -y nodejs
fi

if ! command -v npm >/dev/null 2>&1; then
  printf '%s\n' 'Node.js wurde ohne npm gefunden. Installiere in Termux nodejs-lts oder nodejs erneut.' >&2
  exit 1
fi

if ! command -v pnpm >/dev/null 2>&1; then
  printf '%s\n' 'pnpm wird über npm installiert; ein Termux-pnpm-Paket wird nicht vorausgesetzt.'
  npm install --global pnpm@11
fi

pnpm --version
exec "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)/setup.sh"
