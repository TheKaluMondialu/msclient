#!/usr/bin/env python3
"""
Custom dialog windows for CS 1.6 Master Server GUI.
Includes add server, edit config, about, and error alert dialogs.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Tuple
from theme import Colors, Fonts, Layout, Icons


class AddServerDialog(tk.Toplevel):
    """
    Dialog for adding a new server to the list.
    """
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.title("Add Server")
        self.geometry("400x200")
        self.resizable(False, False)
        
        # Center the dialog
        self.transient(parent)
        self.grab_set()
        
        self.result: Optional[Tuple[str, int]] = None
        
        # Create widgets
        main_frame = tk.Frame(self, padx=Layout.PADDING_LARGE, pady=Layout.PADDING_LARGE)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # IP Address
        tk.Label(
            main_frame,
            text="IP Address:",
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_NORMAL)
        ).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.ip_var = tk.StringVar()
        self.ip_entry = tk.Entry(
            main_frame,
            textvariable=self.ip_var,
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_NORMAL),
            width=30
        )
        self.ip_entry.grid(row=0, column=1, pady=5, padx=(10, 0))
        self.ip_entry.focus_set()
        
        # Port
        tk.Label(
            main_frame,
            text="Port:",
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_NORMAL)
        ).grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.port_var = tk.StringVar(value="27015")
        self.port_entry = tk.Entry(
            main_frame,
            textvariable=self.port_var,
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_NORMAL),
            width=30
        )
        self.port_entry.grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Validation label
        self.validation_label = tk.Label(
            main_frame,
            text="",
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_SMALL),
            fg=Colors.ERROR
        )
        self.validation_label.grid(row=2, column=0, columnspan=2, pady=5)
        
        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(20, 0))
        
        self.ok_btn = tk.Button(
            button_frame,
            text="Add",
            command=self.on_ok,
            width=10,
            bg=Colors.SUCCESS,
            fg=Colors.TEXT_WHITE,
            relief=tk.FLAT
        )
        self.ok_btn.pack(side=tk.LEFT, padx=5)
        
        self.cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self.on_cancel,
            width=10,
            relief=tk.FLAT,
            bg=Colors.BG_TERTIARY
        )
        self.cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Bind Enter and Escape
        self.bind("<Return>", lambda e: self.on_ok())
        self.bind("<Escape>", lambda e: self.on_cancel())
    
    def validate(self) -> bool:
        """Validate input fields."""
        ip = self.ip_var.get().strip()
        port_str = self.port_var.get().strip()
        
        if not ip:
            self.validation_label.config(text="IP address is required")
            return False
        
        if not port_str:
            self.validation_label.config(text="Port is required")
            return False
        
        try:
            port = int(port_str)
            if not (1 <= port <= 65535):
                self.validation_label.config(text="Port must be between 1 and 65535")
                return False
        except ValueError:
            self.validation_label.config(text="Port must be a number")
            return False
        
        # Basic IP validation (simplified)
        parts = ip.split(".")
        if len(parts) != 4:
            self.validation_label.config(text="Invalid IP address format")
            return False
        
        for part in parts:
            try:
                num = int(part)
                if not (0 <= num <= 255):
                    self.validation_label.config(text="Invalid IP address")
                    return False
            except ValueError:
                self.validation_label.config(text="Invalid IP address")
                return False
        
        self.validation_label.config(text="")
        return True
    
    def on_ok(self):
        """OK button clicked."""
        if self.validate():
            ip = self.ip_var.get().strip()
            port = int(self.port_var.get().strip())
            self.result = (ip, port)
            self.destroy()
    
    def on_cancel(self):
        """Cancel button clicked."""
        self.result = None
        self.destroy()
    
    def show(self) -> Optional[Tuple[str, int]]:
        """Show dialog and return result."""
        self.wait_window()
        return self.result


class ConfigEditorDialog(tk.Toplevel):
    """
    Dialog for editing configuration settings.
    """
    
    def __init__(self, parent, config_data: dict):
        super().__init__(parent)
        
        self.title("Configuration Editor")
        self.geometry("600x500")
        self.resizable(True, True)
        
        # Center the dialog
        self.transient(parent)
        self.grab_set()
        
        self.config_data = config_data.copy()
        self.result = None
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Network settings tab
        network_frame = tk.Frame(notebook, padx=20, pady=20)
        notebook.add(network_frame, text="Network")
        
        row = 0
        tk.Label(network_frame, text="Host:", font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_NORMAL)).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.host_var = tk.StringVar(value=config_data.get("HOST", "0.0.0.0"))
        tk.Entry(network_frame, textvariable=self.host_var, width=30).grid(
            row=row, column=1, pady=5, padx=(10, 0), sticky=tk.W
        )
        
        row += 1
        tk.Label(network_frame, text="Port:", font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_NORMAL)).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.port_var = tk.StringVar(value=config_data.get("PORTGS", "27010"))
        tk.Entry(network_frame, textvariable=self.port_var, width=30).grid(
            row=row, column=1, pady=5, padx=(10, 0), sticky=tk.W
        )
        
        # Behavior settings tab
        behavior_frame = tk.Frame(notebook, padx=20, pady=20)
        notebook.add(behavior_frame, text="Behavior")
        
        row = 0
        tk.Label(behavior_frame, text="Mode:", font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_NORMAL)).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.mode_var = tk.StringVar(value=config_data.get("MODE", "file"))
        tk.Entry(behavior_frame, textvariable=self.mode_var, width=30, state="readonly").grid(
            row=row, column=1, pady=5, padx=(10, 0), sticky=tk.W
        )
        
        row += 1
        tk.Label(behavior_frame, text="Refresh Interval (s):", font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_NORMAL)).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.refresh_var = tk.StringVar(value=config_data.get("REFRESH", "60"))
        tk.Entry(behavior_frame, textvariable=self.refresh_var, width=30).grid(
            row=row, column=1, pady=5, padx=(10, 0), sticky=tk.W
        )
        
        row += 1
        self.noping_var = tk.BooleanVar(value=config_data.get("NOPING", "0") == "1")
        tk.Checkbutton(
            behavior_frame,
            text="No Ping (omit trailing zero bytes)",
            variable=self.noping_var
        ).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        row += 1
        self.randomize_var = tk.BooleanVar(value=config_data.get("RANDOM", "0") == "1")
        tk.Checkbutton(
            behavior_frame,
            text="Randomize server list",
            variable=self.randomize_var
        ).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # GeoIP settings tab
        geoip_frame = tk.Frame(notebook, padx=20, pady=20)
        notebook.add(geoip_frame, text="GeoIP")
        
        row = 0
        self.geoip_enabled_var = tk.BooleanVar(value=config_data.get("ENABLE", "1") == "1")
        tk.Checkbutton(
            geoip_frame,
            text="Enable GeoIP lookups",
            variable=self.geoip_enabled_var
        ).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        row += 1
        tk.Label(geoip_frame, text="Database Path:", font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_NORMAL)).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        
        db_frame = tk.Frame(geoip_frame)
        db_frame.grid(row=row, column=1, pady=5, padx=(10, 0), sticky=tk.W)
        
        self.db_path_var = tk.StringVar(value=config_data.get("DB_PATH", "GeoLite2-Country.mmdb"))
        tk.Entry(db_frame, textvariable=self.db_path_var, width=25).pack(side=tk.LEFT)
        tk.Button(
            db_frame,
            text="Browse",
            command=self.browse_database,
            relief=tk.FLAT,
            bg=Colors.BG_TERTIARY
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Logging settings tab
        logging_frame = tk.Frame(notebook, padx=20, pady=20)
        notebook.add(logging_frame, text="Logging")
        
        row = 0
        self.log_once_var = tk.BooleanVar(value=config_data.get("ONCE_PER_IP", "1") == "1")
        tk.Checkbutton(
            logging_frame,
            text="Log each IP only once",
            variable=self.log_once_var
        ).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        row += 1
        tk.Label(logging_frame, text="Throttle Seconds:", font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_NORMAL)).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.throttle_var = tk.StringVar(value=config_data.get("THROTTLE_SECONDS", "10"))
        tk.Entry(logging_frame, textvariable=self.throttle_var, width=30).grid(
            row=row, column=1, pady=5, padx=(10, 0), sticky=tk.W
        )
        tk.Label(
            logging_frame,
            text="(Used when 'Log once' is disabled)",
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_SMALL),
            fg=Colors.TEXT_SECONDARY
        ).grid(row=row+1, column=0, columnspan=2, sticky=tk.W, pady=0)
        
        # Buttons
        button_frame = tk.Frame(self)
        button_frame.pack(side=tk.BOTTOM, pady=10)
        
        tk.Button(
            button_frame,
            text="Save",
            command=self.on_save,
            width=10,
            bg=Colors.SUCCESS,
            fg=Colors.TEXT_WHITE,
            relief=tk.FLAT
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Cancel",
            command=self.on_cancel,
            width=10,
            relief=tk.FLAT,
            bg=Colors.BG_TERTIARY
        ).pack(side=tk.LEFT, padx=5)
        
        # Bind Escape
        self.bind("<Escape>", lambda e: self.on_cancel())
    
    def browse_database(self):
        """Browse for GeoIP database file."""
        filename = filedialog.askopenfilename(
            parent=self,
            title="Select GeoIP Database",
            filetypes=[("MaxMind DB", "*.mmdb"), ("All Files", "*.*")]
        )
        if filename:
            self.db_path_var.set(filename)
    
    def on_save(self):
        """Save button clicked."""
        self.result = {
            "HOST": self.host_var.get(),
            "PORTGS": self.port_var.get(),
            "MODE": self.mode_var.get(),
            "REFRESH": self.refresh_var.get(),
            "NOPING": "1" if self.noping_var.get() else "0",
            "RANDOM": "1" if self.randomize_var.get() else "0",
            "ENABLE": "1" if self.geoip_enabled_var.get() else "0",
            "DB_PATH": self.db_path_var.get(),
            "ONCE_PER_IP": "1" if self.log_once_var.get() else "0",
            "THROTTLE_SECONDS": self.throttle_var.get(),
        }
        self.destroy()
    
    def on_cancel(self):
        """Cancel button clicked."""
        self.result = None
        self.destroy()
    
    def show(self) -> Optional[dict]:
        """Show dialog and return result."""
        self.wait_window()
        return self.result


class AboutDialog(tk.Toplevel):
    """
    About dialog showing application information.
    """
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.title("About CS 1.6 Master Server")
        self.geometry("450x400")
        self.resizable(False, False)
        
        # Center the dialog
        self.transient(parent)
        self.grab_set()
        
        main_frame = tk.Frame(self, padx=30, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Icon/Title
        title_label = tk.Label(
            main_frame,
            text=f"{Icons.SERVER} CS 1.6 Master Server",
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_HEADER, Fonts.WEIGHT_BOLD),
            fg=Colors.PRIMARY
        )
        title_label.pack(pady=(0, 10))
        
        # Version
        version_label = tk.Label(
            main_frame,
            text="Version 2.0 - GUI Edition",
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_MEDIUM)
        )
        version_label.pack(pady=5)
        
        # Description
        desc_text = """
