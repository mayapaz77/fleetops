#!/usr/bin/env bash
set -euo pipefail

SERVER_NAME="${1:-server1}"
MULTIPASS="$(command -v multipass.exe)"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG="$PROJECT_DIR/infrastructure/${SERVER_NAME}.yaml"

if [[ ! -f "$CONFIG" ]]; then
    echo "Error: Configuration file not found: $CONFIG" >&2
    exit 1
fi

CONFIG_WIN="$(wslpath -w "$CONFIG")"

"$MULTIPASS" version

if "$MULTIPASS" list --format csv | cut -d, -f1 | grep -Fxq "$SERVER_NAME"; then
    echo "$SERVER_NAME already exists. Skipping creation."
    exit 0
fi

"$MULTIPASS" launch 24.04 \
  --name "$SERVER_NAME" \
  --cpus 2 \
  --memory 2G \
  --disk 10G \
  --cloud-init "$CONFIG_WIN"
