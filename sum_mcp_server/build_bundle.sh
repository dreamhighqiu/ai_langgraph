#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${1:-dist/sum_mcp_bundle}"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${ROOT}/${OUT_DIR}"

rm -rf "${TARGET}"
mkdir -p "${TARGET}"

echo "[1/3] Copy sum_mcp_server -> ${OUT_DIR}"
cp -R "${ROOT}/sum_mcp_server" "${TARGET}/sum_mcp_server"

echo "[2/3] Vendorize deps into bundle"
chmod +x "${TARGET}/sum_mcp_server/vendorize.sh"
"${TARGET}/sum_mcp_server/vendorize.sh"

echo "[3/3] Done"
echo "Bundle ready: ${TARGET}"
echo "Run:"
echo "  cd ${TARGET}"
echo "  python sum_mcp_server/mcpctl.py start --all"

