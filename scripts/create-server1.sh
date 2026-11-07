#!/usr/bin/env bash
set -euo pipefail

MULTIPASS="$(command -v multipass.exe)"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG="$PROJECT_DIR/infrastructure/server1.yaml"
CONFIG_WIN="$(wslpath -w "$CONFIG")"

"$MULTIPASS" version

if "$MULTIPASS" list --format csv | cut -d, -f1 | grep -Fxq "server1"; then
    echo "server1 already exists. Skipping creation."
    exit 0
fi

"$MULTIPASS" launch 24.04 \
  --name server1 \
  --cpus 2 \
  --memory 2G \
  --disk 10G \
  --cloud-init "$CONFIG_WIN"
