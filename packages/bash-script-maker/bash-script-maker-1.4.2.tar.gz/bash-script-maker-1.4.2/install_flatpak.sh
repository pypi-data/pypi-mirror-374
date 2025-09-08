#!/bin/bash
# Flatpak-Installation für Bash-Script-Maker

echo "=== Bash-Script-Maker - Flatpak Installation ==="
echo "Dieses Script installiert Bash-Script-Maker als Flatpak-Paket."
echo ""

# Farbcodes für bessere Lesbarkeit
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funktion für farbige Ausgabe
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Überprüfe, ob Flatpak installiert ist
if ! command -v flatpak &> /dev/null; then
    print_error "Flatpak ist nicht installiert!"
    print_status "Installieren Sie Flatpak mit:"
    
    if command -v dnf &> /dev/null; then
        print_status "  sudo dnf install flatpak"
    elif command -v apt &> /dev/null; then
        print_status "  sudo apt install flatpak"
    elif command -v pacman &> /dev/null; then
        print_status "  sudo pacman -S flatpak"
    elif command -v zypper &> /dev/null; then
        print_status "  sudo zypper install flatpak"
    else
        print_status "  Installieren Sie Flatpak über Ihren Paketmanager"
    fi
    
    exit 1
fi

# Überprüfe, ob flatpak-builder installiert ist
if ! command -v flatpak-builder &> /dev/null; then
    print_error "flatpak-builder ist nicht installiert!"
    print_status "Installieren Sie flatpak-builder mit:"
    
    if command -v dnf &> /dev/null; then
        print_status "  sudo dnf install flatpak-builder"
    elif command -v apt &> /dev/null; then
        print_status "  sudo apt install flatpak-builder"
    elif command -v pacman &> /dev/null; then
        print_status "  sudo pacman -S flatpak-builder"
    elif command -v zypper &> /dev/null; then
        print_status "  sudo zypper install flatpak-builder"
    else
        print_status "  Installieren Sie flatpak-builder über Ihren Paketmanager"
    fi
    
    exit 1
fi

# Überprüfe, ob Flathub-Repository hinzugefügt ist
if ! flatpak remote-list | grep -q flathub; then
    print_status "Füge Flathub-Repository hinzu..."
    if flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo; then
        print_success "Flathub-Repository hinzugefügt"
    else
        print_error "Fehler beim Hinzufügen des Flathub-Repositories"
        exit 1
    fi
fi

# Installiere Flatpak-Runtime
print_status "Installiere Flatpak-Runtime..."
if ! flatpak list | grep -q "org.freedesktop.Platform.*23.08"; then
    if flatpak install -y flathub org.freedesktop.Platform//23.08; then
        print_success "Flatpak-Runtime installiert"
    else
        print_error "Fehler beim Installieren der Flatpak-Runtime"
        exit 1
    fi
else
    print_success "Flatpak-Runtime bereits installiert"
fi

if ! flatpak list | grep -q "org.freedesktop.Sdk.*23.08"; then
    if flatpak install -y flathub org.freedesktop.Sdk//23.08; then
        print_success "Flatpak-SDK installiert"
    else
        print_error "Fehler beim Installieren des Flatpak-SDK"
        exit 1
    fi
else
    print_success "Flatpak-SDK bereits installiert"
fi

# Erstelle Build-Verzeichnis
print_status "Erstelle Build-Verzeichnis..."
mkdir -p build/flatpak

# Kopiere Manifest und AppData
print_status "Kopiere Flatpak-Dateien..."
cp flatpak/org.securebits.bashscriptmaker.simple.yml build/flatpak/org.securebits.bashscriptmaker.yml
cp flatpak/org.securebits.bashscriptmaker.appdata.xml build/flatpak/

# Erstelle Desktop-Datei für Flatpak
print_status "Erstelle Desktop-Datei für Flatpak..."
cat > build/flatpak/org.securebits.bashscriptmaker.desktop << 'EOF'
[Desktop Entry]
Name=Bash-Script-Maker
Comment=Ein GUI-Programm zur Erstellung von Bash-Scripts
Exec=bash-script-maker
Icon=org.securebits.bashscriptmaker
Terminal=false
Type=Application
Categories=Development;Utility;
Keywords=bash;script;editor;generator;
StartupWMClass=bash-script-maker
EOF

# Kopiere Icon
print_status "Kopiere Icon..."
mkdir -p build/flatpak/icons/hicolor/scalable/apps
cp assets/bash-script-maker.svg build/flatpak/icons/hicolor/scalable/apps/org.securebits.bashscriptmaker.svg

# Erstelle requirements.txt für Flatpak
print_status "Erstelle requirements.txt für Flatpak..."
cat > build/flatpak/requirements.txt << 'EOF'
ttkbootstrap>=1.10.1
pygments>=2.15.1
EOF

# Erstelle setup.py für Flatpak
print_status "Erstelle setup.py für Flatpak..."
cat > build/flatpak/setup.py << 'EOF'
#!/usr/bin/env python3
from setuptools import setup

setup(
    name="bash-script-maker",
    version="1.2.1",
    py_modules=["bash_script_maker", "syntax_highlighter", "localization", "custom_dialogs", "assets"],
    entry_points={
        "console_scripts": [
            "bash-script-maker=bash_script_maker:main",
        ],
    },
    install_requires=[
        "ttkbootstrap>=1.10.1",
        "pygments>=2.15.1",
    ],
)
EOF

# Kopiere Python-Module
print_status "Kopiere Python-Module..."
cp bash_script_maker.py build/flatpak/
cp syntax_highlighter.py build/flatpak/
cp localization.py build/flatpak/
cp custom_dialogs.py build/flatpak/
cp assets.py build/flatpak/

# Erstelle Flatpak-Paket
print_status "Erstelle Flatpak-Paket..."
cd build/flatpak

if flatpak-builder --repo=repo --force-clean build org.securebits.bashscriptmaker.yml; then
    print_success "Flatpak-Paket erfolgreich erstellt!"
    
    # Erstelle Bundle
    print_status "Erstelle Flatpak-Bundle..."
    if flatpak build-bundle repo bash-script-maker.flatpak org.securebits.bashscriptmaker; then
        print_success "Flatpak-Bundle erstellt: bash-script-maker.flatpak"
        
        # Installiere das Paket
        print_status "Installiere Flatpak-Paket..."
        if flatpak install --user bash-script-maker.flatpak; then
            print_success "Flatpak-Paket erfolgreich installiert!"
            print_status "Sie können die App jetzt starten mit:"
            print_status "  flatpak run org.securebits.bashscriptmaker"
            print_status "Oder über das Anwendungsmenü suchen Sie nach 'Bash-Script-Maker'"
        else
            print_error "Fehler beim Installieren des Flatpak-Pakets"
            exit 1
        fi
    else
        print_error "Fehler beim Erstellen des Flatpak-Bundles"
        exit 1
    fi
else
    print_error "Fehler beim Erstellen des Flatpak-Pakets"
    exit 1
fi

cd ../..

echo ""
print_success "=== FLATPAK-INSTALLATION ABGESCHLOSSEN ==="
print_status "Die App ist jetzt als Flatpak-Paket installiert!"
print_status "Starten: flatpak run org.securebits.bashscriptmaker"
print_status "Deinstallieren: flatpak uninstall org.securebits.bashscriptmaker"
