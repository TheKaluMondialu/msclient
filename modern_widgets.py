#!/usr/bin/env python3
"""
Modern enhanced widgets for CS 1.6 Master Server GUI.
Includes new functionality and improved design.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, List, Tuple
from theme import Colors, Fonts, Layout
import threading
import time


class ModernCard(tk.Frame):
    """
    Modern card widget with shadow effect and hover state.
    """
    
    def __init__(self, parent, title: str = "", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.configure(
            bg=Colors.BG_CARD,
            relief=tk.FLAT,
            borderwidth=0,
            padx=Layout.PADDING_MEDIUM,
            pady=Layout.PADDING_MEDIUM
        )
        
        # Add visual depth with border
        self.configure(highlightbackground=Colors.BORDER_LIGHT, highlightthickness=1)
        
        if title:
            title_label = tk.Label(
                self,
                text=title,
                font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_MEDIUM, Fonts.WEIGHT_BOLD),
                fg=Colors.TEXT_PRIMARY,
                bg=Colors.BG_CARD,
                anchor=tk.W
            )
            title_label.pack(side=tk.TOP, fill=tk.X, pady=(0, Layout.PADDING_SMALL))


class ModernStatCard(tk.Frame):
    """
    Enhanced stat card with icon, gradient background, and trend indicator.
    """
    
    def __init__(self, parent, title: str, icon: str = "📊", color: str = Colors.PRIMARY, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.color = color
        self.configure(
            bg=color,
            relief=tk.FLAT,
            padx=Layout.PADDING_MEDIUM,
            pady=Layout.PADDING_MEDIUM
        )
        
        # Icon and title row
        header_frame = tk.Frame(self, bg=color)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        
        icon_label = tk.Label(
            header_frame,
            text=icon,
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_XLARGE),
            bg=color,
            fg=Colors.TEXT_WHITE
        )
        icon_label.pack(side=tk.LEFT, padx=(0, Layout.PADDING_SMALL))
        
        self.title_label = tk.Label(
            header_frame,
            text=title,
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_SMALL),
            fg=Colors.TEXT_WHITE,
            bg=color,
            anchor=tk.W
        )
        self.title_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Value label
        self.value_label = tk.Label(
            self,
            text="0",
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_HEADER, Fonts.WEIGHT_BOLD),
            fg=Colors.TEXT_WHITE,
            bg=color,
            anchor=tk.W
        )
        self.value_label.pack(side=tk.TOP, fill=tk.X, pady=(Layout.PADDING_SMALL, 0))
        
        # Trend indicator (optional)
        self.trend_label = tk.Label(
            self,
            text="",
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_TINY),
            fg=Colors.TEXT_WHITE,
            bg=color,
            anchor=tk.W
        )
        self.trend_label.pack(side=tk.TOP, fill=tk.X)
    
    def set_value(self, value: str, trend: str = ""):
        """Update the value and optional trend."""
        self.value_label.config(text=str(value))
        if trend:
            self.trend_label.config(text=trend)


class ServerTestDialog(tk.Toplevel):
    """
    Dialog for testing server connectivity.
    """
    
    def __init__(self, parent, server_list: List[Tuple[str, int]]):
        super().__init__(parent)
        
        self.title("Test Server Connectivity")
        self.geometry("600x400")
        self.transient(parent)
        self.grab_set()
        
        self.server_list = server_list
        self.results = {}
        self.testing = False
        
        # Header
        header = tk.Label(
            self,
            text="🔍 Testing Server Connectivity",
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_LARGE, Fonts.WEIGHT_BOLD),
            fg=Colors.TEXT_PRIMARY,
            bg=Colors.BG_PRIMARY
        )
        header.pack(pady=Layout.PADDING_MEDIUM)
        
        # Progress
        self.progress_label = tk.Label(
            self,
            text="Ready to test...",
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_NORMAL),
            fg=Colors.TEXT_SECONDARY
        )
        self.progress_label.pack(pady=Layout.PADDING_SMALL)
        
        self.progress_bar = ttk.Progressbar(
            self,
            mode='determinate',
            maximum=len(server_list)
        )
        self.progress_bar.pack(fill=tk.X, padx=Layout.PADDING_LARGE, pady=Layout.PADDING_SMALL)
        
        # Results area
        result_frame = tk.Frame(self)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=Layout.PADDING_MEDIUM, pady=Layout.PADDING_MEDIUM)
        
        scrollbar = tk.Scrollbar(result_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.result_text = tk.Text(
            result_frame,
            font=(Fonts.FAMILY_MONO, Fonts.SIZE_SMALL),
            yscrollcommand=scrollbar.set,
            wrap=tk.WORD
        )
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.result_text.yview)
        
        # Buttons
        button_frame = tk.Frame(self)
        button_frame.pack(pady=Layout.PADDING_MEDIUM)
        
        self.test_btn = tk.Button(
            button_frame,
            text="▶ Start Test",
            command=self.start_test,
            bg=Colors.SUCCESS,
            fg=Colors.TEXT_WHITE,
            relief=tk.FLAT,
            padx=Layout.PADDING_LARGE,
            pady=Layout.PADDING_SMALL
        )
        self.test_btn.pack(side=tk.LEFT, padx=Layout.PADDING_SMALL)
        
        tk.Button(
            button_frame,
            text="Close",
            command=self.destroy,
            relief=tk.FLAT,
            padx=Layout.PADDING_LARGE,
            pady=Layout.PADDING_SMALL
        ).pack(side=tk.LEFT, padx=Layout.PADDING_SMALL)
    
    def start_test(self):
        """Start testing servers."""
        if self.testing:
            return
        
        self.testing = True
        self.test_btn.config(state=tk.DISABLED)
        self.result_text.delete(1.0, tk.END)
        self.progress_bar['value'] = 0
        
        # Run test in thread
        thread = threading.Thread(target=self._test_servers, daemon=True)
        thread.start()
    
    def _test_servers(self):
        """Test each server (runs in thread)."""
        import socket
        
        for i, (ip, port) in enumerate(self.server_list):
            self.progress_label.config(text=f"Testing {ip}:{port}...")
            
            # Try to connect
            result = "❌ Offline"
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result_code = sock.connect_ex((ip, port))
                sock.close()
                
                if result_code == 0:
                    result = "✅ Online"
                else:
                    result = f"❌ Error ({result_code})"
            except Exception as e:
                result = f"❌ Failed ({str(e)[:20]})"
            
            # Update UI (must be done in main thread)
            self.after(0, self._update_result, ip, port, result)
            self.after(0, lambda: self.progress_bar.step(1))
            
            time.sleep(0.1)  # Small delay between tests
        
        self.after(0, self._test_complete)
    
    def _update_result(self, ip, port, result):
        """Update result text (runs in main thread)."""
        self.result_text.insert(tk.END, f"{ip}:{port} - {result}\n")
        self.result_text.see(tk.END)
    
    def _test_complete(self):
        """Test complete callback."""
        self.progress_label.config(text="✅ Test completed!")
        self.test_btn.config(state=tk.NORMAL, text="🔄 Test Again")
        self.testing = False


class QuickFilterBar(tk.Frame):
    """
    Quick filter bar with search and filter options.
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.configure(bg=Colors.BG_SECONDARY, pady=Layout.PADDING_SMALL)
        
        # Search box
        search_frame = tk.Frame(self, bg=Colors.BG_SECONDARY)
        search_frame.pack(side=tk.LEFT, padx=Layout.PADDING_MEDIUM)
        
        tk.Label(
            search_frame,
            text="🔍",
            bg=Colors.BG_SECONDARY,
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_NORMAL)
        ).pack(side=tk.LEFT, padx=(0, Layout.PADDING_TINY))
        
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_SMALL),
            width=25
        )
        self.search_entry.pack(side=tk.LEFT)
        
        # Filter buttons
        self.filter_frame = tk.Frame(self, bg=Colors.BG_SECONDARY)
        self.filter_frame.pack(side=tk.LEFT, padx=Layout.PADDING_MEDIUM)
        
        self.filters = {}
        self.create_filter_btn("All", "all", active=True)
        self.create_filter_btn("Enabled", "enabled")
        self.create_filter_btn("Disabled", "disabled")
        
        # Stats label
        self.stats_label = tk.Label(
            self,
            text="0 servers",
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_SMALL),
            fg=Colors.TEXT_SECONDARY,
            bg=Colors.BG_SECONDARY
        )
        self.stats_label.pack(side=tk.RIGHT, padx=Layout.PADDING_MEDIUM)
        
        # Callbacks
        self.on_search_callback: Optional[Callable] = None
        self.on_filter_callback: Optional[Callable] = None
        
        # Bind search
        self.search_var.trace("w", self._on_search)
    
    def create_filter_btn(self, text: str, filter_key: str, active: bool = False):
        """Create a filter button."""
        btn = tk.Button(
            self.filter_frame,
            text=text,
            command=lambda: self.set_filter(filter_key),
            relief=tk.FLAT,
            bg=Colors.PRIMARY if active else Colors.BG_TERTIARY,
            fg=Colors.TEXT_WHITE if active else Colors.TEXT_PRIMARY,
            padx=Layout.PADDING_MEDIUM,
            pady=Layout.PADDING_TINY,
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_SMALL)
        )
        btn.pack(side=tk.LEFT, padx=Layout.PADDING_TINY)
        self.filters[filter_key] = btn
        
        if active:
            self.active_filter = filter_key
    
    def set_filter(self, filter_key: str):
        """Set active filter."""
        # Update button colors
        for key, btn in self.filters.items():
            if key == filter_key:
                btn.config(bg=Colors.PRIMARY, fg=Colors.TEXT_WHITE)
            else:
                btn.config(bg=Colors.BG_TERTIARY, fg=Colors.TEXT_PRIMARY)
        
        self.active_filter = filter_key
        
        if self.on_filter_callback:
            self.on_filter_callback(filter_key)
    
    def _on_search(self, *args):
        """Search changed callback."""
        if self.on_search_callback:
            self.on_search_callback(self.search_var.get())
    
    def update_stats(self, total: int, filtered: int):
        """Update stats display."""
        if total == filtered:
            self.stats_label.config(text=f"{total} servers")
        else:
            self.stats_label.config(text=f"{filtered} of {total} servers")


