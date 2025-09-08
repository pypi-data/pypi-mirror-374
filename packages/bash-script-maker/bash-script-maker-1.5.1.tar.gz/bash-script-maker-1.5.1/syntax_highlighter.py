#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Syntax-Highlighter für Bash-Scripts
"""

import tkinter as tk
from tkinter import scrolledtext, Listbox, Toplevel
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledText
import re
import os
import glob


class BashAutocomplete:
    """Autovervollständigung für Bash-Scripts"""

    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.suggestions_window = None
        self.suggestions_listbox = None
        self.current_suggestions = []
        self.current_word_start = None
        self.current_word_end = None

        # Bash-Befehle und Schlüsselwörter
        self.bash_commands = {
            # Grundlegende Befehle
            "echo",
            "printf",
            "read",
            "exit",
            "return",
            "cd",
            "pwd",
            "ls",
            "cp",
            "mv",
            "rm",
            "mkdir",
            "rmdir",
            "touch",
            "cat",
            "grep",
            "sed",
            "awk",
            "find",
            "chmod",
            "chown",
            "ps",
            "kill",
            "killall",
            "top",
            "df",
            "du",
            "free",
            "uname",
            "whoami",
            "id",
            "groups",
            "passwd",
            "su",
            "sudo",
            "which",
            "whereis",
            "locate",
            "updatedb",
            "tar",
            "gzip",
            "gunzip",
            "bzip2",
            "bunzip2",
            "zip",
            "unzip",
            "wget",
            "curl",
            # Erweiterte Befehle
            "head",
            "tail",
            "sort",
            "uniq",
            "wc",
            "cut",
            "paste",
            "tr",
            "diff",
            "patch",
            "comm",
            "join",
            "xargs",
            "tee",
            "yes",
            "seq",
            "bc",
            "dc",
            "expr",
            "let",
            "declare",
            "export",
            "unset",
            "set",
            "shift",
            "getopts",
            "source",
            "eval",
            "exec",
            "trap",
            "wait",
            "jobs",
            "fg",
            "bg",
            "disown",
            # Systembefehle
            "mount",
            "umount",
            "fdisk",
            "mkfs",
            "fsck",
            "dd",
            "mkswap",
            "swapon",
            "swapoff",
            "sysctl",
            "modprobe",
            "lsmod",
            "insmod",
            "rmmod",
            "lspci",
            "lsusb",
            "ifconfig",
            "ip",
            "route",
            "netstat",
            "ss",
            "ping",
            "traceroute",
            "nslookup",
            "dig",
            "host",
            "hostname",
            "date",
            "cal",
            "uptime",
            # Paketverwaltung
            "apt",
            "apt-get",
            "dpkg",
            "rpm",
            "yum",
            "dnf",
            "pacman",
            "zypper",
            "snap",
            "flatpak",
            # Text-Editoren
            "vi",
            "vim",
            "nano",
            "emacs",
            "gedit",
            "kate",
            "code",
            "subl",
            # Entwicklungstools
            "gcc",
            "g++",
            "make",
            "cmake",
            "git",
            "svn",
            "hg",
            "docker",
            "podman",
            "kubectl",
        }

        # Bash-Schlüsselwörter
        self.bash_keywords = {
            "if",
            "then",
            "else",
            "elif",
            "fi",
            "for",
            "while",
            "until",
            "do",
            "done",
            "case",
            "esac",
            "select",
            "function",
            "local",
            "readonly",
            "declare",
            "typeset",
            "export",
            "unset",
            "break",
            "continue",
            "return",
            "exit",
            "trap",
            "eval",
            "exec",
            "source",
            "alias",
            "unalias",
            "builtin",
            "command",
            "type",
            "hash",
            "help",
            "history",
            "fc",
            "bind",
            "set",
            "shopt",
            "caller",
            "false",
            "true",
        }

        # Häufige Optionen für Befehle
        self.command_options = {
            "ls": ["-l", "-a", "-h", "-la", "-lh", "-1", "-R", "-t", "-S", "-X"],
            "cp": ["-r", "-i", "-v", "-p", "-u", "-n", "--backup"],
            "mv": ["-i", "-v", "-u", "-n", "--backup"],
            "rm": ["-i", "-r", "-f", "-v", "--interactive=never"],
            "mkdir": ["-p", "-v", "-m"],
            "chmod": ["-R", "-v", "+x", "+r", "+w", "755", "644"],
            "chown": ["-R", "-v", "--reference"],
            "grep": ["-i", "-v", "-r", "-n", "-l", "-c", "--color"],
            "find": ["-name", "-type", "-exec", "-delete", "-mtime", "-size"],
            "ps": ["aux", "ef", "-p", "-u", "-C"],
            "tar": ["-xzf", "-czf", "-tzf", "-xvzf", "-cvzf"],
            "git": [
                "status",
                "add",
                "commit",
                "push",
                "pull",
                "clone",
                "branch",
                "checkout",
                "merge",
                "log",
            ],
        }

        # Event-Bindings für Autocomplete
        self.bind_events()

    def bind_events(self):
        """Bindet Events für Autocomplete"""
        # Strg+Space für Autocomplete
        self.text_widget.bind("<Control-space>", self.show_suggestions)
        # Tab für Autocomplete (alternative zu Tab für Einrückung)
        self.text_widget.bind("<Control-Tab>", self.show_suggestions)
        # Escape zum Schließen der Vorschlagsliste
        self.text_widget.bind("<Escape>", self.hide_suggestions)

    def get_current_word_bounds(self):
        """Ermittelt die Grenzen des aktuellen Wortes unter dem Cursor"""
        cursor_pos = self.text_widget.index(tk.INSERT)
        line, col = cursor_pos.split(".")

        # Hole die aktuelle Zeile
        line_content = self.text_widget.get(f"{line}.0", f"{line}.end")

        # Finde Wortgrenzen
        word_start = col
        word_end = col

        # Gehe rückwärts zum Wortanfang
        while word_start > 0 and (
            line_content[int(word_start) - 1].isalnum()
            or line_content[int(word_start) - 1] in "_-$/"
        ):
            word_start = str(int(word_start) - 1)

        # Gehe vorwärts zum Wortende
        while int(word_end) < len(line_content) and (
            line_content[int(word_end)].isalnum()
            or line_content[int(word_end)] in "_-$/"
        ):
            word_end = str(int(word_end) + 1)

        return f"{line}.{word_start}", f"{line}.{word_end}"

    def get_current_word(self):
        """Gibt das aktuelle Wort unter dem Cursor zurück"""
        start, end = self.get_current_word_bounds()
        return self.text_widget.get(start, end).strip()

    def get_context_aware_suggestions(self, partial_word, line_content, cursor_pos):
        """Generiert kontextabhängige Vorschläge"""
        suggestions = set()

        # Position in der Zeile
        line_num, col = cursor_pos.split(".")
        prefix = line_content[: int(col)].strip()

        # Prüfe Kontext
        if not partial_word:
            # Am Zeilenanfang - zeige alle Befehle
            suggestions.update(self.bash_commands)
            suggestions.update(self.bash_keywords)
        elif partial_word.startswith("$"):
            # Variablen
            suggestions.update(self.get_variable_suggestions())
        elif partial_word.startswith("/"):
            # Pfadvervollständigung
            suggestions.update(self.get_path_suggestions(partial_word))
        elif partial_word.startswith("./") or partial_word.startswith("../"):
            # Relativer Pfad
            suggestions.update(self.get_path_suggestions(partial_word))
        elif partial_word in self.command_options:
            # Optionen für bekannten Befehl
            suggestions.update(self.command_options[partial_word])
        else:
            # Normale Befehle und Schlüsselwörter
            # Filtere basierend auf Eingabe
            for cmd in self.bash_commands:
                if cmd.startswith(partial_word):
                    suggestions.add(cmd)

            for keyword in self.bash_keywords:
                if keyword.startswith(partial_word):
                    suggestions.add(keyword)

            # Wenn keine direkten Übereinstimmungen, zeige ähnliche
            if not suggestions:
                suggestions.update(self.get_similar_suggestions(partial_word))

        return sorted(list(suggestions))

    def get_variable_suggestions(self):
        """Sammelt alle Variablen aus dem Script"""
        variables = set()

        # Häufige Bash-Variablen
        variables.update(
            [
                "$HOME",
                "$PATH",
                "$PWD",
                "$USER",
                "$SHELL",
                "$0",
                "$1",
                "$2",
                "$3",
                "$?",
                "$$",
                "$!",
            ]
        )

        # Extrahiere benutzerdefinierte Variablen aus dem Text
        text_content = self.text_widget.get("1.0", tk.END)
        var_pattern = r"\b([A-Za-z_][A-Za-z0-9_]*)\s*="
        for match in re.finditer(var_pattern, text_content):
            var_name = match.group(1)
            variables.add(f"${var_name}")

        return variables

    def get_path_suggestions(self, partial_path):
        """Generiert Pfadvorschläge"""
        suggestions = set()

        try:
            # Expandiere ~ zu Home-Verzeichnis
            expanded_path = os.path.expanduser(partial_path)

            # Finde das Verzeichnis und den Präfix
            if os.path.isdir(expanded_path):
                base_dir = expanded_path
                prefix = ""
            else:
                base_dir = os.path.dirname(expanded_path) or "."
                prefix = os.path.basename(expanded_path)

            # Liste Dateien/Verzeichnisse auf
            if os.path.exists(base_dir):
                for item in os.listdir(base_dir):
                    if item.startswith(prefix):
                        full_path = os.path.join(base_dir, item)
                        if os.path.isdir(full_path):
                            suggestions.add(
                                os.path.join(os.path.dirname(partial_path), item) + "/"
                            )
                        else:
                            suggestions.add(
                                os.path.join(os.path.dirname(partial_path), item)
                            )

        except (OSError, ValueError):
            pass

        return suggestions

    def get_similar_suggestions(self, partial_word):
        """Findet ähnliche Befehle/Schlüsselwörter"""
        suggestions = set()
        partial_lower = partial_word.lower()

        # Fuzzy-Matching für Befehle
        for cmd in self.bash_commands:
            if partial_lower in cmd.lower():
                suggestions.add(cmd)

        # Fuzzy-Matching für Schlüsselwörter
        for keyword in self.bash_keywords:
            if partial_lower in keyword.lower():
                suggestions.add(keyword)

        return suggestions

    def show_suggestions(self, event=None):
        """Zeigt Vorschlagsliste an"""
        # Verstecke bestehende Vorschläge
        self.hide_suggestions()

        # Hole aktuelles Wort und Kontext
        current_word = self.get_current_word()
        cursor_pos = self.text_widget.index(tk.INSERT)
        line_num, col = cursor_pos.split(".")
        line_content = self.text_widget.get(f"{line_num}.0", f"{line_num}.end")

        # Generiere Vorschläge
        suggestions = self.get_context_aware_suggestions(
            current_word, line_content, cursor_pos
        )

        if not suggestions:
            return "break"

        # Erstelle Vorschlagsfenster
        self.current_word_start, self.current_word_end = self.get_current_word_bounds()
        self.current_suggestions = suggestions

        # Position für Vorschlagsfenster berechnen
        bbox = self.text_widget.bbox(self.current_word_end)
        if bbox:
            x, y, width, height = bbox
            x += self.text_widget.winfo_rootx()
            y += self.text_widget.winfo_rooty() + height
        else:
            # Fallback-Position
            x = self.text_widget.winfo_rootx() + 50
            y = self.text_widget.winfo_rooty() + 100

        # Erstelle Toplevel-Fenster
        self.suggestions_window = Toplevel(self.text_widget)
        self.suggestions_window.wm_overrideredirect(True)
        self.suggestions_window.wm_geometry(f"+{x}+{y}")

        # Erstelle Listbox
        self.suggestions_listbox = Listbox(
            self.suggestions_window,
            height=min(len(suggestions), 10),
            width=30,
            font=("Courier", 10),
        )

        # Füge Vorschläge hinzu
        for suggestion in suggestions:
            self.suggestions_listbox.insert(tk.END, suggestion)

        self.suggestions_listbox.pack()

        # Selektion des ersten Elements
        if suggestions:
            self.suggestions_listbox.selection_set(0)
            self.suggestions_listbox.activate(0)

        # Event-Bindings für Listbox
        self.suggestions_listbox.bind("<Return>", self.apply_suggestion)
        self.suggestions_listbox.bind("<Tab>", self.apply_suggestion)
        self.suggestions_listbox.bind("<Escape>", self.hide_suggestions)
        self.suggestions_listbox.bind("<Up>", lambda e: self.navigate_suggestions(-1))
        self.suggestions_listbox.bind("<Down>", lambda e: self.navigate_suggestions(1))
        self.suggestions_listbox.bind("<Button-1>", self.on_listbox_click)

        # Fokussiere Listbox
        self.suggestions_listbox.focus_set()

        return "break"

    def navigate_suggestions(self, direction):
        """Navigiert in der Vorschlagsliste"""
        if not self.suggestions_listbox:
            return

        current_selection = self.suggestions_listbox.curselection()
        if not current_selection:
            return

        current_index = current_selection[0]
        new_index = current_index + direction

        if 0 <= new_index < self.suggestions_listbox.size():
            self.suggestions_listbox.selection_clear(0, tk.END)
            self.suggestions_listbox.selection_set(new_index)
            self.suggestions_listbox.activate(new_index)
            self.suggestions_listbox.see(new_index)

    def on_listbox_click(self, event):
        """Behandelt Klicks in der Listbox"""
        if self.suggestions_listbox:
            self.apply_suggestion()

    def apply_suggestion(self, event=None):
        """Wendet den ausgewählten Vorschlag an"""
        if not self.suggestions_listbox:
            return

        selection = self.suggestions_listbox.curselection()
        if selection:
            selected_suggestion = self.suggestions_listbox.get(selection[0])

            # Ersetze das aktuelle Wort
            self.text_widget.delete(self.current_word_start, self.current_word_end)
            self.text_widget.insert(self.current_word_start, selected_suggestion)

            # Setze Cursor an das Ende
            self.text_widget.mark_set(
                tk.INSERT, f"{self.current_word_start} + {len(selected_suggestion)}c"
            )

        self.hide_suggestions()
        return "break"

    def hide_suggestions(self, event=None):
        """Versteckt die Vorschlagsliste"""
        if self.suggestions_window:
            self.suggestions_window.destroy()
            self.suggestions_window = None
            self.suggestions_listbox = None
            self.current_suggestions = []

        # Fokussiere zurück zum Text-Widget
        self.text_widget.focus_set()

        return "break"


class BashSyntaxHighlighter:
    """Syntax-Highlighter für Bash-Scripts"""

    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.highlighting_active = True
        self.tag_configs = {}  # Hält die Konfigurationen für die Tags

        # Syntax-Muster für Bash
        self.patterns = {
            "comments": r"#.*$",  # Kommentare
            "shebang": r"^#!/.*bash",  # Shebang
            "strings": r'(["\'])(?:(?=(\\?))\2.)*?\1',  # Strings
            "variables": r"\$[A-Za-z_][A-Za-z0-9_]*|\$\{[^}]+\}",  # Variablen
            "commands": r"\b(?:echo|read|if|then|else|elif|fi|for|while|do|done|case|esac|function|return|exit|cd|ls|pwd|mkdir|rm|cp|mv|chmod|chown|grep|sed|awk|cat|head|tail|sort|uniq|wc|find|ps|kill|sudo|apt|yum|dnf|pacman)\b",  # Häufige Befehle
            "operators": r"\b(?:-eq|-ne|-lt|-le|-gt|-ge|-f|-d|-e|-r|-w|-x|&&|\|\||==|!=|=~)\b",  # Operatoren
            "numbers": r"\b\d+\b",  # Zahlen
            "brackets": r"[(){}[\]]",  # Klammern
        }

        # Tag-Konfigurationen
        self.configure_tags()

        # Event-Binding für Live-Highlighting
        self.text_widget.bind("<KeyRelease>", self.highlight_syntax)
        self.text_widget.bind("<ButtonRelease>", self.highlight_syntax)

    def configure_tags(self):
        """Konfiguriert die Text-Tags für das Solarized Dark Theme"""
        # Solarized Dark Palette
        sol_base01 = "#586e75"  # Comments
        sol_cyan = "#2aa198"  # Shebang
        sol_orange = "#cb4b16"  # Strings, Numbers
        sol_blue = "#268bd2"  # Variables
        sol_green = "#859900"  # Commands, Keywords
        sol_magenta = "#d33682"  # Operators
        sol_base0 = "#839496"  # Brackets

        # Kommentare
        self.tag_configs["comments"] = {
            "foreground": sol_base01,
            "font": ("Courier", 10, "italic bold"),
        }
        self.text_widget.tag_configure("comments", **self.tag_configs["comments"])

        # Shebang
        self.tag_configs["shebang"] = {
            "foreground": sol_cyan,
            "font": ("Courier", 10, "bold"),
        }
        self.text_widget.tag_configure("shebang", **self.tag_configs["shebang"])

        # Strings
        self.tag_configs["strings"] = {
            "foreground": sol_orange,
            "font": ("Courier", 10, "bold"),
        }
        self.text_widget.tag_configure("strings", **self.tag_configs["strings"])

        # Variablen
        self.tag_configs["variables"] = {
            "foreground": sol_blue,
            "font": ("Courier", 10, "bold"),
        }
        self.text_widget.tag_configure("variables", **self.tag_configs["variables"])

        # Befehle & Schlüsselwörter
        self.tag_configs["commands"] = {
            "foreground": sol_green,
            "font": ("Courier", 10, "bold"),
        }
        self.text_widget.tag_configure("commands", **self.tag_configs["commands"])

        # Operatoren
        self.tag_configs["operators"] = {
            "foreground": sol_magenta,
            "font": ("Courier", 10, "bold"),
        }
        self.text_widget.tag_configure("operators", **self.tag_configs["operators"])

        # Zahlen
        self.tag_configs["numbers"] = {
            "foreground": sol_orange,
            "font": ("Courier", 10, "bold"),
        }
        self.text_widget.tag_configure("numbers", **self.tag_configs["numbers"])

        # Klammern
        self.tag_configs["brackets"] = {
            "foreground": sol_base0,
            "font": ("Courier", 10, "bold"),
        }
        self.text_widget.tag_configure("brackets", **self.tag_configs["brackets"])

    def highlight_syntax(self, event=None):
        """Hebt die Syntax im Text hervor"""
        if not self.highlighting_active:
            return

        # Entferne alle vorhandenen Tags
        for tag in self.patterns.keys():
            self.text_widget.tag_remove(tag, "1.0", tk.END)

        # Hole den gesamten Text
        text_content = self.text_widget.get("1.0", tk.END)

        # Hebe jedes Muster hervor
        for tag_name, pattern in self.patterns.items():
            self._highlight_pattern(tag_name, pattern, text_content)

    def _highlight_pattern(self, tag_name, pattern, text_content):
        """Hebt ein bestimmtes Muster hervor"""
        try:
            for match in re.finditer(pattern, text_content, re.MULTILINE):
                start = f"1.0 + {match.start()} chars"
                end = f"1.0 + {match.end()} chars"

                self.text_widget.tag_add(tag_name, start, end)
        except re.error:
            # Überspringe ungültige Regex-Muster
            pass

    def toggle_highlighting(self):
        """Schaltet Syntax-Highlighting ein/aus"""
        self.highlighting_active = not self.highlighting_active
        if self.highlighting_active:
            self.highlight_syntax()
        else:
            # Entferne alle Tags
            for tag in self.patterns.keys():
                self.text_widget.tag_remove(tag, "1.0", tk.END)


class BashScriptEditor(ScrolledText):
    """Bash-Script-Editor mit Syntax-Highlighting und Tab-Unterstützung"""

    def __init__(self, parent, **kwargs):
        # Tab-Konfiguration muss vor dem super().__init__ Aufruf stehen
        self.tab_size = 4  # 4 Leerzeichen pro Tab

        # Konfigurationen an das zugrundeliegende Text-Widget via kwargs weitergeben
        kwargs.setdefault("font", ("Courier", 10, "bold"))
        self.base_font = kwargs.get("font")
        kwargs.setdefault("tabs", (f"{self.tab_size}c",))

        super().__init__(parent, **kwargs)

        # Einrückungs-Schlüsselwörter
        self.indent_keywords = {
            "if",
            "then",
            "else",
            "elif",
            "for",
            "while",
            "until",
            "case",
            "function",
            "do",
        }
        self.dedent_keywords = {"fi", "done", "esac", "else", "elif"}

        # Syntax-Highlighter initialisieren
        self.highlighter = BashSyntaxHighlighter(self.text)

        # Autocomplete initialisieren
        self.autocomplete = BashAutocomplete(self.text)

        # Veraltete .config Aufrufe entfernt, da sie über kwargs an den Konstruktor übergeben werden
        # und teilweise mit dem Theme "superhero" in Konflikt stehen.

        # Tab-Event-Bindings
        self.text.bind("<Tab>", self.handle_tab)
        self.text.bind("<Shift-Tab>", self.handle_shift_tab)
        self.text.bind("<Return>", self.handle_return)
        self.text.bind("<BackSpace>", self.handle_backspace)

        # Rechtsklick-Menü
        self.create_context_menu()

    def create_context_menu(self):
        """Erstellt ein Rechtsklick-Kontextmenü"""
        self.context_menu = tk.Menu(self.text, tearoff=0)
        self.context_menu.add_command(
            label="Ausschneiden", command=lambda: self.event_generate("<<Cut>>")
        )
        self.context_menu.add_command(
            label="Kopieren", command=lambda: self.event_generate("<<Copy>>")
        )
        self.context_menu.add_command(
            label="Einfügen", command=lambda: self.event_generate("<<Paste>>")
        )
        self.context_menu.add_separator()
        self.context_menu.add_command(
            label="Alles auswählen", command=self.select_all, accelerator="Ctrl+A"
        )
        self.context_menu.add_separator()
        self.context_menu.add_command(
            label="Einrücken", command=self.insert_indent, accelerator="Tab"
        )
        self.context_menu.add_command(
            label="Ausrücken", command=self.remove_indent, accelerator="Shift+Tab"
        )
        self.context_menu.add_command(
            label="Zeile duplizieren", command=self.duplicate_line, accelerator="Ctrl+D"
        )
        self.context_menu.add_command(
            label="Kommentar umschalten",
            command=self.comment_uncomment_selection,
            accelerator="Ctrl+/",
        )
        self.context_menu.add_separator()
        self.context_menu.add_command(
            label="Autovervollständigung",
            command=self.autocomplete.show_suggestions,
            accelerator="Ctrl+Space",
        )
        self.context_menu.add_separator()
        self.context_menu.add_command(
            label="Syntax-Highlighting umschalten",
            command=self.highlighter.toggle_highlighting,
        )

        # Rechtsklick-Event binden
        self.text.bind("<Button-3>", self.show_context_menu)

        # Zusätzliche Tastenkombinationen
        self.text.bind("<Control-a>", lambda e: self.select_all())
        self.text.bind("<Control-d>", lambda e: self.duplicate_line())
        self.text.bind("<Control-slash>", lambda e: self.comment_uncomment_selection())

    def update_font(self, font_family, font_size):
        """Aktualisiert die Schriftart des Editors."""
        new_font = (font_family, font_size, "bold")
        self.text.config(font=new_font)
        # Sorge dafür, dass die Syntax-Tags die neue Schriftgröße übernehmen, aber ihre Stile beibehalten
        for tag_name, config in self.highlighter.tag_configs.items():
            font_config = config.get("font")
            if (
                font_config
                and isinstance(font_config, (list, tuple))
                and len(font_config) == 3
            ):
                # Behält den Stil (italic, bold) bei
                style = font_config[2]
                self.text.tag_configure(tag_name, font=(font_family, font_size, style))
            else:
                # Standard-Schriftart für andere Tags
                self.text.tag_configure(tag_name, font=new_font)

    def show_context_menu(self, event):
        """Zeigt das Kontextmenü an"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def select_all(self):
        """Wählt den gesamten Text aus"""
        self.tag_add(tk.SEL, "1.0", tk.END)
        self.mark_set(tk.INSERT, tk.END)
        self.see(tk.INSERT)

    def insert_command_at_cursor(self, command):
        """Fügt einen Befehl an der Cursor-Position ein"""
        current_pos = self.index(tk.INSERT)
        self.insert(current_pos, command + "\n")
        self.see(current_pos)

    def get_selected_text(self):
        """Gibt den ausgewählten Text zurück"""
        try:
            return self.get(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            return ""

    def replace_selected_text(self, new_text):
        """Ersetzt den ausgewählten Text"""
        try:
            self.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.insert(tk.INSERT, new_text)
        except tk.TclError:
            pass

    def duplicate_line(self):
        """Dupliziert die aktuelle Zeile"""
        current_line = self.index(tk.INSERT).split(".")[0]
        line_content = self.get(f"{current_line}.0", f"{current_line}.end")

        # Füge die Zeile nach der aktuellen ein
        self.insert(f"{current_line}.end", "\n" + line_content)

    def comment_uncomment_selection(self):
        """Kommentiert/entfernt Kommentar von ausgewähltem Text"""
        selected_text = self.get_selected_text()
        if not selected_text:
            return

        lines = selected_text.split("\n")
        commented_lines = []

        for line in lines:
            if line.strip().startswith("#"):
                # Entferne Kommentar
                commented_lines.append(line.replace("#", "", 1).lstrip())
            else:
                # Füge Kommentar hinzu
                commented_lines.append("# " + line)

        new_text = "\n".join(commented_lines)
        self.replace_selected_text(new_text)

    def handle_tab(self, event):
        """Behandelt Tab-Taste für Einrückung"""
        # Verhindere Standard-Tab-Verhalten
        self.after_idle(lambda: self.insert_indent())
        return "break"

    def handle_shift_tab(self, event):
        """Behandelt Shift+Tab für Ausrückung"""
        self.after_idle(lambda: self.remove_indent())
        return "break"

    def handle_return(self, event):
        """Behandelt Enter-Taste mit automatischer Einrückung"""
        # Hole die aktuelle Zeile
        current_line = self.index(tk.INSERT).split(".")[0]
        line_content = self.get(f"{current_line}.0", f"{current_line}.end")

        # Berechne Einrückung für die nächste Zeile
        indent_level = self._calculate_indent_level(line_content)

        # Füge Zeilenumbruch und Einrückung ein
        self.insert(tk.INSERT, "\n" + " " * (indent_level * self.tab_size))

        # Stelle sicher, dass die neue Zeile sichtbar ist
        self.see(tk.INSERT)
        return "break"

    def handle_backspace(self, event):
        """Behandelt Backspace mit intelligenter Ausrückung"""
        # Prüfe, ob wir am Anfang einer eingerückten Zeile sind
        current_pos = self.index(tk.INSERT)
        line_start = current_pos.split(".")[0] + ".0"
        line_content = self.get(line_start, current_pos)

        # Wenn die Zeile nur aus Leerzeichen besteht und wir am Ende sind
        if line_content.strip() == "" and len(line_content) > 0:
            # Lösche bis zum nächsten Tab-Stop
            spaces_to_remove = len(line_content) % self.tab_size
            if spaces_to_remove == 0:
                spaces_to_remove = self.tab_size

            # Lösche die Leerzeichen
            start_pos = f"{line_start} + {len(line_content) - spaces_to_remove} chars"
            self.delete(start_pos, current_pos)
            return "break"

        # Normales Backspace-Verhalten
        return None

    def insert_indent(self):
        """Fügt Einrückung an der aktuellen Position oder für ausgewählten Text ein"""
        try:
            # Prüfe, ob Text ausgewählt ist
            selected_text = self.get(tk.SEL_FIRST, tk.SEL_LAST)
            if selected_text:
                self._indent_selection()
            else:
                self._indent_current_line()
        except tk.TclError:
            # Kein ausgewählter Text
            self._indent_current_line()

    def remove_indent(self):
        """Entfernt Einrückung von der aktuellen Position oder ausgewähltem Text"""
        try:
            # Prüfe, ob Text ausgewählt ist
            selected_text = self.get(tk.SEL_FIRST, tk.SEL_LAST)
            if selected_text:
                self._dedent_selection()
            else:
                self._dedent_current_line()
        except tk.TclError:
            # Kein ausgewählter Text
            self._dedent_current_line()

    def _indent_current_line(self):
        """Rückt die aktuelle Zeile ein"""
        current_line = self.index(tk.INSERT).split(".")[0]
        line_start = f"{current_line}.0"
        line_content = self.get(line_start, f"{current_line}.end")

        # Füge Tab am Anfang der Zeile ein
        self.insert(line_start, " " * self.tab_size)

    def _dedent_current_line(self):
        """Rückt die aktuelle Zeile aus"""
        current_line = self.index(tk.INSERT).split(".")[0]
        line_start = f"{current_line}.0"
        line_content = self.get(line_start, f"{current_line}.end")

        # Entferne Leerzeichen vom Anfang der Zeile
        leading_spaces = len(line_content) - len(line_content.lstrip())
        spaces_to_remove = min(leading_spaces, self.tab_size)

        if spaces_to_remove > 0:
            end_pos = f"{line_start} + {spaces_to_remove} chars"
            self.delete(line_start, end_pos)

    def _indent_selection(self):
        """Rückt alle ausgewählten Zeilen ein"""
        start_line = self.index(tk.SEL_FIRST).split(".")[0]
        end_line = self.index(tk.SEL_LAST).split(".")[0]

        for line_num in range(int(start_line), int(end_line) + 1):
            line_start = f"{line_num}.0"
            self.insert(line_start, " " * self.tab_size)

        # Aktualisiere Auswahl
        new_start = f"{start_line}.0 + {self.tab_size} chars"
        new_end = f"{end_line}.end + {self.tab_size} chars"
        self.tag_remove(tk.SEL, "1.0", tk.END)
        self.tag_add(tk.SEL, new_start, new_end)

    def _dedent_selection(self):
        """Rückt alle ausgewählten Zeilen aus"""
        start_line = self.index(tk.SEL_FIRST).split(".")[0]
        end_line = self.index(tk.SEL_LAST).split(".")[0]

        total_removed = 0
        for line_num in range(int(start_line), int(end_line) + 1):
            line_start = f"{line_num}.0"
            line_content = self.get(line_start, f"{line_num}.end")

            leading_spaces = len(line_content) - len(line_content.lstrip())
            spaces_to_remove = min(leading_spaces, self.tab_size)

            if spaces_to_remove > 0:
                end_pos = f"{line_start} + {spaces_to_remove} chars"
                self.delete(line_start, end_pos)
                total_removed += spaces_to_remove

        # Aktualisiere Auswahl
        if total_removed > 0:
            new_end = f"{end_line}.end - {total_removed} chars"
            self.tag_remove(tk.SEL, "1.0", tk.END)
            self.tag_add(tk.SEL, tk.SEL_FIRST, new_end)

    def _calculate_indent_level(self, line_content):
        """Berechnet die Einrückungsebene für die nächste Zeile"""
        stripped_line = line_content.strip()

        # Prüfe auf Einrückung-erhöhende Schlüsselwörter
        if any(keyword in stripped_line for keyword in self.indent_keywords):
            return (len(line_content) - len(line_content.lstrip())) // self.tab_size + 1

        # Prüfe auf Einrückung-verringernde Schlüsselwörter
        if any(keyword in stripped_line for keyword in self.dedent_keywords):
            current_indent = (
                len(line_content) - len(line_content.lstrip())
            ) // self.tab_size
            return max(0, current_indent - 1)

        # Behalte aktuelle Einrückungsebene bei
        return (len(line_content) - len(line_content.lstrip())) // self.tab_size

    def get_current_indent_level(self):
        """Gibt die aktuelle Einrückungsebene zurück"""
        current_line = self.index(tk.INSERT).split(".")[0]
        line_content = self.get(f"{current_line}.0", f"{current_line}.end")
        return (len(line_content) - len(line_content.lstrip())) // self.tab_size


# Alias für Abwärtskompatibilität
EnhancedScriptEditor = BashScriptEditor
