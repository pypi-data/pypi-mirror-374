#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eigene, modern gestaltete Datei-Dialoge für den Bash-Script-Maker.
Diese ersetzen die nativen Tkinter-Dialoge, um ein konsistentes
Aussehen und Verhalten zu gewährleisten.
"""
import os
import tkinter as tk
from fnmatch import fnmatch
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from localization import _
from tkinter import messagebox


class CustomFileDialog(ttk.Toplevel):
    """
    Ein benutzerdefinierter Datei-Dialog, der ttkbootstrap-Widgets verwendet.
    """

    def __init__(
        self,
        parent,
        title="Datei auswählen",
        initialdir=os.path.expanduser("~"),
        filetypes=[("Alle Dateien", "*.*")],
        defaultextension=".sh",
        mode="open",
    ):
        super().__init__(parent)
        self.title(title)
        self.geometry("800x600")
        self.result = None
        self.current_path = os.path.abspath(initialdir)
        self.filetypes = filetypes
        self.defaultextension = defaultextension
        self.mode = mode  # 'open' oder 'save'

        # --- UI Erstellen ---
        container = ttk.Frame(self, padding=10)
        container.pack(fill=BOTH, expand=YES)
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # 1. Adressleiste und Navigation
        path_frame = self._create_path_frame(container)
        path_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))

        # 2. Baumansicht für Dateien und Ordner
        tree_frame = self._create_tree_frame(container)
        tree_frame.grid(row=1, column=0, sticky="nsew")

        # 3. Dateiname und Filter
        entry_frame = self._create_entry_frame(container)
        entry_frame.grid(row=2, column=0, sticky="ew", pady=(5, 0))

        # 4. Buttons (Öffnen/Speichern, Abbrechen)
        button_frame = self._create_button_frame(container)
        button_frame.grid(row=3, column=0, sticky="e", pady=(10, 0))

        self.update_path_entry()
        self.populate_tree()

    def _create_path_frame(self, parent):
        frame = ttk.Frame(parent)
        frame.grid_columnconfigure(1, weight=1)

        up_btn = ttk.Button(
            frame, text="↑", command=self.go_up, bootstyle="secondary"
        )
        up_btn.grid(row=0, column=0, padx=(0, 5))

        self.path_var = tk.StringVar()
        path_entry = ttk.Entry(frame, textvariable=self.path_var)
        path_entry.grid(row=0, column=1, sticky="ew")
        path_entry.bind("<Return>", self.path_entry_changed)

        return frame

    def _create_tree_frame(self, parent):
        frame = ttk.Frame(parent)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            frame, columns=("type", "size"), show="tree headings"
        )
        self.tree.heading("#0", text=_("Name"))
        self.tree.heading("type", text=_("Typ"))
        self.tree.heading("size", text=_("Größe"))
        self.tree.column("#0", stretch=YES)
        self.tree.column("type", width=100, anchor="w")
        self.tree.column("size", width=100, anchor="e")

        scrollbar = ttk.Scrollbar(
            frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Double-1>", self.on_tree_double_click)

        return frame

    def _create_entry_frame(self, parent):
        frame = ttk.Frame(parent)
        frame.grid_columnconfigure(0, weight=1)

        ttk.Label(frame, text=_("Dateiname:")).grid(
            row=0, column=0, sticky="w", padx=(5, 0)
        )
        self.filename_var = tk.StringVar()
        filename_entry = ttk.Entry(frame, textvariable=self.filename_var)
        filename_entry.grid(row=1, column=0, sticky="ew")

        self.filetype_var = tk.StringVar()
        filetype_combo = ttk.Combobox(
            frame,
            textvariable=self.filetype_var,
            values=[f"{desc} ({pat})" for desc, pat in self.filetypes],
        )
        filetype_combo.grid(row=1, column=1, padx=(5, 0))
        filetype_combo.current(0)
        filetype_combo.bind("<<ComboboxSelected>>", self.populate_tree)

        return frame

    def _create_button_frame(self, parent):
        frame = ttk.Frame(parent)
        ok_text = _("Speichern") if self.mode == "save" else _("Öffnen")
        ok_btn = ttk.Button(
            frame, text=ok_text, command=self.on_ok, bootstyle="success"
        )
        ok_btn.pack(side=RIGHT, padx=(5, 0))

        cancel_btn = ttk.Button(
            frame, text=_("Abbrechen"), command=self.on_cancel, bootstyle="secondary"
        )
        cancel_btn.pack(side=RIGHT)
        return frame

    def populate_tree(self, event=None):
        for i in self.tree.get_children():
            self.tree.delete(i)

        try:
            items = os.listdir(self.current_path)
            # Verzeichnisse zuerst
            dirs = sorted(
                [d for d in items if os.path.isdir(os.path.join(self.current_path, d))]
            )
            # Dann Dateien
            files = sorted(
                [f for f in items if os.path.isfile(os.path.join(self.current_path, f))]
            )

            for d in dirs:
                self.tree.insert("", "end", text=d, values=("Ordner", ""))

            selected_filter = self.filetype_var.get()
            filter_pattern = "*" # Default
            if selected_filter:
                try:
                    # Extrahiere das Muster aus "(Beschreibung (*.sh))"
                    filter_pattern = selected_filter.split('(')[1].split(')')[0]
                except IndexError:
                    pass
            
            for f in files:
                if fnmatch(f, filter_pattern) or filter_pattern == "*.*":
                    try:
                        size = os.path.getsize(os.path.join(self.current_path, f))
                        self.tree.insert("", "end", text=f, values=("Datei", f"{size} B"))
                    except OSError:
                        pass # Datei könnte ein Broken Symlink sein

        except OSError as e:
            self.tree.insert("", "end", text=_("Fehler: {}").format(str(e)), values=("", ""))

    def update_path_entry(self):
        self.path_var.set(self.current_path)

    def go_up(self):
        new_path = os.path.dirname(self.current_path)
        if os.path.isdir(new_path):
            self.current_path = new_path
            self.update_path_entry()
            self.populate_tree()
    
    def path_entry_changed(self, event=None):
        new_path = self.path_var.get()
        if os.path.isdir(new_path):
            self.current_path = new_path
            self.populate_tree()
        else:
            # Zurücksetzen auf den alten gültigen Pfad
            self.update_path_entry()

    def on_tree_select(self, event=None):
        selected_items = self.tree.selection()
        if selected_items:
            item_text = self.tree.item(selected_items[0], "text")
            self.filename_var.set(item_text)

    def on_tree_double_click(self, event=None):
        selected_items = self.tree.selection()
        if not selected_items:
            return

        item = self.tree.item(selected_items[0])
        item_text = item["text"]
        item_type = item["values"][0]

        if item_type == "Ordner":
            new_path = os.path.join(self.current_path, item_text)
            if os.path.isdir(new_path):
                self.current_path = new_path
                self.update_path_entry()
                self.populate_tree()
        else:
            # Bei Doppelklick auf eine Datei wird der Dialog bestätigt
            self.on_ok()

    def on_ok(self):
        filename = self.filename_var.get()
        if not filename:
            return

        # Füge die Standard-Endung hinzu, falls sie fehlt (nur im Speichern-Modus)
        if self.mode == "save":
            _, ext = os.path.splitext(filename)
            if not ext and self.defaultextension:
                 filename += self.defaultextension
        
        self.result = os.path.join(self.current_path, filename)
        
        # Prüfe im Speichern-Modus, ob die Datei existiert
        if self.mode == "save" and os.path.exists(self.result):
            if not messagebox.askyesno(
                _("Bestätigen"), _("Die Datei existiert bereits. Möchten Sie sie ersetzen?")
            ):
                self.result = None # Abbruch
                return

        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()

    def show(self):
        """Zeigt den Dialog an und wartet auf eine Benutzereingabe."""
        self.transient(self.master)
        self.grab_set()
        self.wait_window(self)
        return self.result


def askopenfilename(**kwargs):
    dialog = CustomFileDialog(mode="open", **kwargs)
    return dialog.show()


def asksaveasfilename(**kwargs):
    dialog = CustomFileDialog(mode="save", **kwargs)
    return dialog.show()
