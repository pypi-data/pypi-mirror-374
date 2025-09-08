#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bash-Script-Maker - Ein GUI-Programm zur Erstellung von Bash-Scripts
"""

try:
    from __version__ import __version__
except ImportError:
    __version__ = "1.2.1"

import tkinter as tk
from tkinter import scrolledtext, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
import subprocess
import os
import sys
import webbrowser
from datetime import datetime
from tkinter import font as tkfont
from syntax_highlighter import EnhancedScriptEditor
from localization import _, save_language_setting
import configparser
from custom_dialogs import askopenfilename, asksaveasfilename


class FontSettingsDialog(ttk.Toplevel):
    def __init__(self, parent, editor):
        super().__init__(master=parent)
        self.title(_("Schriftart anpassen"))
        self.geometry("350x300")  # Feste Startgröße
        self.editor = editor

        # Aktuelle Schriftart ermitteln
        font_tuple = editor.base_font
        current_font_family = font_tuple[0]
        current_font_size = font_tuple[1]

        # UI Elemente
        container = ttk.Frame(self, padding=15)
        container.pack(fill=tk.BOTH, expand=True)

        # Schriftfamilie
        font_frame = ttk.Labelframe(container, text=_("Schriftart"), padding=10)
        font_frame.pack(fill=tk.X, pady=5)

        # Empfohlene Schriftarten für Code
        preferred_fonts = [
            "Source Code Pro",
            "Consolas",
            "Courier New",
            "DejaVu Sans Mono",
            "Liberation Mono",
            "Menlo",
            "Monaco",
        ]

        try:
            # Versuche, System-Schriftarten zu laden
            system_fonts = sorted(
                [f for f in tkfont.families() if not f.startswith("@")]
            )
            all_fonts = sorted(list(set(preferred_fonts + system_fonts)))
        except Exception:
            # Fallback, falls das Laden fehlschlägt
            all_fonts = sorted(preferred_fonts)

        if not all_fonts:
            # Fallback, falls gar keine Schriftarten gefunden werden
            all_fonts = ["Courier New", "Consolas", "Monaco"]
            ttk.Label(
                font_frame,
                text=_(
                    "Keine System-Schriftarten gefunden.\nBitte installieren Sie Schriftart-Pakete (z.B. 'ttf-mscorefonts-installer')."
                ),
                bootstyle="warning",
            ).pack(pady=5)

        self.font_var = tk.StringVar(value=current_font_family)
        self.font_combo = ttk.Combobox(
            font_frame, textvariable=self.font_var, values=all_fonts
        )
        self.font_combo.pack(fill=tk.X)

        # Schriftgröße
        size_frame = ttk.Labelframe(container, text=_("Schriftgröße"), padding=10)
        size_frame.pack(fill=tk.X, pady=5)

        self.size_var = tk.IntVar(value=current_font_size)
        self.size_spinbox = ttk.Spinbox(
            size_frame, from_=8, to=72, textvariable=self.size_var
        )
        self.size_spinbox.pack(fill=tk.X)

        # Buttons
        button_frame = ttk.Frame(container)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        apply_btn = ttk.Button(
            button_frame,
            text=_("Anwenden"),
            command=self.apply_settings,
            bootstyle="success",
        )
        apply_btn.pack(side=tk.RIGHT, padx=(5, 0))

        close_btn = ttk.Button(
            button_frame,
            text=_("Schließen"),
            command=self.destroy,
            bootstyle="secondary",
        )
        close_btn.pack(side=tk.RIGHT)

    def apply_settings(self):
        family = self.font_var.get()
        size = self.size_var.get()
        if family and size:
            self.editor.update_font(family, size)


class AboutDialog(ttk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(_("Über Bash-Script-Maker"))
        self.geometry("450x350")

        container = ttk.Frame(self, padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(
            container,
            text="Bash-Script-Maker",
            font=("", 18, "bold"),
            bootstyle="primary",
        )
        title_label.pack(pady=(0, 10))

        desc_text = _("Ein GUI-Programm zur einfachen Erstellung von Bash-Scripts.")
        desc_label = ttk.Label(container, text=desc_text, wraplength=400)
        desc_label.pack(pady=(0, 20))

        features_frame = ttk.Labelframe(container, text=_("Funktionen"), padding=15)
        features_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        features = [
            _("Visuelle Script-Erstellung"),
            _("Zenity-Dialog-Integration"),
            _("Syntax-Hervorhebung"),
            _("Script-Ausführung"),
            _("Anpassbare Schriftart & Themes"),
        ]
        for feature in features:
            ttk.Label(features_frame, text=f"• {feature}").pack(anchor=tk.W)

        # Version dynamisch aus VERSION-Datei lesen (Fallback zu pyproject)
        version_text = "1.0"
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            version_file = os.path.join(base_dir, "VERSION")
            if os.path.exists(version_file):
                with open(version_file, "r", encoding="utf-8") as vf:
                    version_text = vf.read().strip()
            else:
                # Optionaler Fallback: pyproject.toml parsen
                pyproj = os.path.join(base_dir, "pyproject.toml")
                if os.path.exists(pyproj):
                    import re

                    with open(pyproj, "r", encoding="utf-8") as pf:
                        content = pf.read()
                        m = re.search(r"^version\s*=\s*\"([^\"]+)\"", content, re.M)
                        if m:
                            version_text = m.group(1)
        except Exception:
            pass

        version_label = ttk.Label(
            container, text=_("Version: {}").format(version_text), bootstyle="secondary"
        )
        version_label.pack(pady=(15, 0))


class ScriptInfoDialog(ttk.Toplevel):
    def __init__(self, parent, script_name, content):
        super().__init__(parent)
        self.title(_("Script-Info"))
        self.geometry("400x250")

        container = ttk.Frame(self, padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(
            container, text=script_name, font=("", 16, "bold"), bootstyle="info"
        )
        title_label.pack(pady=(0, 15))

        # Berechnungen
        lines = len(content.split("\n"))
        chars = len(content)
        size_bytes = len(content.encode("utf-8"))

        # Info-Grid
        info_frame = ttk.Frame(container)
        info_frame.pack(fill=tk.X)

        ttk.Label(info_frame, text=_("Zeilen:"), font=("", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=2
        )
        ttk.Label(info_frame, text=f"{lines}").grid(
            row=0, column=1, sticky=tk.W, padx=5, pady=2
        )
        ttk.Label(info_frame, text=_("Zeichen:"), font=("", 10, "bold")).grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=2
        )
        ttk.Label(info_frame, text=f"{chars}").grid(
            row=1, column=1, sticky=tk.W, padx=5, pady=2
        )
        ttk.Label(info_frame, text=_("Größe:"), font=("", 10, "bold")).grid(
            row=2, column=0, sticky=tk.W, padx=5, pady=2
        )
        ttk.Label(info_frame, text=f"{size_bytes} Bytes").grid(
            row=2, column=1, sticky=tk.W, padx=5, pady=2
        )

        close_btn = ttk.Button(
            container, text=_("Schließen"), command=self.destroy, bootstyle="secondary"
        )
        close_btn.pack(side=tk.BOTTOM, pady=(20, 0))


class BashScriptMaker:
    def __init__(self, root):
        self.root = root
        self.root.title("Bash-Script-Maker")
        self.root.geometry("1200x800")

        # Variablen für den letzten Pfad
        self.last_path = os.path.expanduser("~")

        # Script-Variablen
        self.current_script = ""
        self.script_name = "mein_script.sh"

        # GUI erstellen
        self.create_menu()
        main_container = self.create_main_interface()
        self.create_command_palette(main_container)
        self.create_script_editor(main_container)

        # Willkommensnachricht
        self.update_script_content(
            "#!/bin/bash\n# Erstellt mit Bash-Script-Maker\n# "
            + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            + "\n\n"
        )

    def create_menu(self):
        """Erstellt das Menü der Anwendung"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Datei-Menü
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=_("Datei"), menu=file_menu)
        file_menu.add_command(
            label=_("Neu"), command=self.new_script, accelerator="Ctrl+N"
        )
        file_menu.add_command(
            label=_("Öffnen"), command=self.open_script, accelerator="Ctrl+O"
        )
        file_menu.add_command(
            label=_("Speichern"), command=self.save_script, accelerator="Ctrl+S"
        )
        file_menu.add_command(
            label=_("Speichern unter"),
            command=self.save_script_as,
            accelerator="Ctrl+Shift+S",
        )
        file_menu.add_separator()
        file_menu.add_command(
            label=_("Beenden"), command=self.root.quit, accelerator="Ctrl+Q"
        )

        # Bearbeiten-Menü
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=_("Bearbeiten"), menu=edit_menu)
        edit_menu.add_command(
            label=_("Rückgängig"),
            command=lambda: self.text_editor.edit_undo(),
            accelerator="Ctrl+Z",
        )
        edit_menu.add_command(
            label=_("Wiederholen"),
            command=lambda: self.text_editor.edit_redo(),
            accelerator="Ctrl+Y",
        )
        edit_menu.add_separator()
        edit_menu.add_command(
            label=_("Ausschneiden"),
            command=lambda: self.text_editor.event_generate("<<Cut>>"),
            accelerator="Ctrl+X",
        )
        edit_menu.add_command(
            label=_("Kopieren"),
            command=lambda: self.text_editor.event_generate("<<Copy>>"),
            accelerator="Ctrl+C",
        )
        edit_menu.add_command(
            label=_("Einfügen"),
            command=lambda: self.text_editor.event_generate("<<Paste>>"),
            accelerator="Ctrl+V",
        )

        # Skript-Menü
        script_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=_("Skript"), menu=script_menu)
        script_menu.add_command(
            label=_("Ausführen"), command=self.execute_script, accelerator="F5"
        )
        script_menu.add_command(
            label=_("Als ausführbar markieren"), command=self.make_executable
        )
        script_menu.add_separator()
        script_menu.add_command(
            label=_("Skript-Info anzeigen"), command=self.show_script_info
        )

        # Einstellungen-Menü
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=_("Einstellungen"), menu=settings_menu)
        settings_menu.add_command(
            label=_("Schriftart anpassen..."), command=self.open_font_dialog
        )
        # --- Sprachauswahl ---
        language_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label=_("Sprache"), menu=language_menu)
        language_menu.add_command(
            label="Deutsch", command=lambda: self.change_language("de")
        )
        language_menu.add_command(
            label="English", command=lambda: self.change_language("en")
        )

        # Hilfe-Menü
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=_("Hilfe"), menu=help_menu)
        help_menu.add_command(
            label=_("Dokumentation (README)"), command=self.open_documentation
        )
        help_menu.add_command(label="Secure-Bits Blog", command=self.open_blog)
        help_menu.add_separator()
        help_menu.add_command(label=_("Über"), command=self.show_about)

        # Tastenkombinationen
        self.root.bind("<Control-n>", lambda e: self.new_script())
        self.root.bind("<Control-o>", lambda e: self.open_script())
        self.root.bind("<Control-s>", lambda e: self.save_script())
        self.root.bind("<Control-Shift-S>", lambda e: self.save_script_as())
        self.root.bind("<Control-q>", lambda e: self.root.quit())
        self.root.bind("<F5>", lambda e: self.execute_script())

    def create_main_interface(self):
        """Erstellt die Hauptbenutzeroberfläche und den Container für die Haupt-Widgets."""
        # Statusleiste ganz unten platzieren
        self.status_var = tk.StringVar()
        self.status_var.set(_("Bereit"))
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bootstyle="inverse-dark",
            padding=5,
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Toolbar ganz oben platzieren
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=(5, 0))

        # Toolbar-Inhalte - LINKS
        btn_new = ttk.Button(
            toolbar, text=_("Neu"), command=self.new_script, bootstyle="primary"
        )
        btn_new.pack(side=tk.LEFT, padx=(0, 5), pady=20)
        ToolTip(btn_new, text=_("Erstellt ein neues, leeres Script (Ctrl+N)"))
        btn_open = ttk.Button(
            toolbar, text=_("Öffnen"), command=self.open_script, bootstyle="secondary"
        )
        btn_open.pack(side=tk.LEFT, padx=(5, 0), pady=20)
        ToolTip(btn_open, text=_("Öffnet ein vorhandenes Script (Ctrl+O)"))
        btn_save = ttk.Button(
            toolbar, text=_("Speichern"), command=self.save_script, bootstyle="info"
        )
        btn_save.pack(side=tk.LEFT, padx=(5, 0), pady=20)
        ToolTip(btn_save, text=_("Speichert das aktuelle Script (Ctrl+S)"))
        btn_exec = ttk.Button(
            toolbar,
            text=_("Ausführen"),
            command=self.execute_script,
            bootstyle="success",
        )
        btn_exec.pack(
            side=tk.LEFT, padx=(5, 15), pady=20
        )  # Extra Abstand nach dem letzten Button
        ToolTip(btn_exec, text=_("Führt das aktuelle Script aus (F5)"))

        # Separator für visuelle Trennung
        separator = ttk.Separator(toolbar, orient=tk.VERTICAL)
        separator.pack(side=tk.LEFT, fill="y", padx=5, pady=20)

        # Toolbar-Inhalte - RECHTS
        script_name_label = ttk.Label(toolbar, text=_("Script-Name:"))
        script_name_label.pack(side=tk.LEFT, padx=(5, 5), pady=20)

        self.name_entry = ttk.Entry(toolbar, width=40)
        self.name_entry.pack(
            side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True, pady=20
        )
        self.name_entry.insert(0, self.script_name)
        self.name_entry.bind("<KeyRelease>", self.update_script_name)

        # Hauptcontainer für linke und rechte Spalte (füllt den Rest des Platzes)
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=1)  # Rechte Spalte soll wachsen

        return main_container

    def create_command_palette(self, parent):
        """Erstellt die Befehlspalette mit verfügbaren Komponenten"""
        left_frame = ttk.LabelFrame(parent, text=_("Befehle & Komponenten"), padding=5)
        left_frame.grid(row=0, column=0, sticky="nswe")

        self.notebook = ttk.Notebook(left_frame, bootstyle="primary")
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Grundbefehle Tab
        basic_tab = ttk.Frame(self.notebook)
        self.notebook.add(basic_tab, text=_("Grundlagen"))

        basic_commands = [
            ("#!/bin/bash", _("Shebang")),
            ('echo "Hallo Welt"', _("Echo-Befehl")),
            ('read -p "Eingabe: " variable', _("Eingabe lesen")),
            ("if [ ]; then\nfi", _("If-Bedingung")),
            ("for i in {1..10}; do\necho $i\ndone", _("For-Schleife")),
            ("while [ ]; do\ndone", _("While-Schleife")),
            ("case $var in\n  pattern) ;;\n  *) ;;\nesac", _("Case-Anweisung")),
            ("function name() {\n}", _("Funktion")),
        ]

        self.create_command_buttons(basic_tab, basic_commands)

        # Zenity Tab
        zenity_tab = ttk.Frame(self.notebook)
        self.notebook.add(zenity_tab, text="Zenity")

        zenity_commands = [
            ('zenity --info --text="Info"', _("Info-Dialog")),
            ('zenity --error --text="Fehler"', _("Fehler-Dialog")),
            ('zenity --warning --text="Warnung"', _("Warnungs-Dialog")),
            ('zenity --question --text="Frage"', _("Frage-Dialog")),
            ('result=$(zenity --entry --text="Eingabe")', _("Eingabedialog")),
            ("file=$(zenity --file-selection)", _("Dateiauswahl")),
            ('zenity --progress --text="Fortschritt"', _("Fortschrittsbalken")),
            (
                'zenity --list --title="Liste" --column="Option"',
                _("Listen-Dialog"),
            ),
        ]

        self.create_command_buttons(zenity_tab, zenity_commands)

        # System Tab
        system_tab = ttk.Frame(self.notebook)
        self.notebook.add(system_tab, text=_("System"))

        system_commands = [
            ("ls -la", _("Dateien auflisten")),
            ("pwd", _("Aktuelles Verzeichnis")),
            ("cd /pfad", _("Verzeichnis wechseln")),
            ("mkdir neuer_ordner", _("Ordner erstellen")),
            ("rm -rf datei", _("Datei/Ordner löschen")),
            ("cp quelle ziel", _("Kopieren")),
            ("mv quelle ziel", _("Verschieben")),
            ("chmod +x script.sh", _("Ausführbar machen")),
            ("ps aux", _("Prozesse anzeigen")),
            ("kill PID", _("Prozess beenden")),
        ]

        self.create_command_buttons(system_tab, system_commands)

        # Variablen Tab
        variables_tab = ttk.Frame(self.notebook)
        self.notebook.add(variables_tab, text=_("Variablen"))

        variable_commands = [
            ('variable="wert"', _("Variable zuweisen")),
            ("echo $variable", _("Variable ausgeben")),
            ("${variable:-default}", _("Variable mit Default")),
            ("${#variable}", _("String-Länge")),
            ("${variable:0:5}", _("String extrahieren")),
            ("array=(wert1 wert2)", _("Array erstellen")),
            ("echo ${array[0]}", _("Array-Element")),
            ("echo ${#array[@]}", _("Array-Länge")),
        ]

        self.create_command_buttons(variables_tab, variable_commands)

    def create_command_buttons(self, parent, commands):
        """Erstellt Buttons für Befehle"""
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for cmd, desc in commands:
            btn = ttk.Button(
                scrollable_frame,
                text=desc,
                command=lambda c=cmd: self.insert_command(c),
                bootstyle="secondary",
            )
            btn.pack(fill=tk.X, pady=2, padx=5)
            ToolTip(btn, text=_("Einfügen: {}").format(cmd.splitlines()[0]))

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_script_editor(self, parent):
        """Erstellt den Script-Editor"""
        editor_container = ttk.Frame(parent)
        editor_container.grid(row=0, column=1, sticky="nswe")
        editor_container.grid_rowconfigure(0, weight=1)
        editor_container.grid_columnconfigure(0, weight=1)

        right_frame = ttk.LabelFrame(
            editor_container, text=_("Script-Editor"), padding=5
        )
        right_frame.grid(row=0, column=0, sticky="nswe")

        self.text_editor = EnhancedScriptEditor(
            right_frame, wrap=tk.WORD, autohide=True, vbar=True, hbar=True
        )
        self.text_editor.pack(fill=tk.BOTH, expand=True)

        # Support-Bereich unter dem Editor
        self.create_support_area(editor_container)

    def create_support_area(self, parent):
        """Erstellt den Bereich für die Support-Buttons."""
        support_frame = ttk.LabelFrame(
            parent, text=_(" Unterstützung "), bootstyle="secondary"
        )
        support_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=(0, 10))
        support_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # --- Button-Erstellung ohne fehlerhafte Bilder ---

        # GitHub Sponsors Button
        github_btn = ttk.Button(
            support_frame,
            text="GitHub Sponsors",
            bootstyle="success-outline",
            command=lambda: self.open_link("https://github.com/sponsors/securebitsorg"),
        )
        github_btn.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        ToolTip(github_btn, text=_("Unterstütze das Projekt auf GitHub Sponsors"))

        # Patreon Button
        patreon_btn = ttk.Button(
            support_frame,
            text="Patreon",
            bootstyle="info-outline",
            command=lambda: self.open_link("https://patreon.com/securebits"),
        )
        patreon_btn.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        ToolTip(patreon_btn, text=_("Unterstütze das Projekt auf Patreon"))

        # Ko-fi Button
        kofi_btn = ttk.Button(
            support_frame,
            text="Ko-fi",
            bootstyle="warning-outline",
            command=lambda: self.open_link("https://ko-fi.com/securebits"),
        )
        kofi_btn.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        ToolTip(kofi_btn, text=_("Spendiere einen Kaffee auf Ko-fi"))

    def insert_command(self, command):
        """Fügt einen Befehl in den Editor ein"""
        self.text_editor.insert_command_at_cursor(command)
        self.status_var.set(_("Befehl eingefügt: {}...").format(command[:30]))

    def update_script_content(self, content):
        """Aktualisiert den Script-Inhalt"""
        self.text_editor.delete(1.0, tk.END)
        self.text_editor.insert(1.0, content)

    def update_script_name(self, event=None):
        """Aktualisiert den Script-Namen"""
        self.script_name = self.name_entry.get()

    def new_script(self):
        """Erstellt ein neues Script"""
        if messagebox.askyesno(
            _("Neues Script"),
            _(
                "Möchten Sie ein neues Script erstellen? Nicht gespeicherte Änderungen gehen verloren."
            ),
        ):
            self.script_name = "mein_script.sh"
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, self.script_name)
            self.update_script_content(
                "#!/bin/bash\n# "
                + _("Erstellt mit Bash-Script-Maker")
                + "\n# "
                + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                + "\n\n"
            )
            self.status_var.set(_("Neues Script erstellt"))

    def open_script(self):
        """Öffnet ein vorhandenes Script"""
        file_path = askopenfilename(
            parent=self.root,
            title=_("Script öffnen"),
            initialdir=self.last_path,
            filetypes=[(_("Bash Scripts"), "*.sh"), (_("Alle Dateien"), "*.*")],
        )
        if file_path:
            self.last_path = os.path.dirname(file_path)
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                self.update_script_content(content)
                self.script_name = os.path.basename(file_path)
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, self.script_name)
                self.status_var.set(_("Script geladen: {}").format(file_path))
            except Exception as e:
                messagebox.showerror(
                    _("Fehler"), _("Fehler beim Laden des Scripts: {}").format(str(e))
                )

    def save_script(self):
        """Speichert das aktuelle Script"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, self.script_name)

        try:
            content = self.text_editor.get(1.0, tk.END).strip()
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)
            self.status_var.set(_("Script gespeichert: {}").format(file_path))
        except Exception as e:
            messagebox.showerror(
                _("Fehler"), _("Fehler beim Speichern: {}").format(str(e))
            )

    def save_script_as(self):
        """Speichert das Script unter einem neuen Namen"""
        file_path = asksaveasfilename(
            parent=self.root,
            title=_("Script speichern unter"),
            initialdir=self.last_path,
            initialfile=self.script_name,
            defaultextension=".sh",
            filetypes=[(_("Bash Scripts"), "*.sh"), (_("Alle Dateien"), "*.*")],
        )
        if file_path:
            self.last_path = os.path.dirname(file_path)
            try:
                content = self.text_editor.get(1.0, tk.END).strip()
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(content)
                self.script_name = os.path.basename(file_path)
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, self.script_name)
                self.status_var.set(_("Script gespeichert: {}").format(file_path))
            except Exception as e:
                messagebox.showerror(
                    _("Fehler"), _("Fehler beim Speichern: {}").format(str(e))
                )

    def execute_script(self):
        """Führt das aktuelle Script aus"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(script_dir, self.script_name)

        # Script zuerst speichern
        self.save_script()

        try:
            # Script ausführbar machen
            os.chmod(script_path, 0o755)

            # Script ausführen
            result = subprocess.run(
                [script_path], capture_output=True, text=True, cwd=script_dir
            )

            # Ergebnis anzeigen
            output_window = tk.Toplevel(self.root)
            output_window.title(_("Script-Ausgabe"))
            output_window.geometry("600x400")

            text_output = scrolledtext.ScrolledText(output_window, wrap=tk.WORD)
            text_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            if result.stdout:
                text_output.insert(tk.END, "STDOUT:\n" + result.stdout + "\n\n")
            if result.stderr:
                text_output.insert(tk.END, "STDERR:\n" + result.stderr + "\n\n")
            if result.returncode == 0:
                text_output.insert(
                    tk.END,
                    _("Script erfolgreich beendet (Exit-Code: {})").format(
                        result.returncode
                    ),
                )
            else:
                text_output.insert(
                    tk.END,
                    _("Script mit Fehler beendet (Exit-Code: {})").format(
                        result.returncode
                    ),
                )

            text_output.config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror(
                _("Fehler"), _("Fehler beim Ausführen des Scripts: {}").format(str(e))
            )

    def make_executable(self):
        """Macht das Script ausführbar"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(script_dir, self.script_name)

        try:
            os.chmod(script_path, 0o755)
            self.status_var.set(_("Script ist nun ausführbar"))
        except Exception as e:
            messagebox.showerror(
                _("Fehler"),
                _("Fehler beim Ändern der Berechtigungen: {}").format(str(e)),
            )

    def show_script_info(self):
        """Zeigt Informationen über das aktuelle Script"""
        content = self.text_editor.get(1.0, tk.END)
        ScriptInfoDialog(self.root, self.script_name, content)

    def show_about(self):
        """Zeigt About-Dialog"""
        about_text = _(
            "Bash-Script-Maker ist ein GUI-Programm zur einfachen Erstellung von Bash-Scripts.\n\n"
            "Erstellt mit Python und Tkinter"
        )

        messagebox.showinfo(_("Über Bash-Script-Maker"), about_text)

    def open_documentation(self):
        """Öffnet die README.md Datei im Standard-Browser."""
        try:
            readme_path = os.path.abspath("README.md")
            webbrowser.open(f"file://{readme_path}")
        except Exception as e:
            messagebox.showerror(
                _("Fehler"), _("Konnte die README.md nicht öffnen: {}").format(e)
            )

    def open_blog(self):
        """Öffnet den Secure-Bits Blog im Standard-Browser."""
        try:
            webbrowser.open("https://secure-bits.org")
        except Exception as e:
            messagebox.showerror(
                _("Fehler"), _("Konnte den Blog nicht öffnen: {}").format(e)
            )

    def open_font_dialog(self):
        """Öffnet den Dialog zur Schriftart-Anpassung."""
        FontSettingsDialog(self.root, self.text_editor)

    def change_language(self, language_code):
        """Speichert die ausgewählte Sprache und fordert zum Neustart auf."""
        save_language_setting(language_code)
        response = messagebox.showinfo(
            _("Neustart erforderlich"),
            _(
                "Die Sprache wurde geändert. Die Anwendung wird jetzt neu gestartet, um die Änderungen zu übernehmen."
            ),
        )

        if response == "ok":
            # Starte die Anwendung neu
            python = sys.executable
            os.execl(python, python, *sys.argv)


def main():
    # Die Sprache wird jetzt automatisch beim Import von 'localization' geladen.
    root = ttk.Window(themename="superhero")
    # Entfernt das Standard-Icon aus der Titelleiste
    root.iconphoto(False, tk.PhotoImage())
    app = BashScriptMaker(root)
    root.mainloop()


if __name__ == "__main__":
    main()
