#!/bin/bash
# Helper-Script zum Erstellen eines neuen Releases
# Usage: ./create_release.sh [version]

set -e

# Farbcodes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Überprüfe Git-Status
if [[ -n $(git status --porcelain) ]]; then
    print_error "Git working directory ist nicht sauber. Bitte committe alle Änderungen."
    git status --short
    exit 1
fi

# Hole aktuelle Version aus VERSION-Datei
CURRENT_VERSION=$(cat VERSION 2>/dev/null || echo "0.0.0")
print_status "Aktuelle Version: $CURRENT_VERSION"

# Bestimme neue Version
if [ $# -eq 1 ]; then
    NEW_VERSION="$1"
else
    echo "Welche Art von Release möchten Sie erstellen?"
    echo "1) Patch (Bug-Fix): $CURRENT_VERSION -> $(echo $CURRENT_VERSION | awk -F. '{print $1"."$2"."$3+1}')"
    echo "2) Minor (Feature): $CURRENT_VERSION -> $(echo $CURRENT_VERSION | awk -F. '{print $1"."$2+1".0"}')"
    echo "3) Major (Breaking): $CURRENT_VERSION -> $(echo $CURRENT_VERSION | awk -F. '{print $1+1".0.0"}')"
    echo "4) Custom version"
    
    read -p "Wählen Sie (1-4): " choice
    
    case $choice in
        1)
            NEW_VERSION=$(echo $CURRENT_VERSION | awk -F. '{print $1"."$2"."$3+1}')
            ;;
        2)
            NEW_VERSION=$(echo $CURRENT_VERSION | awk -F. '{print $1"."$2+1".0"}')
            ;;
        3)
            NEW_VERSION=$(echo $CURRENT_VERSION | awk -F. '{print $1+1".0.0"}')
            ;;
        4)
            read -p "Geben Sie die neue Version ein: " NEW_VERSION
            ;;
        *)
            print_error "Ungültige Auswahl"
            exit 1
            ;;
    esac
fi

# Validiere Version (Semantic Versioning)
if [[ ! $NEW_VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9-]+)?$ ]]; then
    print_error "Ungültiges Versionsformat. Verwenden Sie Semantic Versioning (z.B. 1.2.3 oder 1.2.3-beta)"
    exit 1
fi

print_status "Neue Version: $NEW_VERSION"

# Bestätigung
read -p "Möchten Sie Release v$NEW_VERSION erstellen? (j/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Jj]$ ]]; then
    print_warning "Release abgebrochen."
    exit 0
fi

# Aktualisiere Versionsdateien
print_status "Aktualisiere Versionsdateien..."

# VERSION-Datei
echo "$NEW_VERSION" > VERSION

# __version__.py
cat > __version__.py << EOF
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Version information for Bash-Script-Maker
"""

__version__ = "$NEW_VERSION"
__version_info__ = ($(echo $NEW_VERSION | sed 's/\([0-9]*\)\.\([0-9]*\)\.\([0-9]*\).*/\1, \2, \3/'))
EOF

# pyproject.toml
sed -i "s/^version = .*/version = \"$NEW_VERSION\"/" pyproject.toml

print_success "Versionsdateien aktualisiert"

# Committe Versionsänderungen
print_status "Committe Versionsänderungen..."
git add VERSION __version__.py pyproject.toml
git commit -m "chore: bump version to $NEW_VERSION"

# Erstelle und pushe Tag
print_status "Erstelle Git-Tag..."
git tag -a "v$NEW_VERSION" -m "Release version $NEW_VERSION

$(cat CHANGELOG.md | awk '/^## \[Unreleased\]/,/^## \[/ {if (!/^## \[/ || NR==1) print}' | head -n -1)"

print_status "Pushe Änderungen und Tag..."
git push origin main
git push origin "v$NEW_VERSION"

print_success "Release v$NEW_VERSION erfolgreich erstellt!"
print_status "GitHub Actions wird automatisch:"
print_status "  - GitHub Release erstellen"
print_status "  - Python-Pakete bauen"
print_status "  - Flatpak-Paket erstellen"
print_status "  - Auf PyPI veröffentlichen (falls konfiguriert)"
print_status ""
print_status "Überprüfen Sie den Fortschritt unter:"
print_status "  https://github.com/securebitsorg/bash-script-maker/actions"
