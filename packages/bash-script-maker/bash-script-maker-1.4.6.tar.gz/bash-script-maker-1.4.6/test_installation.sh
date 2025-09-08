
#!/bin/bash
# Test-Script für Bash-Script-Maker Installation
# Überprüft alle erforderlichen Abhängigkeiten

echo "=== Bash-Script-Maker - Installationstest ==="
echo ""

# Farbcodes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[TEST]${NC} $1"; }
print_success() { echo -e "${GREEN}[PASS]${NC} $1"; }
print_error() { echo -e "${RED}[FAIL]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }

PASSED=0
FAILED=0
WARNINGS=0

# Test 1: Python 3
print_status "Teste Python 3..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | head -n1 | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 6 ]; then
        print_success "Python $PYTHON_VERSION gefunden (erfüllt Anforderungen)"
        ((PASSED++))
    else
        print_error "Python $PYTHON_VERSION gefunden (erfordert 3.6+)"
        ((FAILED++))
    fi
else
    print_error "Python 3 nicht gefunden"
    ((FAILED++))
fi

# Test 2: Tkinter
print_status "Teste Tkinter..."
if python3 -c "import tkinter; root = tkinter.Tk(); root.destroy()" 2>/dev/null; then
    print_success "Tkinter funktioniert korrekt"
    ((PASSED++))
else
    print_error "Tkinter funktioniert nicht oder ist nicht installiert"
    ((FAILED++))
fi

# Test 3: Zenity
print_status "Teste Zenity..."
if command -v zenity &> /dev/null; then
    ZENITY_VERSION=$(zenity --version 2>&1 | head -n1)
    print_success "Zenity gefunden: $ZENITY_VERSION"
    ((PASSED++))
else
    print_error "Zenity nicht gefunden"
    ((FAILED++))
fi

# Test 4: pip
print_status "Teste pip..."
if python3 -m pip --version &> /dev/null; then
    PIP_VERSION=$(python3 -m pip --version 2>&1 | head -n1)
    print_success "pip verfügbar: $PIP_VERSION"
    ((PASSED++))
else
    print_error "pip nicht verfügbar"
    ((FAILED++))
fi

# Test 5: X11/Terminal
print_status "Teste Terminal-Emulator..."
if command -v xterm &> /dev/null || command -v gnome-terminal &> /dev/null || command -v konsole &> /dev/null; then
    print_success "Terminal-Emulator gefunden"
    ((PASSED++))
else
    print_warning "Kein Terminal-Emulator gefunden (kann zu Problemen führen)"
    ((WARNINGS++))
fi

# Test 6: DISPLAY Variable (für GUI)
print_status "Teste DISPLAY-Variable..."
if [ -n "$DISPLAY" ]; then
    print_success "DISPLAY ist gesetzt: $DISPLAY"
    ((PASSED++))
else
    print_warning "DISPLAY ist nicht gesetzt (GUI könnte nicht funktionieren)"
    ((WARNINGS++))
fi

# Test 7: Import-Test der Python-Module
print_status "Teste Python-Module..."
if python3 -c "
try:
    import tkinter
    import os
    import sys
    import subprocess
    import re
    print('Alle erforderlichen Module verfügbar')
except ImportError as e:
    print(f'Fehlendes Modul: {e}')
    sys.exit(1)
" 2>/dev/null; then
    print_success "Alle erforderlichen Python-Module verfügbar"
    ((PASSED++))
else
    print_error "Ein oder mehrere Python-Module fehlen"
    ((FAILED++))
fi

# Test 8: Bash-Script-Maker Dateien
print_status "Teste Bash-Script-Maker Dateien..."
MISSING_FILES=()
if [ ! -f "bash_script_maker.py" ]; then MISSING_FILES+=("bash_script_maker.py"); fi
if [ ! -f "syntax_highlighter.py" ]; then MISSING_FILES+=("syntax_highlighter.py"); fi
if [ ! -f "README.md" ]; then MISSING_FILES+=("README.md"); fi

if [ ${#MISSING_FILES[@]} -eq 0 ]; then
    print_success "Alle erforderlichen Dateien vorhanden"
    ((PASSED++))
else
    print_error "Fehlende Dateien: ${MISSING_FILES[*]}"
    ((FAILED++))
fi

echo ""
echo "=== TESTERGEBNIS ==="
echo "Bestanden: $PASSED"
echo "Fehlgeschlagen: $FAILED"
echo "Warnungen: $WARNINGS"

if [ $FAILED -eq 0 ]; then
    echo ""
    if [ $WARNINGS -eq 0 ]; then
        print_success "Alle Tests bestanden! Installation ist vollständig."
    else
        print_warning "Alle kritischen Tests bestanden, aber es gibt Warnungen."
    fi
    echo ""
    print_status "Sie können Bash-Script-Maker jetzt starten:"
    echo "  ./start.sh"
    echo "  oder"
    echo "  python3 bash_script_maker.py"
    exit 0
else
    echo ""
    print_error "Einige kritische Tests sind fehlgeschlagen."
    echo ""
    print_status "Lösungsmöglichkeiten:"
    echo "1. Führen Sie das Installationsscript erneut aus: ./install.sh"
    echo "2. Installieren Sie fehlende Pakete manuell (siehe packages.txt)"
    echo "3. Überprüfen Sie Ihre Python-Installation"
    exit 1
fi
