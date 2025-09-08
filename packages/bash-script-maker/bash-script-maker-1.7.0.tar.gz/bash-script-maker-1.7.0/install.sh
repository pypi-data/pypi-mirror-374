#!/bin/bash
# Universelles Installationsscript für Bash-Script-Maker
# Erkennt automatisch den verfügbaren Paketmanager

echo "=== Bash-Script-Maker - Universelle Installation ==="
echo "Dieses Script erkennt automatisch Ihren Paketmanager und installiert alle Abhängigkeiten."
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

# Funktion zur Erkennung des Paketmanagers
detect_package_manager() {
    print_status "Erkenne Paketmanager..."

    if command -v apt &> /dev/null; then
        echo "apt (Ubuntu/Debian)"
        PACKAGE_MANAGER="apt"
        return 0
    elif command -v dnf &> /dev/null; then
        echo "dnf (Fedora/RHEL)"
        PACKAGE_MANAGER="dnf"
        return 0
    elif command -v yum &> /dev/null; then
        echo "yum (ältere Fedora/RHEL)"
        PACKAGE_MANAGER="yum"
        return 0
    elif command -v pacman &> /dev/null; then
        echo "pacman (Arch Linux)"
        PACKAGE_MANAGER="pacman"
        return 0
    elif command -v zypper &> /dev/null; then
        echo "zypper (openSUSE)"
        PACKAGE_MANAGER="zypper"
        return 0
    elif command -v emerge &> /dev/null; then
        echo "emerge (Gentoo)"
        PACKAGE_MANAGER="emerge"
        return 0
    else
        print_error "Kein unterstützter Paketmanager gefunden!"
        print_warning "Unterstützte Paketmanager: apt, dnf, yum, pacman, zypper, emerge"
        echo ""
        print_status "Für manuelle Installation siehe packages.txt oder README.md"
        exit 1
    fi
}

# Funktion zur Installation mit apt
install_apt() {
    print_status "Aktualisiere Paketliste..."
    if ! sudo apt update; then
        print_error "Fehler beim Aktualisieren der Paketliste."
        return 1
    fi

    print_status "Installiere Pakete..."
    if sudo apt install -y python3 python3-tk python3-pip zenity xterm; then
        print_success "Pakete erfolgreich installiert."
        return 0
    else
        print_error "Fehler bei der Installation."
        return 1
    fi
}

# Funktion zur Installation mit dnf
install_dnf() {
    print_status "Installiere Pakete..."
    if sudo dnf install -y python3 python3-tkinter python3-pip zenity xterm; then
        print_success "Pakete erfolgreich installiert."
        return 0
    else
        print_error "Fehler bei der Installation."
        return 1
    fi
}

# Funktion zur Installation mit yum
install_yum() {
    print_status "Installiere Pakete..."
    if sudo yum install -y python3 python3-tkinter python3-pip zenity xterm; then
        print_success "Pakete erfolgreich installiert."
        return 0
    else
        print_error "Fehler bei der Installation."
        return 1
    fi
}

# Funktion zur Installation mit pacman
install_pacman() {
    print_status "Installiere Pakete..."
    if sudo pacman -S --noconfirm python python-tk python-pip zenity xterm; then
        print_success "Pakete erfolgreich installiert."
        return 0
    else
        print_error "Fehler bei der Installation."
        return 1
    fi
}

# Funktion zur Installation mit zypper
install_zypper() {
    print_status "Installiere Pakete..."
    if sudo zypper install -y python3 python3-tk python3-pip zenity xterm; then
        print_success "Pakete erfolgreich installiert."
        return 0
    else
        print_error "Fehler bei der Installation."
        return 1
    fi
}

# Funktion zur Installation mit emerge
install_emerge() {
    print_status "Installiere Pakete..."
    if sudo emerge dev-lang/python dev-python/tkinter dev-python/pip x11-misc/zenity x11-terms/xterm; then
        print_success "Pakete erfolgreich installiert."
        return 0
    else
        print_error "Fehler bei der Installation."
        return 1
    fi
}

# Hauptinstallationsfunktion
main_installation() {
    print_status "Starte Installation für $PACKAGE_MANAGER..."

    case $PACKAGE_MANAGER in
        apt)
            install_apt
            ;;
        dnf)
            install_dnf
            ;;
        yum)
            install_yum
            ;;
        pacman)
            install_pacman
            ;;
        zypper)
            install_zypper
            ;;
        emerge)
            install_emerge
            ;;
        *)
            print_error "Unbekannter Paketmanager: $PACKAGE_MANAGER"
            return 1
            ;;
    esac
}

# Verifizierungsfunktion
verify_installation() {
    print_status "Überprüfe Installation..."

    # Python-Version
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_success "Python 3 gefunden: $PYTHON_VERSION"
    else
        print_error "Python 3 nicht gefunden!"
        return 1
    fi

    # Tkinter
    if python3 -c "import tkinter; print('Tkinter OK')" &> /dev/null; then
        print_success "Tkinter verfügbar"
    else
        print_error "Tkinter nicht verfügbar!"
        return 1
    fi

    # Zenity
    if command -v zenity &> /dev/null; then
        print_success "Zenity verfügbar"
    else
        print_error "Zenity nicht verfügbar!"
        return 1
    fi

    # Python-Paket: ttkbootstrap
    if python3 -c "import ttkbootstrap; print('ttkbootstrap OK')" &> /dev/null; then
        print_success "Python-Paket 'ttkbootstrap' installiert"
    else
        print_error "Python-Paket 'ttkbootstrap' fehlt!"
        return 1
    fi

    return 0
}

