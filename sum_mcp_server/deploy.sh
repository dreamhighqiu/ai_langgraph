#!/usr/bin/env bash
set -euo pipefail

ACTION="${1:-start}"
shift || true

AUTO_PORT=0
KILL_PORT=0
OUT_DIR="dist/sum_mcp_bundle"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --auto-port) AUTO_PORT=1; shift ;;
    --kill-port) KILL_PORT=1; shift ;;
    --out-dir) OUT_DIR="${2:-${OUT_DIR}}"; shift 2 ;;
    *) break ;;
  esac
done

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CTL="${ROOT}/sum_mcp_server/mcpctl.py"
VENDORIZE="${ROOT}/sum_mcp_server/vendorize.sh"
BUNDLE="${ROOT}/sum_mcp_server/build_bundle.sh"

PY="${ROOT}/.venv/bin/python"
if [[ -x "${ROOT}/.venv/Scripts/python.exe" ]]; then
  PY="${ROOT}/.venv/Scripts/python.exe"
elif [[ -x "${ROOT}/.venv/bin/python" ]]; then
  PY="${ROOT}/.venv/bin/python"
else
  PY="python"
fi

cd "${ROOT}"

EXTRA=()
if [[ "${AUTO_PORT}" == "1" ]]; then EXTRA+=("--auto-port"); fi
if [[ "${KILL_PORT}" == "1" ]]; then EXTRA+=("--kill-port"); fi

case "${ACTION}" in
  list)     "${PY}" "${CTL}" list ;;
  status)   "${PY}" "${CTL}" status ;;
  doctor)   "${PY}" "${CTL}" doctor ;;
  stop)     "${PY}" "${CTL}" stop --all ;;
  start)    "${PY}" "${CTL}" start --all "${EXTRA[@]}" ;;
  restart)  "${PY}" "${CTL}" restart --all "${EXTRA[@]}" ;;
  vendorize) bash "${VENDORIZE}" ;;
  bundle)   bash "${BUNDLE}" "${OUT_DIR}" ;;
  *) echo "Usage: $0 {start|stop|restart|status|list|doctor|vendorize|bundle} [--auto-port] [--kill-port] [--out-dir <path>]" >&2; exit 2 ;;
esac
