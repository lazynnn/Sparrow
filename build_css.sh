#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TW_BIN="$SCRIPT_DIR/tailwindcss"

if [ ! -f "$TW_BIN" ]; then
    echo "tailwindcss binary not found, downloading..."
    OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
    ARCH="$(uname -m)"
    case "$ARCH" in
        x86_64) ARCH="x64" ;;
        aarch64) ARCH="arm64" ;;
        armv7l) ARCH="armv7" ;;
    esac
    TW_VERSION="v4.3.1"
    URL="https://github.com/tailwindlabs/tailwindcss/releases/download/${TW_VERSION}/tailwindcss-${OS}-${ARCH}"
    echo "Downloading $URL"
    curl -fSL -o "$TW_BIN" "$URL"
    chmod +x "$TW_BIN"
    echo "tailwindcss ${TW_VERSION} downloaded successfully."
fi

"$TW_BIN" \
    --input "$SCRIPT_DIR/sparrow/web/static/css/input.css" \
    --output "$SCRIPT_DIR/sparrow/web/static/dist/output.css" \
    "$@"