class ModernButton(tk.Button):
    """
    Modern styled button with hover effect.
    """
    
    def __init__(self, parent, text: str, command: Callable = None, 
                 style: str = "primary", icon: str = "", **kwargs):
        
        # Style presets
        styles = {
            "primary": {
                "bg": Colors.PRIMARY,
                "fg": Colors.TEXT_WHITE,
                "hover_bg": Colors.PRIMARY_DARK
            },
            "success": {
                "bg": Colors.SUCCESS,
                "fg": Colors.TEXT_WHITE,
                "hover_bg": Colors.SUCCESS_DARK
            },
            "danger": {
                "bg": Colors.ERROR,
                "fg": Colors.TEXT_WHITE,
                "hover_bg": Colors.ERROR_DARK
            },
            "secondary": {
                "bg": Colors.BG_TERTIARY,
                "fg": Colors.TEXT_PRIMARY,
                "hover_bg": Colors.BG_DARK
            }
        }
        
        style_config = styles.get(style, styles["primary"])
        
        display_text = f"{icon} {text}" if icon else text
        
        super().__init__(
            parent,
            text=display_text,
            command=command,
            bg=style_config["bg"],
            fg=style_config["fg"],
            activebackground=style_config["hover_bg"],
            relief=tk.FLAT,
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_NORMAL),
            padx=Layout.PADDING_MEDIUM,
            pady=Layout.PADDING_SMALL,
            cursor="hand2",
            **kwargs
        )
        
        self.default_bg = style_config["bg"]
        self.hover_bg = style_config["hover_bg"]
        
        # Hover effects
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        """Mouse enter - show hover state."""
        self.config(bg=self.hover_bg)
    
    def _on_leave(self, event):
        """Mouse leave - restore normal state."""
        self.config(bg=self.default_bg)




