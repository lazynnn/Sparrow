#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
"$SCRIPT_DIR/tailwindcss" \
  --input "$SCRIPT_DIR/sparrow/web/static/css/input.css" \
  --output "$SCRIPT_DIR/sparrow/web/static/dist/output.css" \
  "$@"
