#!/usr/bin/env bash
set -euo pipefail

APP_NAME="bash-script-maker"
APP_MODULE="bash_script_maker"
DESKTOP_USER1="$HOME/.local/share/applications/bash-script-maker.desktop"
DESKTOP_USER2="$HOME/.local/share/applications/org.securebits.bashscriptmaker.desktop"
ICON_USER1="$HOME/.local/share/icons/hicolor/scalable/apps/bash-script-maker.svg"
ICON_USER2="$HOME/.local/share/icons/hicolor/scalable/apps/org.securebits.bashscriptmaker.svg"
BIN_USER="$HOME/.local/bin/bash-script-maker"

DESKTOP_SYS1="/usr/share/applications/bash-script-maker.desktop"
DESKTOP_SYS2="/usr/share/applications/org.securebits.bashscriptmaker.desktop"
ICON_SYS1="/usr/share/icons/hicolor/scalable/apps/bash-script-maker.svg"
ICON_SYS2="/usr/share/icons/hicolor/scalable/apps/org.securebits.bashscriptmaker.svg"
BIN_SYS1="/usr/local/bin/bash-script-maker"
BIN_SYS2="/usr/bin/bash-script-maker"

CFG_DIRS=(
  "$HOME/.config/bash-script-maker"
  "$HOME/.cache/bash-script-maker"
  "$HOME/.local/share/bash-script-maker"
  "$HOME/.var/app/org.securebits.bashscriptmaker"
)

YES=0
USER_ONLY=0
KEEP_CONFIG=0

usage() {
  cat <<EOF
Uninstaller für $APP_NAME

Optionen:
  -y, --yes         Ohne Rückfrage fortfahren
  --user-only       Nur Benutzerinstallation bereinigen (kein sudo, keine Systempfade)
  --keep-config     Konfigurations-/Cache-Daten behalten
  -h, --help        Hilfe anzeigen
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -y|--yes) YES=1 ;;
    --user-only) USER_ONLY=1 ;;
    --keep-config) KEEP_CONFIG=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unbekannte Option: $1"; usage; exit 1 ;;
  esac
  shift
done

confirm() {
  [[ $YES -eq 1 ]] && return 0
  read -r -p "Soll $APP_NAME vollständig entfernt werden? [y/N] " ans
  [[ "${ans,,}" == "y" || "${ans,,}" == "yes" ]]
}

need_sudo() {
  [[ $USER_ONLY -eq 0 ]] && command -v sudo >/dev/null 2>&1
}

log() { echo -e "[uninstall] $*"; }

if ! confirm; then
  log "Abgebrochen."
  exit 0
fi

log "Entferne Python-Paket(e) via pip (falls vorhanden)…"
for PY in python3 python; do
  if command -v "$PY" >/dev/null 2>&1; then
    "$PY" -m pip uninstall -y "$APP_NAME" >/dev/null 2>&1 || true
    "$PY" -m pip uninstall -y "$APP_MODULE" >/dev/null 2>&1 || true
  fi
done

log "Entferne Nutzer-Binärdateien/Links…"
rm -f "$BIN_USER" 2>/dev/null || true

if [[ $USER_ONLY -eq 0 ]]; then
  if need_sudo; then
    log "Entferne System-Binärdateien/Links…"
    sudo rm -f "$BIN_SYS1" "$BIN_SYS2" 2>/dev/null || true
  fi
fi

log "Entferne .desktop-Dateien (Nutzer)…"
rm -f "$DESKTOP_USER1" "$DESKTOP_USER2" 2>/dev/null || true

if [[ $USER_ONLY -eq 0 ]] && need_sudo; then
  log "Entferne .desktop-Dateien (System)…"
  sudo rm -f "$DESKTOP_SYS1" "$DESKTOP_SYS2" 2>/dev/null || true
fi

log "Entferne Icons (Nutzer)…"
rm -f "$ICON_USER1" "$ICON_USER2" 2>/dev/null || true

if [[ $USER_ONLY -eq 0 ]] && need_sudo; then
  log "Entferne Icons (System)…"
  sudo rm -f "$ICON_SYS1" "$ICON_SYS2" 2>/dev/null || true
fi

if command -v flatpak >/dev/null 2>&1; then
  if flatpak list --app | grep -q '^org\.securebits\.bashscriptmaker'; then
    log "Entferne Flatpak-App org.securebits.bashscriptmaker…"
    flatpak uninstall -y org.securebits.bashscriptmaker >/dev/null 2>&1 || true
  fi
fi

if [[ $KEEP_CONFIG -eq 0 ]]; then
  log "Entferne Konfigurations-/Cache-Verzeichnisse…"
  for d in "${CFG_DIRS[@]}"; do
    rm -rf "$d" 2>/dev/null || true
  done
else
  log "Konfigurations-/Cache-Daten werden beibehalten (--keep-config)."
fi

log "Aktualisiere Desktop-/Icon-Caches…"
update-desktop-database "$HOME/.local/share/applications" >/dev/null 2>&1 || true
gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" >/dev/null 2>&1 || true

if [[ $USER_ONLY -eq 0 ]] && need_sudo; then
  sudo update-desktop-database /usr/share/applications >/dev/null 2>&1 || true
  sudo gtk-update-icon-cache -f -t /usr/share/icons/hicolor >/dev/null 2>&1 || true
fi

log "Prüfe restliche Einträge…"
which bash-script-maker >/dev/null 2>&1 && log "Hinweis: 'bash-script-maker' ist noch im PATH. Prüfe aktive Umgebungen/venvs."

log "Deinstallation abgeschlossen."