# Python-Abhängigkeiten installieren
install_python_requirements() {
    print_status "Installiere Python-Abhängigkeiten aus requirements.txt ..."

    # Stelle sicher, dass pip verfügbar ist
    if ! command -v python3 &> /dev/null; then
        print_error "python3 nicht gefunden. Bitte installieren und erneut versuchen."
        return 1
    fi

    # Bevorzugt: virtuelles Environment verwenden (vermeidet 'externally-managed-environment')
    VENV_DIR=".venv"
    if [ ! -d "$VENV_DIR" ]; then
        print_status "Erstelle virtuelles Environment in $VENV_DIR ..."
        if ! python3 -m venv "$VENV_DIR"; then
            print_warning "Konnte venv nicht erstellen. Prüfe, ob 'python3-venv' installiert ist."
            # Versuche, venv bereitzustellen (Debian/Ubuntu)
            if command -v apt &> /dev/null; then
                sudo apt update && sudo apt install -y python3-venv || true
                python3 -m venv "$VENV_DIR" || true
            fi
        fi
    fi

    if [ -x "$VENV_DIR/bin/pip" ]; then
        print_status "Aktiviere venv und installiere Requirements ..."
        "$VENV_DIR/bin/pip" install --upgrade pip
        if "$VENV_DIR/bin/pip" install -r requirements.txt; then
            print_success "Requirements in venv installiert."
            echo "$VENV_DIR" > .venv_path
            return 0
        else
            print_warning "Installation in venv fehlgeschlagen. Fallback auf Benutzerinstallation (--user)."
        fi
    fi

    # Fallback: Benutzerinstallation
    if python3 -m pip --version &> /dev/null; then
        python3 -m pip install --upgrade pip || true
        if python3 -m pip install --user -r requirements.txt; then
            print_success "Python-Abhängigkeiten (User) installiert."
            return 0
        fi
    else
        print_error "pip ist nicht verfügbar. Bitte installieren Sie 'python3-pip'."
    fi

    print_error "Installation der Python-Abhängigkeiten fehlgeschlagen."
    return 1
}

# Hauptprogramm
detect_package_manager
print_status "Erkannter Paketmanager: $PACKAGE_MANAGER"

echo ""
read -p "Möchten Sie fortfahren? (j/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Jj]$ ]]; then
    print_warning "Installation abgebrochen."
    exit 1
fi

# Installation durchführen
if main_installation; then
    echo ""
    # Python-Abhängigkeiten
    if ! install_python_requirements; then
        print_error "Python-Abhängigkeiten konnten nicht installiert werden."
        exit 1
    fi

    if verify_installation; then
        # Desktop-Integration installieren
        print_status "Installiere Desktop-Integration..."
        if [ -f "bash-script-maker.desktop" ] && [ -f "assets/bash-script-maker.svg" ]; then
            # Erstelle Verzeichnisse
            mkdir -p ~/.local/share/applications
            mkdir -p ~/.local/share/icons/hicolor/scalable/apps
            
            # Kopiere Icon
            cp assets/bash-script-maker.svg ~/.local/share/icons/hicolor/scalable/apps/
            
            # Erstelle Desktop-Datei mit korrekten absoluten Pfaden
            cat > ~/.local/share/applications/bash-script-maker.desktop << EOF
[Desktop Entry]
Name=Bash-Script-Maker
Comment=Ein GUI-Programm zur Erstellung von Bash-Scripts
Exec=$HOME/.local/bin/bash-script-maker
Icon=$HOME/.local/share/icons/hicolor/scalable/apps/bash-script-maker.svg
Terminal=false
Type=Application
Categories=Development;Utility;TextEditor;
Keywords=bash;script;editor;generator;development;
StartupWMClass=bash-script-maker
MimeType=text/x-shellscript;application/x-shellscript;
EOF
            
            # Berechtigungen setzen
            chmod +x ~/.local/share/applications/bash-script-maker.desktop
            
            # Desktop-Datenbank aktualisieren
            if command -v update-desktop-database &> /dev/null; then
                update-desktop-database ~/.local/share/applications
            fi
            
            if command -v gtk-update-icon-cache &> /dev/null; then
                gtk-update-icon-cache -f -t ~/.local/share/icons/hicolor
            fi
            
            print_success "Desktop-Integration installiert!"
            print_status "Die App ist jetzt im Anwendungsmenü verfügbar."
        else
            print_warning "Desktop-Datei oder Icon nicht gefunden. Desktop-Integration übersprungen."
        fi
        
        echo ""
        print_success "=== INSTALLATION ERFOLGREICH ABGESCHLOSSEN ==="
        print_status "Sie können Bash-Script-Maker jetzt starten mit:"
        echo "  bash-script-maker"
        echo "  (über das Anwendungsmenü oder Terminal)"
        echo ""
        print_status "Oder direkt mit:"
        echo "  python3 bash_script_maker.py"
        echo ""
        print_status "Viel Spaß mit Bash-Script-Maker! 🚀"
    else
        print_error "Installation unvollständig. Überprüfen Sie die Fehlermeldungen oben."
        exit 1
    fi
else
    print_error "Installation fehlgeschlagen."
    print_status "Für Hilfe siehe packages.txt oder README.md"
    exit 1
fi
