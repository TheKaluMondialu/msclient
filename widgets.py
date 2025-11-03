#!/usr/bin/env python3
"""
Custom reusable widgets for CS 1.6 Master Server GUI.
Includes stat cards, log viewer, server table, and status indicators.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Optional, Callable, List, Tuple
from theme import Colors, Fonts, Layout, LogColors, Icons


# Try to import customtkinter for modern widgets
try:
    import customtkinter as ctk
    HAS_CTK = True
except ImportError:
    HAS_CTK = False
    ctk = None


class StatCard(tk.Frame):
    """
    A card widget displaying a statistic with label and value.
    """
    
    def __init__(self, parent, title: str, initial_value: str = "0", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.configure(
            bg=Colors.BG_SECONDARY,
            relief=tk.RAISED,
            borderwidth=1,
            padx=Layout.PADDING_MEDIUM,
            pady=Layout.PADDING_MEDIUM
        )
        
        # Title label
        self.title_label = tk.Label(
            self,
            text=title,
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_SMALL),
            fg=Colors.TEXT_SECONDARY,
            bg=Colors.BG_SECONDARY
        )
        self.title_label.pack(side=tk.TOP, anchor=tk.W)
        
        # Value label
        self.value_label = tk.Label(
            self,
            text=initial_value,
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_DISPLAY, Fonts.WEIGHT_BOLD),
            fg=Colors.TEXT_PRIMARY,
            bg=Colors.BG_SECONDARY
        )
        self.value_label.pack(side=tk.TOP, anchor=tk.W, pady=(5, 0))
    
    def set_value(self, value: str):
        """Update the displayed value."""
        self.value_label.config(text=str(value))
    
    def set_color(self, color: str):
        """Update the value color."""
        self.value_label.config(fg=color)


class ColoredLogViewer(tk.Frame):
    """
    A log viewer widget with color-coded messages and search functionality.
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Toolbar
        toolbar = tk.Frame(self, bg=Colors.BG_SECONDARY, height=Layout.TOOLBAR_HEIGHT)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Auto-scroll checkbox
        self.auto_scroll_var = tk.BooleanVar(value=True)
        self.auto_scroll_check = tk.Checkbutton(
            toolbar,
            text="Auto-scroll",
            variable=self.auto_scroll_var,
            bg=Colors.BG_SECONDARY
        )
        self.auto_scroll_check.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        self.clear_btn = tk.Button(
            toolbar,
            text=f"{Icons.CLEAR} Clear",
            command=self.clear_logs,
            relief=tk.FLAT,
            bg=Colors.BG_TERTIARY,
            activebackground=Colors.BG_DARK
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Export button
        self.export_btn = tk.Button(
            toolbar,
            text=f"{Icons.EXPORT} Export",
            command=self.export_logs,
            relief=tk.FLAT,
            bg=Colors.BG_TERTIARY,
            activebackground=Colors.BG_DARK
        )
        self.export_btn.pack(side=tk.LEFT, padx=5)
        
        # Search entry
        tk.Label(toolbar, text="Search:", bg=Colors.BG_SECONDARY).pack(side=tk.LEFT, padx=(20, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.highlight_search())
        self.search_entry = tk.Entry(toolbar, textvariable=self.search_var, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        # Text widget with scrollbar
        text_frame = tk.Frame(self)
        text_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.text_widget = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            font=(Fonts.FAMILY_MONO, Fonts.SIZE_NORMAL),
            bg=Colors.BG_PRIMARY,
            fg=Colors.TEXT_PRIMARY,
            relief=tk.SUNKEN,
            borderwidth=1
        )
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure color tags
        self.text_widget.tag_config("INFO", foreground=LogColors.INFO)
        self.text_widget.tag_config("WARNING", foreground=LogColors.WARNING)
        self.text_widget.tag_config("ERROR", foreground=LogColors.ERROR)
        self.text_widget.tag_config("SUCCESS", foreground=LogColors.SUCCESS)
        self.text_widget.tag_config("PLAYER", foreground=LogColors.PLAYER)
        self.text_widget.tag_config("DEBUG", foreground=LogColors.DEBUG)
        self.text_widget.tag_config("TIMESTAMP", foreground=LogColors.TIMESTAMP)
        self.text_widget.tag_config("HIGHLIGHT", background=Colors.HIGHLIGHT)
        
        self.log_buffer = []
        self.export_callback: Optional[Callable] = None
    
    def add_log(self, level: str, message: str, timestamp: Optional[str] = None):
        """Add a log message with color coding."""
        self.text_widget.config(state=tk.NORMAL)
        
        # Add to buffer
        log_entry = f"[{level}] {message}"
        if timestamp:
            log_entry = f"{timestamp} {log_entry}"
        self.log_buffer.append(log_entry)
        
        # Insert with color tag
        if timestamp:
            self.text_widget.insert(tk.END, timestamp + " ", "TIMESTAMP")
        
        self.text_widget.insert(tk.END, f"[{level}] ", level)
        self.text_widget.insert(tk.END, message + "\n")
        
        self.text_widget.config(state=tk.DISABLED)
        
        # Auto-scroll if enabled
        if self.auto_scroll_var.get():
            self.text_widget.see(tk.END)
    
    def clear_logs(self):
        """Clear all log messages."""
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.config(state=tk.DISABLED)
        self.log_buffer.clear()
    
    def export_logs(self):
        """Export logs to file."""
        if self.export_callback:
            self.export_callback(self.log_buffer)
    
    def highlight_search(self):
        """Highlight search terms in the log."""
        self.text_widget.tag_remove("HIGHLIGHT", 1.0, tk.END)
        
        search_term = self.search_var.get()
        if not search_term:
            return
        
        self.text_widget.config(state=tk.NORMAL)
        start_pos = "1.0"
        while True:
            start_pos = self.text_widget.search(search_term, start_pos, tk.END, nocase=True)
            if not start_pos:
                break
            end_pos = f"{start_pos}+{len(search_term)}c"
            self.text_widget.tag_add("HIGHLIGHT", start_pos, end_pos)
            start_pos = end_pos
        self.text_widget.config(state=tk.DISABLED)


class ServerTable(tk.Frame):
    """
    An interactive table for managing server list.
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Toolbar
        toolbar = tk.Frame(self, bg=Colors.BG_SECONDARY, height=Layout.TOOLBAR_HEIGHT)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Buttons
        self.add_btn = tk.Button(
            toolbar,
            text=f"{Icons.ADD} Add Server",
            command=self.on_add,
            relief=tk.FLAT,
            bg=Colors.SUCCESS,
            fg=Colors.TEXT_WHITE,
            activebackground=Colors.SUCCESS_DARK
        )
        self.add_btn.pack(side=tk.LEFT, padx=5)
        
        self.remove_btn = tk.Button(
            toolbar,
            text=f"{Icons.REMOVE} Remove",
            command=self.on_remove,
            relief=tk.FLAT,
            bg=Colors.ERROR,
            fg=Colors.TEXT_WHITE,
            activebackground=Colors.ERROR_DARK
        )
        self.remove_btn.pack(side=tk.LEFT, padx=5)
        
        self.refresh_btn = tk.Button(
            toolbar,
            text=f"{Icons.RELOAD} Refresh",
            command=self.on_refresh,
            relief=tk.FLAT,
            bg=Colors.BG_TERTIARY,
            activebackground=Colors.BG_DARK
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        
        self.import_btn = tk.Button(
            toolbar,
            text=f"{Icons.IMPORT} Import",
            command=self.on_import,
            relief=tk.FLAT,
            bg=Colors.BG_TERTIARY,
            activebackground=Colors.BG_DARK
        )
        self.import_btn.pack(side=tk.LEFT, padx=5)
        
        self.export_btn = tk.Button(
            toolbar,
            text=f"{Icons.EXPORT} Export",
            command=self.on_export,
            relief=tk.FLAT,
            bg=Colors.BG_TERTIARY,
            activebackground=Colors.BG_DARK
        )
        self.export_btn.pack(side=tk.LEFT, padx=5)
        
        # Search
        tk.Label(toolbar, text="Filter:", bg=Colors.BG_SECONDARY).pack(side=tk.LEFT, padx=(20, 5))
        self.filter_var = tk.StringVar()
        self.filter_var.trace("w", lambda *args: self.apply_filter())
        self.filter_entry = tk.Entry(toolbar, textvariable=self.filter_var, width=20)
        self.filter_entry.pack(side=tk.LEFT, padx=5)
        
        # Treeview with scrollbar
        tree_frame = tk.Frame(self)
        tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("IP", "Port", "Status"),
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Configure columns
        self.tree.heading("IP", text="IP Address")
        self.tree.heading("Port", text="Port")
        self.tree.heading("Status", text="Status")
        
        self.tree.column("IP", width=200)
        self.tree.column("Port", width=80)
        self.tree.column("Status", width=100)
        
        # Callbacks
        self.add_callback: Optional[Callable] = None
        self.remove_callback: Optional[Callable] = None
        self.refresh_callback: Optional[Callable] = None
        self.import_callback: Optional[Callable] = None
        self.export_callback: Optional[Callable] = None
        
        self.all_servers = []  # Store all servers for filtering
    
    def load_servers(self, servers: List[Tuple[str, int]]):
        """Load servers into the table."""
        self.all_servers = servers
        self.refresh_display()
    
    def refresh_display(self):
        """Refresh the table display."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Apply filter
        filter_text = self.filter_var.get().lower()
        for ip, port in self.all_servers:
            if filter_text and filter_text not in ip.lower() and filter_text not in str(port):
                continue
            self.tree.insert("", tk.END, values=(ip, port, "Active"))
    
    def apply_filter(self):
        """Apply the current filter."""
        self.refresh_display()
    
    def get_selected(self) -> List[Tuple[str, int]]:
        """Get selected servers."""
        selected = []
        for item in self.tree.selection():
            values = self.tree.item(item)["values"]
            if len(values) >= 2:
                selected.append((values[0], int(values[1])))
        return selected
    
    def on_add(self):
        """Add button clicked."""
        if self.add_callback:
            self.add_callback()
    
    def on_remove(self):
        """Remove button clicked."""
        selected = self.get_selected()
        if self.remove_callback and selected:
            self.remove_callback(selected)
    
    def on_refresh(self):
        """Refresh button clicked."""
        if self.refresh_callback:
            self.refresh_callback()
    
    def on_import(self):
        """Import button clicked."""
        if self.import_callback:
            self.import_callback()
    
    def on_export(self):
        """Export button clicked."""
        if self.export_callback:
            self.export_callback()


class StatusIndicator(tk.Frame):
    """
    A visual status indicator with colored circle and text.
    """
    
    def __init__(self, parent, initial_status: str = "Stopped", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.configure(bg=Colors.BG_SECONDARY)
        
        # Canvas for colored circle
        self.canvas = tk.Canvas(
            self,
            width=16,
            height=16,
            bg=Colors.BG_SECONDARY,
            highlightthickness=0
        )
        self.canvas.pack(side=tk.LEFT, padx=(0, 5))
        
        self.circle = self.canvas.create_oval(2, 2, 14, 14, fill=Colors.TEXT_DISABLED, outline="")
        
        # Status label
        self.label = tk.Label(
            self,
            text=initial_status,
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_NORMAL, Fonts.WEIGHT_BOLD),
            fg=Colors.TEXT_PRIMARY,
            bg=Colors.BG_SECONDARY
        )
        self.label.pack(side=tk.LEFT)
        
        self.status_colors = {
            "stopped": Colors.TEXT_DISABLED,
            "starting": Colors.WARNING,
            "running": Colors.SUCCESS,
            "stopping": Colors.WARNING,
            "error": Colors.ERROR,
        }
    
    def set_status(self, status: str):
        """Update the status indicator."""
        self.label.config(text=status.title())
        color = self.status_colors.get(status.lower(), Colors.TEXT_DISABLED)
        self.canvas.itemconfig(self.circle, fill=color)


class ChartWidget(tk.Frame):
    """
    A simple chart widget for displaying statistics.
    Falls back to text display if matplotlib is not available.
    """
    
    def __init__(self, parent, title: str = "Chart", chart_type: str = "line", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.title = title
        self.chart_type = chart_type
        self.data = []
        
        # Try to use matplotlib
        self.has_matplotlib = False
        self.Figure = None
        self.FigureCanvasTkAgg = None
        
        try:
            import sys
            import os
            # Make sure vendor is in path
            vendor_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor")
            if os.path.exists(vendor_dir) and vendor_dir not in sys.path:
                sys.path.insert(0, vendor_dir)
            
            import matplotlib
            matplotlib.use('TkAgg')
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            
            self.Figure = Figure
            self.FigureCanvasTkAgg = FigureCanvasTkAgg
            self.has_matplotlib = True
            
            # Create figure
            self.figure = Figure(figsize=(5, 3), dpi=80, facecolor=Colors.BG_SECONDARY)
            self.subplot = self.figure.add_subplot(111)
            self.subplot.set_title(title, fontsize=10, color=Colors.TEXT_PRIMARY)
            self.subplot.set_facecolor(Colors.BG_PRIMARY)
            
            # Create canvas
            self.canvas = FigureCanvasTkAgg(self.figure, self)
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            print(f"[INFO] Chart widget '{title}' initialized with matplotlib")
            
        except Exception as e:
            print(f"[WARNING] matplotlib not available for '{title}': {e}")
            # Fallback to text display
            self.text_label = tk.Label(
                self,
                text=f"{title}\n(Matplotlib not available)\nData will show as text",
                font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_SMALL),
                fg=Colors.TEXT_SECONDARY,
                bg=Colors.BG_SECONDARY,
                justify=tk.CENTER
            )
            self.text_label.pack(fill=tk.BOTH, expand=True)
    
    def update_data(self, data: List, labels: Optional[List] = None):
        """Update chart data."""
        self.data = data
        
        if not self.has_matplotlib:
            # Update text display
            if hasattr(self, 'text_label'):
                summary = f"{self.title}\n\n"
                if data and len(data) > 0:
                    summary += f"Latest: {data[-1] if data else 0}\n"
                    summary += f"Max: {max(data) if data else 0}\n"
                    summary += f"Avg: {sum(data)/len(data) if data else 0:.1f}\n"
                    summary += f"Count: {len(data)}"
                else:
                    summary += "No data yet\n(Start server to see activity)"
                self.text_label.config(text=summary)
            return
        
        try:
            # Clear and redraw
            self.subplot.clear()
            self.subplot.set_title(self.title, fontsize=10, color=Colors.TEXT_PRIMARY)
            self.subplot.set_facecolor(Colors.BG_PRIMARY)
            
            # Only draw if we have data
            if not data or len(data) == 0:
                self.subplot.text(0.5, 0.5, 'No data yet\nStart server to see activity',
                                ha='center', va='center', transform=self.subplot.transAxes,
                                fontsize=9, color=Colors.TEXT_SECONDARY)
            elif self.chart_type == "line":
                self.subplot.plot(data, color=Colors.PRIMARY, linewidth=2)
                self.subplot.fill_between(range(len(data)), data, alpha=0.3, color=Colors.PRIMARY_LIGHT)
            elif self.chart_type == "bar" and labels:
                bars = self.subplot.bar(range(len(data)), data, color=Colors.PRIMARY)
                if labels and len(labels) == len(data):
                    self.subplot.set_xticks(range(len(labels)))
                    # Limit label length for readability
                    short_labels = [lbl[:12] + '...' if len(lbl) > 12 else lbl for lbl in labels]
                    self.subplot.set_xticklabels(short_labels, rotation=45, ha='right', fontsize=8)
            
            self.subplot.grid(True, alpha=0.2, linestyle='--', linewidth=0.5)
            self.subplot.tick_params(labelsize=8)
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            print(f"[ERROR] Chart update error: {e}")
            # Show error in chart
            if hasattr(self, 'subplot'):
                self.subplot.clear()
                self.subplot.text(0.5, 0.5, f'Chart error:\n{str(e)[:50]}',
                                ha='center', va='center', transform=self.subplot.transAxes,
                                fontsize=8, color=Colors.ERROR)

