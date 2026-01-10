#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENDOR="${ROOT}/sum_mcp_server/vendor"

sync_dir() {
  local src="$1"
  local dst="$2"
  if [[ ! -d "${src}" ]]; then
    echo "Missing source dir: ${src}" >&2
    exit 1
  fi
  rm -rf "${dst}"
  mkdir -p "$(dirname "${dst}")"
  cp -R "${src}" "${dst}"
}

echo "[1/4] Sync lightrag -> sum_mcp_server/vendor/lightrag"
sync_dir "${ROOT}/anything-chat-rag/lightrag" "${VENDOR}/lightrag"

echo "[2/4] Sync raganything -> sum_mcp_server/vendor/raganything"
sync_dir "${ROOT}/anything-chat-rag/raganything" "${VENDOR}/raganything"

echo "[3/4] Sync mcp_server_rag_anything -> sum_mcp_server/vendor/mcp_server_rag_anything"
sync_dir "${ROOT}/mcp-server/src/mcp_server_rag_anything" "${VENDOR}/mcp_server_rag_anything"

echo "[4/4] Sync automation-quality-mcp -> sum_mcp_server/vendor/automation-quality-mcp"
AQ_SRC="${ROOT}/testing-agents-service/src/api_agent/mcp_servers/automation-quality-mcp"
AQ_DST="${VENDOR}/automation-quality-mcp"
rm -rf "${AQ_DST}"
mkdir -p "${AQ_DST}"
cp -R "${AQ_SRC}/src" "${AQ_DST}/src"
cp -f "${AQ_SRC}/mcpServer.js" "${AQ_SRC}/run-server.js" "${AQ_SRC}/cli.js" "${AQ_SRC}/browserControl.js" \
  "${AQ_SRC}/package.json" "${AQ_SRC}/package-lock.json" "${AQ_SRC}/README.md" "${AQ_DST}/"

echo "[OK] vendor sync complete: ${VENDOR}"

