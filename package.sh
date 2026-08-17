#!/bin/bash

echo "Starting the Pac-Man game packaging..."

# Install PyInstaller if it is not already installed
uv pip install pyinstaller

# Package the game
uv run python -m PyInstaller --onedir \
    --paths "src" \
    --add-data "config.json:." \
    --add-data "instructions.txt:." \
    --add-data "assets:assets" \
    src/pac-man.py

echo "Packaging completed!"
