#!/bin/bash
# Desktop-Integration für Bash-Script-Maker
# Installiert Desktop-Datei und Icon für alle Linux-Distributionen

echo "=== Bash-Script-Maker - Desktop-Integration ==="
echo "Dieses Script installiert die Desktop-Integration für alle Linux-Distributionen."
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

# Überprüfe, ob wir im richtigen Verzeichnis sind
if [ ! -f "bash-script-maker.desktop" ] || [ ! -f "assets/bash-script-maker.svg" ]; then
    print_error "Desktop-Datei oder Icon nicht gefunden!"
    print_status "Stellen Sie sicher, dass Sie im Projektverzeichnis sind."
    exit 1
fi

# Erstelle Verzeichnisse
print_status "Erstelle Verzeichnisse..."
mkdir -p ~/.local/share/applications
mkdir -p ~/.local/share/icons/hicolor/scalable/apps

# Kopiere Desktop-Datei
print_status "Installiere Desktop-Datei..."
if cp bash-script-maker.desktop ~/.local/share/applications/; then
    print_success "Desktop-Datei installiert: ~/.local/share/applications/bash-script-maker.desktop"
else
    print_error "Fehler beim Kopieren der Desktop-Datei!"
    exit 1
fi

# Kopiere Icon
print_status "Installiere Icon..."
if cp assets/bash-script-maker.svg ~/.local/share/icons/hicolor/scalable/apps/; then
    print_success "Icon installiert: ~/.local/share/icons/hicolor/scalable/apps/bash-script-maker.svg"
else
    print_error "Fehler beim Kopieren des Icons!"
    exit 1
fi

# Desktop-Datenbank aktualisieren
print_status "Aktualisiere Desktop-Datenbank..."
if command -v update-desktop-database &> /dev/null; then
    if update-desktop-database ~/.local/share/applications; then
        print_success "Desktop-Datenbank aktualisiert"
    else
        print_warning "Fehler beim Aktualisieren der Desktop-Datenbank"
    fi
else
    print_warning "update-desktop-database nicht gefunden"
fi

# Icon-Cache aktualisieren
print_status "Aktualisiere Icon-Cache..."
if command -v gtk-update-icon-cache &> /dev/null; then
    if gtk-update-icon-cache -f -t ~/.local/share/icons/hicolor; then
        print_success "Icon-Cache aktualisiert"
    else
        print_warning "Fehler beim Aktualisieren des Icon-Caches"
    fi
else
    print_warning "gtk-update-icon-cache nicht gefunden"
fi

# Berechtigungen setzen
print_status "Setze Berechtigungen..."
chmod +x ~/.local/share/applications/bash-script-maker.desktop

echo ""
print_success "=== DESKTOP-INTEGRATION ERFOLGREICH INSTALLIERT ==="
print_status "Die App ist jetzt verfügbar:"
print_status "  - Im Anwendungsmenü Ihrer Desktop-Umgebung"
print_status "  - Über den Befehl: bash-script-maker"
print_status "  - Mit dem Icon: bash-script-maker"
echo ""
print_status "Falls die App nicht im Menü erscheint, starten Sie Ihren Desktop neu."
