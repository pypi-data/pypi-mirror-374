#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Icon-Generator für Bash-Script-Maker
Erstellt PNG-Icons in verschiedenen Größen aus der SVG-Datei
"""

import os
import sys

def generate_icons():
    """Generiert PNG-Icons aus der SVG-Datei"""
    try:
        import cairosvg
    except ImportError:
        print("Fehler: cairosvg ist nicht installiert.")
        print("Installieren Sie es mit: pip install cairosvg")
        return False
    
    # Pfade definieren
    script_dir = os.path.dirname(os.path.abspath(__file__))
    svg_path = os.path.join(script_dir, "assets", "bash-script-maker.svg")
    
    if not os.path.exists(svg_path):
        print(f"Fehler: SVG-Datei nicht gefunden: {svg_path}")
        return False
    
    # Icon-Größen definieren
    sizes = [16, 32, 48, 64, 128, 256]
    
    print("=== Bash-Script-Maker Icon Generator ===")
    print(f"Quelle: {svg_path}")
    print()
    
    success_count = 0
    
    for size in sizes:
        output_path = os.path.join(script_dir, "assets", f"bash-script-maker-{size}.png")
        
        try:
            # SVG zu PNG konvertieren
            cairosvg.svg2png(
                url=svg_path,
                write_to=output_path,
                output_width=size,
                output_height=size
            )
            
            # Dateigröße überprüfen
            file_size = os.path.getsize(output_path)
            print(f"✓ {os.path.basename(output_path)} ({size}x{size}) - {file_size:,} Bytes")
            success_count += 1
            
        except Exception as e:
            print(f"✗ Fehler bei {size}x{size}: {e}")
    
    print()
    print(f"Erfolgreich: {success_count}/{len(sizes)} Icons erstellt")
    return success_count == len(sizes)

def main():
    """Hauptfunktion"""
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print(__doc__)
        print("\nVerwendung:")
        print("  python3 generate_icons.py")
        print("\nVoraussetzungen:")
        print("  pip install cairosvg")
        return
    
    success = generate_icons()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
