#!/usr/bin/env bash
set -euo pipefail

ACTION="${1:-start}"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CTL="${ROOT}/sum_mcp_server/mcpctl.py"

PY="${ROOT}/.venv/bin/python"
if [[ -x "${ROOT}/.venv/Scripts/python.exe" ]]; then
  PY="${ROOT}/.venv/Scripts/python.exe"
elif [[ -x "${ROOT}/.venv/bin/python" ]]; then
  PY="${ROOT}/.venv/bin/python"
else
  PY="python"
fi

cd "${ROOT}"

case "${ACTION}" in
  list)   "${PY}" "${CTL}" list ;;
  status) "${PY}" "${CTL}" status ;;
  stop)   "${PY}" "${CTL}" stop --all ;;
  start)  "${PY}" "${CTL}" start --all ;;
  *) echo "Usage: $0 {start|stop|status|list}" >&2; exit 2 ;;
esac

