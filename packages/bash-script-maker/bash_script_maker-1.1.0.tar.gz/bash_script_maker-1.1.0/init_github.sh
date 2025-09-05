#!/bin/bash
# GitHub Repository Initialisierung für Bash-Script-Maker

echo "=== Bash-Script-Maker - GitHub Repository Setup ==="
echo ""

# Farbcodes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Überprüfen, ob Git installiert ist
if ! command -v git &> /dev/null; then
    print_error "Git ist nicht installiert. Bitte installieren Sie Git zuerst."
    exit 1
fi

# Überprüfen, ob bereits ein Git-Repository ist
if [ -d ".git" ]; then
    print_warning "Git-Repository bereits initialisiert."
    read -p "Möchten Sie trotzdem fortfahren? (j/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Jj]$ ]]; then
        print_warning "Abbruch."
        exit 1
    fi
else
    print_status "Initialisiere Git-Repository..."
    git init
fi

# Git-Konfiguration abfragen
print_status "Git-Konfiguration überprüfen..."

if [ -z "$(git config --global user.name)" ]; then
    read -p "Git Benutzername: " git_username
    git config --global user.name "$git_username"
fi

if [ -z "$(git config --global user.email)" ]; then
    read -p "Git E-Mail: " git_email
    git config --global user.email "$git_email"
fi

print_success "Git-Konfiguration: $(git config --global user.name) <$(git config --global user.email)>"

# Repository-URL abfragen
if [ -z "$(git remote get-url origin 2>/dev/null)" ]; then
    echo ""
    print_status "Repository-URL eingeben:"
    print_status "Format: https://github.com/IHR_BENUTZERNAME/bash-script-maker.git"
    read -p "GitHub Repository URL: " repo_url

    if [ -z "$repo_url" ]; then
        print_error "Keine Repository-URL angegeben."
        exit 1
    fi

    git remote add origin "$repo_url"
else
    repo_url=$(git remote get-url origin)
    print_success "Repository bereits konfiguriert: $repo_url"
fi

# Branch auf main setzen
print_status "Setze Hauptbranch auf 'main'..."
git branch -M main

# Alle Dateien hinzufügen
print_status "Füge alle Dateien hinzu..."
git add .

# Überprüfen, ob es etwas zu committen gibt
if [ -z "$(git status --porcelain)" ]; then
    print_warning "Keine Änderungen zum Committen gefunden."
    exit 0
fi

# Commit erstellen
print_status "Erstelle Commit..."
git commit -m "🎉 Initial commit: Bash-Script-Maker mit GitHub Actions CI/CD

✨ Features:
• GUI-Programm zur Bash-Script-Erstellung
• Syntax-Highlighting für Bash-Scripts
• Autovervollständigung
• Intelligente Tab-Funktionalität
• Zenity-Dialog-Integration

🔧 Technik:
• Vollständige GitHub Actions CI/CD Pipeline
• Automatische Releases und Package-Publishing
• CodeQL Security Scanning
• Mehrere Linux-Distributionen unterstützt
• Umfassende Test-Suite

📚 Dokumentation:
• Detaillierte Setup-Anleitungen
• Installationsscripts für verschiedene Distributionen
• Vollständige API-Dokumentation"

# Push zu GitHub
print_status "Push zu GitHub..."
if git push -u origin main; then
    print_success "Repository erfolgreich zu GitHub gepusht!"
else
    print_error "Fehler beim Push zu GitHub."
    print_status "Mögliche Ursachen:"
    echo "  • Falsche Repository-URL"
    echo "  • Keine Berechtigung für das Repository"
    echo "  • Netzwerkprobleme"
    echo ""
    print_status "Überprüfen Sie Ihre Repository-URL und Berechtigungen."
    exit 1
fi

echo ""
print_success "=== GitHub Repository erfolgreich initialisiert! ==="
print_status "Nächste Schritte:"
echo "1. Gehen Sie zu: $repo_url"
echo "2. Überprüfen Sie den Actions Tab für die CI/CD Pipeline"
echo "3. Setzen Sie die GitHub Secrets (siehe GITHUB_SETUP.md)"
echo "4. Erstellen Sie Ihren ersten Release"
echo ""
print_status "Viel Erfolg mit Bash-Script-Maker! 🚀"
