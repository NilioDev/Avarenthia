#!/usr/bin/env bash
# Builds dist/Umbrathyn - a single file you can run without Python (macOS / Linux).
set -euo pipefail
cd "$(dirname "$0")"
python3 -m venv .build-venv
source .build-venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt pyinstaller
pyinstaller --noconfirm --clean --onefile --windowed --name Umbrathyn --add-data "assets:assets" main.py
echo
echo "Klaar: dist/Umbrathyn"
