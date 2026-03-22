#!/bin/bash

# 1. Absoluten Pfad zum Skript-Ordner ermitteln
SCRIPT_DIR=$(dirname "$(realpath "$0")")

# 2. In das Verzeichnis wechseln (damit relative Pfade in .env oder Python passen)
cd "$SCRIPT_DIR"

# 3. .env Variablen laden (falls vorhanden)
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# 4. Virtuelle Umgebung aktivieren und Python-Skript ausführen
# Wir nutzen den direkten Pfad zum Python-Interpreter im venv, das spart den 'source' Call
./venv/bin/python3 kicktipp.py --use-login-token "$KICKTIPP_TOKEN"

