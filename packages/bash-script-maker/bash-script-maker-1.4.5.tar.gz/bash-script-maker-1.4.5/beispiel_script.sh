#!/bin/bash
# Beispiel-Script erstellt mit Bash-Script-Maker
# Dieses Script demonstriert verschiedene Funktionen

# Begrüßung
echo "Willkommen zum Bash-Script-Maker Demo!"

# Zenity Info-Dialog
zenity --info --text="Dies ist ein Beispiel-Script\nerstellt mit Bash-Script-Maker!" --title="Demo"

# Eingabe mit Zenity
name=$(zenity --entry --text="Wie heißen Sie?" --title="Eingabe")

if [ -n "$name" ]; then
    echo "Hallo $name!"

    # Frage-Dialog
    if zenity --question --text="Möchten Sie mehr über Bash-Scripts erfahren?" --title="Frage"; then
        zenity --info --text="Bash-Scripts sind sehr mächtig!\nBesuchen Sie unsere Dokumentation." --title="Info"
    else
        echo "Auf Wiedersehen $name!"
    fi
else
    echo "Keine Eingabe erhalten."
fi

# Systeminformationen anzeigen
echo "Systeminformationen:"
echo "Aktuelles Verzeichnis: $(pwd)"
echo "Benutzer: $(whoami)"
echo "Datum: $(date)"

# Schleife demonstrieren
echo "Zähle von 1 bis 5:"
for i in {1..5}; do
    echo "Zahl: $i"

    # Verschachtelte if-Anweisung
    if [ $i -eq 3 ]; then
        echo "Das ist die magische Zahl!"
    elif [ $i -gt 3 ]; then
        echo "Größer als 3"
    else
        echo "Kleiner oder gleich 3"
    fi
done

# Funktion demonstrieren
function zeige_info() {
    echo "=== System-Info ==="
    uname -a
    echo "Speicherplatz:"
    df -h /
    echo "=================="
}

# Funktion aufrufen
zeige_info

# Dateien auflisten
echo "Dateien im aktuellen Verzeichnis:"
ls -la

# Beispiel für Autovervollständigung
# Probieren Sie diese Befehle aus:
# - Schreiben Sie "ech" und drücken Sie Ctrl+Space -> "echo" wird vorgeschlagen
# - Schreiben Sie "$H" und drücken Sie Ctrl+Space -> "$HOME" wird vorgeschlagen
# - Schreiben Sie "/ho" und drücken Sie Ctrl+Space -> Pfadvorschläge werden angezeigt
# - Schreiben Sie "ls -" und drücken Sie Ctrl+Space -> ls-Optionen werden vorgeschlagen

echo "Demo-Script beendet!"