A modern, feature-rich master server for Counter-Strike 1.6
with real-time statistics, GeoIP support, and an intuitive
graphical interface.

Features:
• Real-time request monitoring
• GeoIP country detection
• Interactive server management
• Live statistics dashboard
• Color-coded console logs
        """
        desc_label = tk.Label(
            main_frame,
            text=desc_text.strip(),
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_NORMAL),
            justify=tk.LEFT,
            fg=Colors.TEXT_SECONDARY
        )
        desc_label.pack(pady=15)
        
        # Credits
        credits_label = tk.Label(
            main_frame,
            text="© 2025 | Python + Tkinter",
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_SMALL),
            fg=Colors.TEXT_DISABLED
        )
        credits_label.pack(pady=10)
        
        # Close button
        close_btn = tk.Button(
            main_frame,
            text="Close",
            command=self.destroy,
            width=10,
            relief=tk.FLAT,
            bg=Colors.PRIMARY,
            fg=Colors.TEXT_WHITE
        )
        close_btn.pack(pady=(10, 0))
        
        # Bind Escape
        self.bind("<Escape>", lambda e: self.destroy())


def show_error(parent, title: str, message: str):
    """Show an error message dialog."""
    messagebox.showerror(title, message, parent=parent)


def show_warning(parent, title: str, message: str):
    """Show a warning message dialog."""
    messagebox.showwarning(title, message, parent=parent)


def show_info(parent, title: str, message: str):
    """Show an information message dialog."""
    messagebox.showinfo(title, message, parent=parent)


def show_question(parent, title: str, message: str) -> bool:
    """Show a yes/no question dialog."""
    return messagebox.askyesno(title, message, parent=parent)


def save_file_dialog(parent, title: str = "Save File", filetypes=None) -> Optional[str]:
    """Show a save file dialog."""
    if filetypes is None:
        filetypes = [("Text Files", "*.txt"), ("All Files", "*.*")]
    return filedialog.asksaveasfilename(parent=parent, title=title, filetypes=filetypes)


def open_file_dialog(parent, title: str = "Open File", filetypes=None) -> Optional[str]:
    """Show an open file dialog."""
    if filetypes is None:
        filetypes = [("Text Files", "*.txt"), ("All Files", "*.*")]
    return filedialog.askopenfilename(parent=parent, title=title, filetypes=filetypes)




