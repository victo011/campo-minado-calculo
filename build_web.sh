#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
if [[ -x "$ROOT_DIR/.tools/node/bin/node" ]]; then
  NODE_BIN_DIR="$ROOT_DIR/.tools/node/bin"
elif command -v node >/dev/null 2>&1 && command -v npm >/dev/null 2>&1; then
  NODE_BIN_DIR="$(dirname -- "$(command -v node)")"
else
  echo "Instale Node.js 24 LTS e npm ou restaure .tools/node/ neste projeto." >&2
  exit 1
fi
export PATH="$NODE_BIN_DIR:$ROOT_DIR/node_modules/.bin:$PATH"
exec "$NODE_BIN_DIR/npm" run build
