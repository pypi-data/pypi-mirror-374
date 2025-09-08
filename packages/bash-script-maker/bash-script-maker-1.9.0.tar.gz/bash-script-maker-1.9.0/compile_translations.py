import os
import polib
import struct

def compile_po_to_mo(po_file_path, mo_file_path):
    """
    Kompiliert eine .po-Datei in eine .mo-Datei.
    Diese Funktion stellt eine grundlegende Alternative zum msgfmt-Tool dar.
    """
    try:
        po = polib.pofile(po_file_path)
        mo_data = po.to_binary()
        
        # Sicherstellen, dass das Zielverzeichnis existiert
        os.makedirs(os.path.dirname(mo_file_path), exist_ok=True)
        
        with open(mo_file_path, "wb") as f:
            f.write(mo_data)
        
        print(f"Successfully compiled '{po_file_path}' to '{mo_file_path}'")
    except Exception as e:
        print(f"Error compiling '{po_file_path}': {e}")
        # Versuche einen Fallback, falls polib nicht installiert ist
        print("Attempting fallback compilation method...")
        try:
            with open(po_file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            messages = {}
            msgid = ""
            msgstr = ""
            in_msgid = False
            in_msgstr = False

            for line in lines:
                line = line.strip()
                if line.startswith("msgid "):
                    if msgid:
                        messages[msgid] = msgstr
                    msgid = line[6:].strip()[1:-1]
                    in_msgid = True
                    in_msgstr = False
                elif line.startswith("msgstr "):
                    msgstr = line[7:].strip()[1:-1]
                    in_msgstr = True
                    in_msgid = False
                elif line.startswith('"'):
                    if in_msgid:
                        msgid += line[1:-1]
                    elif in_msgstr:
                        msgstr += line[1:-1]
            if msgid:
                messages[msgid] = msgstr

            # .mo Datei schreiben (sehr vereinfacht)
            with open(mo_file_path, "wb") as f:
                # Header
                f.write(struct.pack('I', 0x950412de)) # Magic number
                f.write(struct.pack('I', 0)) # Version
                f.write(struct.pack('I', len(messages))) # Number of strings
                f.write(struct.pack('I', 28)) # Offset of original string table
                f.write(struct.pack('I', 28 + 8 * len(messages))) # Offset of translation string table
                f.write(struct.pack('I', 0)) # Hashing table size
                f.write(struct.pack('I', 28 + 16 * len(messages))) # Hashing table offset

                # String-Tabellen (Offsets)
                str_offset = 28 + 16 * len(messages)
                for msgid in messages:
                    f.write(struct.pack('I', len(msgid)))
                    f.write(struct.pack('I', str_offset))
                    str_offset += len(msgid) + 1
                for msgid, msgstr in messages.items():
                    f.write(struct.pack('I', len(msgstr)))
                    f.write(struct.pack('I', str_offset))
                    str_offset += len(msgstr) + 1

                # String-Daten
                for msgid in messages:
                    f.write(msgid.encode('utf-8') + b'\0')
                for msgstr in messages.values():
                    f.write(msgstr.encode('utf-8') + b'\0')
            print(f"Fallback compilation successful for '{po_file_path}'")
        except Exception as fallback_e:
            print(f"Fallback compilation failed: {fallback_e}")
            print("Please install 'polib' for a more reliable compilation: pip install polib")

def main():
    """
    Sucht nach allen .po-Dateien im 'locales'-Verzeichnis und kompiliert sie.
    """
    locales_dir = "locales"
    if not os.path.isdir(locales_dir):
        print(f"Error: Directory '{locales_dir}' not found.")
        return

    print("Starting compilation of .po files...")
    for root, _, files in os.walk(locales_dir):
        for file in files:
            if file.endswith(".po"):
                po_file_path = os.path.join(root, file)
                mo_file_path = po_file_path.replace(".po", ".mo")
                compile_po_to_mo(po_file_path, mo_file_path)
    print("Compilation finished.")

if __name__ == "__main__":
    # polib muss möglicherweise installiert werden: pip install polib
    try:
        import polib
    except ImportError:
        print("Warning: 'polib' library not found. Using a fallback method.")
        print("For best results, please install it via 'pip install polib'")
    
    main()
