#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
PIN=844ec73b08f5284626e40aa6f0f73e293502b0b3
python3 -m venv .venv
.venv/bin/python -m pip install "python-kasa @ git+https://github.com/python-kasa/python-kasa.git@$PIN"
