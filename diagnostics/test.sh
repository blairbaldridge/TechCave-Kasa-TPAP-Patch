#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
if [[ $# -ne 1 ]]; then
  echo "Usage: bash test.sh SWITCH_IP" >&2
  exit 2
fi
exec .venv/bin/python test_ks205.py --host "$1"
