#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bash-Script-Maker - Vereinfachte Flatpak-Version
Ein benutzerfreundliches GUI-Programm zur Erstellung von Bash-Scripts
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import os
import subprocess
import sys
import threading

class BashScriptMaker:
    def __init__(self, root):
        self.root = root
        self.root.title("Bash Script Maker")  # Korrigierter Titel
        self.root.geometry("1000x700")
        
        # Set window class for proper desktop integration
        self.root.wm_class("Bash-Script-Maker", "Bash-Script-Maker")
        
        # Variables
        self.current_file = None
        
        # Create GUI
        self.create_widgets()
        
    def create_widgets(self):
        # Menu
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Datei", menu=file_menu)
        file_menu.add_command(label="Neu", command=self.new_file)
        file_menu.add_command(label="Öffnen", command=self.open_file)
        file_menu.add_command(label="Speichern", command=self.save_file)
        file_menu.add_command(label="Speichern unter...", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Beenden", command=self.root.quit)
        
        run_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ausführen", menu=run_menu)
        run_menu.add_command(label="Script ausführen", command=self.run_script)
        
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Commands
        left_frame = ttk.LabelFrame(main_frame, text="Befehle")
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Command buttons
        commands = [
            ("Shebang", self.insert_shebang),
            ("Echo", self.insert_echo),
            ("Variable", self.insert_variable),
            ("If-Statement", self.insert_if),
            ("For-Loop", self.insert_for),
            ("While-Loop", self.insert_while),
            ("Function", self.insert_function),
            ("Kommentar", self.insert_comment),
        ]
        
        for cmd_name, cmd_func in commands:
            btn = ttk.Button(left_frame, text=cmd_name, command=cmd_func, width=15)
            btn.pack(pady=2, padx=5, fill=tk.X)
        
        # Right panel - Editor
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Editor
        self.text_editor = scrolledtext.ScrolledText(
            right_frame, 
            wrap=tk.NONE, 
            font=("Monaco", 11) if sys.platform == "darwin" else ("Consolas", 11),
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="#ffffff",
            selectbackground="#264f78",
            relief=tk.FLAT,
            borderwidth=1
        )
        self.text_editor.pack(fill=tk.BOTH, expand=True)
        
        # Add basic syntax highlighting
        self.setup_syntax_highlighting()
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Bereit | Flatpak-Version", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 10))
    
    def setup_syntax_highlighting(self):
        """Setup basic syntax highlighting for bash scripts"""
        # Define colors for syntax highlighting
        self.text_editor.tag_config("comment", foreground="#6a9955", font=("Consolas", 11, "italic"))
        self.text_editor.tag_config("keyword", foreground="#569cd6", font=("Consolas", 11, "bold"))
        self.text_editor.tag_config("string", foreground="#ce9178")
        self.text_editor.tag_config("variable", foreground="#9cdcfe")
        self.text_editor.tag_config("operator", foreground="#d4d4d4")
        
        # Bind text change event for live highlighting
        self.text_editor.bind("<KeyRelease>", self.on_text_change)
    
    def on_text_change(self, event=None):
        """Apply basic syntax highlighting on text change"""
        import re
        content = self.text_editor.get("1.0", tk.END)
        
        # Clear existing tags
        for tag in ["comment", "keyword", "string", "variable"]:
            self.text_editor.tag_delete(tag)
        
        # Highlight comments
        for match in re.finditer(r'#.*', content):
            start_line = content[:match.start()].count('\n') + 1
            start_col = match.start() - content.rfind('\n', 0, match.start()) - 1
            end_line = content[:match.end()].count('\n') + 1
            end_col = match.end() - content.rfind('\n', 0, match.end()) - 1
            self.text_editor.tag_add("comment", f"{start_line}.{start_col}", f"{end_line}.{end_col}")
        
        # Highlight bash keywords
        keywords = r'\b(if|then|else|elif|fi|for|while|do|done|case|esac|function|return|exit|break|continue|echo|read|export|local)\b'
        for match in re.finditer(keywords, content):
            start_line = content[:match.start()].count('\n') + 1
            start_col = match.start() - content.rfind('\n', 0, match.start()) - 1
            end_line = content[:match.end()].count('\n') + 1
            end_col = match.end() - content.rfind('\n', 0, match.end()) - 1
            self.text_editor.tag_add("keyword", f"{start_line}.{start_col}", f"{end_line}.{end_col}")
        
        # Highlight strings
        for match in re.finditer(r'"[^"]*"', content):
            start_line = content[:match.start()].count('\n') + 1
            start_col = match.start() - content.rfind('\n', 0, match.start()) - 1
            end_line = content[:match.end()].count('\n') + 1
            end_col = match.end() - content.rfind('\n', 0, match.end()) - 1
            self.text_editor.tag_add("string", f"{start_line}.{start_col}", f"{end_line}.{end_col}")
        
        # Highlight variables
        for match in re.finditer(r'\$\w+|\$\{[^}]+\}', content):
            start_line = content[:match.start()].count('\n') + 1
            start_col = match.start() - content.rfind('\n', 0, match.start()) - 1
            end_line = content[:match.end()].count('\n') + 1
            end_col = match.end() - content.rfind('\n', 0, match.end()) - 1
            self.text_editor.tag_add("variable", f"{start_line}.{start_col}", f"{end_line}.{end_col}")
        
    def insert_shebang(self):
        self.text_editor.insert(tk.INSERT, "#!/bin/bash\n")
        
    def insert_echo(self):
        self.text_editor.insert(tk.INSERT, 'echo "Hello World"\n')
        
    def insert_variable(self):
        self.text_editor.insert(tk.INSERT, 'VARIABLE="value"\necho "$VARIABLE"\n')
        
    def insert_if(self):
        template = '''if [ condition ]; then
    # commands
elif [ condition ]; then
    # commands
else
    # commands
fi
'''
        self.text_editor.insert(tk.INSERT, template)
        
    def insert_for(self):
        template = '''for item in list; do
    echo "$item"
done
'''
        self.text_editor.insert(tk.INSERT, template)
        
    def insert_while(self):
        template = '''while [ condition ]; do
    # commands
done
'''
        self.text_editor.insert(tk.INSERT, template)
        
    def insert_function(self):
        template = '''function_name() {
    # commands
    return 0
}
'''
        self.text_editor.insert(tk.INSERT, template)
        
    def insert_comment(self):
        self.text_editor.insert(tk.INSERT, "# Kommentar\n")
        
    def new_file(self):
        if messagebox.askyesno("Neu", "Aktuelles Script verwerfen?"):
            self.text_editor.delete(1.0, tk.END)
            self.current_file = None
            self.update_title()
            
    def open_file(self):
        filename = filedialog.askopenfilename(
            title="Script öffnen",
            filetypes=[("Bash Scripts", "*.sh"), ("Alle Dateien", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.text_editor.delete(1.0, tk.END)
                self.text_editor.insert(1.0, content)
                self.current_file = filename
                self.update_title()
            except Exception as e:
                messagebox.showerror("Fehler", f"Datei konnte nicht geöffnet werden: {e}")
                
    def save_file(self):
        if self.current_file:
            self.save_to_file(self.current_file)
        else:
            self.save_as_file()
            
    def save_as_file(self):
        filename = filedialog.asksaveasfilename(
            title="Script speichern",
            defaultextension=".sh",
            filetypes=[("Bash Scripts", "*.sh"), ("Alle Dateien", "*.*")]
        )
        if filename:
            self.save_to_file(filename)
            self.current_file = filename
            self.update_title()
            
    def save_to_file(self, filename):
        try:
            content = self.text_editor.get(1.0, tk.END)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            # Make executable
            os.chmod(filename, 0o755)
            self.status_bar.config(text=f"Gespeichert: {filename}")
        except Exception as e:
            messagebox.showerror("Fehler", f"Datei konnte nicht gespeichert werden: {e}")
            
    def run_script(self):
        if not self.current_file:
            if messagebox.askyesno("Speichern", "Script muss erst gespeichert werden. Jetzt speichern?"):
                self.save_as_file()
                if not self.current_file:
                    return
            else:
                return
                
        def run_in_thread():
            try:
                result = subprocess.run(
                    ["bash", self.current_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                output = result.stdout + result.stderr
                if output:
                    messagebox.showinfo("Script-Ausgabe", output)
                else:
                    messagebox.showinfo("Script-Ausgabe", "Script erfolgreich ausgeführt (keine Ausgabe)")
                    
            except subprocess.TimeoutExpired:
                messagebox.showerror("Fehler", "Script-Ausführung abgebrochen (Timeout)")
            except Exception as e:
                messagebox.showerror("Fehler", f"Script-Ausführung fehlgeschlagen: {e}")
                
        threading.Thread(target=run_in_thread, daemon=True).start()
        
    def update_title(self):
        title = "Bash-Script-Maker"
        if self.current_file:
            title += f" - {os.path.basename(self.current_file)}"
        self.root.title(title)

def main():
    root = tk.Tk()
    app = BashScriptMaker(root)
    root.mainloop()

if __name__ == "__main__":
    main()
