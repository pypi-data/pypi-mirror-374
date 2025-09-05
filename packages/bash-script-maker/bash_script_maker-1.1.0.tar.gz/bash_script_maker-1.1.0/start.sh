
#!/bin/bash
# Startscript für Bash-Script-Maker

echo "Starte Bash-Script-Maker..."

# Überprüfe, ob Python installiert ist
if ! command -v python3 &> /dev/null; then
    echo "Fehler: Python 3 ist nicht installiert!"
    exit 1
fi

# Überprüfe, ob Tkinter verfügbar ist
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Fehler: Tkinter ist nicht verfügbar!"
    echo "Installieren Sie python3-tk:"
    echo "  Ubuntu/Debian: sudo apt install python3-tk"
    echo "  Fedora: sudo dnf install python3-tkinter"
    echo "  Arch Linux: sudo pacman -S tk"
    exit 1
fi

# Überprüfe, ob Zenity verfügbar ist
if ! command -v zenity &> /dev/null; then
    echo "Warnung: Zenity ist nicht installiert!"
    echo "Zenity-Dialoge werden in Ihren Scripts nicht funktionieren."
    echo "Installieren Sie zenity:"
    echo "  Ubuntu/Debian: sudo apt install zenity"
    echo "  Fedora: sudo dnf install zenity"
    echo "  Arch Linux: sudo pacman -S zenity"
    echo ""
    echo "Drücken Sie Enter, um trotzdem fortzufahren..."
    read
fi

# Starte das Programm (bevorzugt in venv, falls vorhanden)
cd "$(dirname "$0")"

if [ -f ".venv_path" ]; then
    VENV_DIR=$(cat .venv_path)
elif [ -d ".venv" ]; then
    VENV_DIR=".venv"
fi

if [ -n "$VENV_DIR" ] && [ -x "$VENV_DIR/bin/python" ]; then
    "$VENV_DIR/bin/python" bash_script_maker.py
else
    python3 bash_script_maker.py
fi
