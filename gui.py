#!/usr/bin/env python3
"""
Main GUI application for CS 1.6 Master Server.
Provides a modern desktop interface with real-time monitoring and management.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import configparser
import os
import sys
from datetime import datetime
from typing import Optional, List, Tuple

# Import and call ensure_vendor_on_path FIRST before other imports
from ms import BASE_DIR, ensure_vendor_on_path
ensure_vendor_on_path()  # Make vendor modules available

# Try to import pystray for system tray support (optional)
try:
    import pystray
    from PIL import Image, ImageDraw
    HAS_SYSTRAY = True
except ImportError:
    HAS_SYSTRAY = False
    pystray = None

# Azure theme will be loaded via Tcl - no Python import needed
# Use simplified version that works without images
HAS_AZURE_THEME = os.path.exists(os.path.join(BASE_DIR, "azure_simple.tcl"))

# Import local modules
from ms import MasterServer
from stats import Statistics
from theme import Colors, Fonts, Layout, Icons, Status
from widgets import StatCard, ColoredLogViewer, ServerTable, StatusIndicator, ChartWidget
from modern_widgets import ModernStatCard, ModernButton, QuickFilterBar, ServerTestDialog, ModernCard
from server_discovery import ServerDiscoveryDialog
from dialogs import (
    AddServerDialog, ConfigEditorDialog, AboutDialog,
    show_error, show_warning, show_info, show_question,
    save_file_dialog, open_file_dialog
)


class MasterServerGUI:
    """
    Main GUI application for the CS 1.6 Master Server.
    """
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("CS 1.6 Master Server - Control Panel")
        self.root.geometry(f"{Layout.WINDOW_DEFAULT_WIDTH}x{Layout.WINDOW_DEFAULT_HEIGHT}")
        self.root.minsize(Layout.WINDOW_MIN_WIDTH, Layout.WINDOW_MIN_HEIGHT)
        
        # Server instance
        self.server: Optional[MasterServer] = None
        self.server_thread: Optional[threading.Thread] = None
        self.is_running = False
        
        # Update job IDs
        self.stats_update_job = None
        self.chart_update_job = None
        
        # System tray
        self.tray_icon = None
        self.tray_thread = None
        
        # Create UI
        self._create_header()
        self._create_tabs()
        self._create_control_panel()
        self._create_status_bar()
        
        # Initialize server in stopped state
        self._init_server()
        
        # Setup system tray if available
        if HAS_SYSTRAY:
            self._setup_system_tray()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Apply Azure theme AFTER window is fully created
        self.current_theme_mode = "light"  # Start with light theme
        self._theme_loaded = False
        if HAS_AZURE_THEME:
            self.root.after(100, self._apply_azure_theme)
        
        # Start update loops
        self._start_update_loops()
    
    def _create_header(self):
        """Create the header with title and status indicator."""
        header = tk.Frame(self.root, bg=Colors.PRIMARY, height=Layout.HEADER_HEIGHT)
        header.pack(side=tk.TOP, fill=tk.X)
        header.pack_propagate(False)
        
        # Title
        title = tk.Label(
            header,
            text=f"{Icons.SERVER} CS 1.6 Master Server",
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_HEADER, Fonts.WEIGHT_BOLD),
            fg=Colors.TEXT_WHITE,
            bg=Colors.PRIMARY
        )
        title.pack(side=tk.LEFT, padx=Layout.PADDING_LARGE)
        
        # Status indicator
        status_frame = tk.Frame(header, bg=Colors.PRIMARY)
        status_frame.pack(side=tk.RIGHT, padx=Layout.PADDING_LARGE)
        
        tk.Label(
            status_frame,
            text="Status:",
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_NORMAL),
            fg=Colors.TEXT_WHITE,
            bg=Colors.PRIMARY
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.status_indicator = StatusIndicator(status_frame, initial_status="Stopped")
        self.status_indicator.pack(side=tk.LEFT)
    
    def _create_tabs(self):
        """Create the tabbed interface."""
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self._create_dashboard_tab()
        self._create_serverlist_tab()
        self._create_console_tab()
        self._create_config_tab()
    
    def _create_dashboard_tab(self):
        """Create the dashboard tab with modern statistics."""
        dashboard = tk.Frame(self.notebook, bg=Colors.BG_SECONDARY)
        self.notebook.add(dashboard, text=f"{Icons.STATS} Dashboard")
        
        # Top stats cards - Modern colored cards
        cards_frame = tk.Frame(dashboard, bg=Colors.BG_SECONDARY)
        cards_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=8)
        
        # Create modern stat cards with icons and colors
        self.card_requests = ModernStatCard(cards_frame, "Total Requests", "📊", Colors.PRIMARY)
        self.card_requests.pack(side=tk.LEFT, padx=4, fill=tk.BOTH, expand=True)
        
        self.card_unique_ips = ModernStatCard(cards_frame, "Unique Players", "👥", Colors.ACCENT)
        self.card_unique_ips.pack(side=tk.LEFT, padx=4, fill=tk.BOTH, expand=True)
        
        self.card_rps = ModernStatCard(cards_frame, "Requests/sec", "⚡", Colors.SUCCESS)
        self.card_rps.pack(side=tk.LEFT, padx=4, fill=tk.BOTH, expand=True)
        
        self.card_uptime = ModernStatCard(cards_frame, "Uptime", "⏱️", Colors.WARNING)
        self.card_uptime.pack(side=tk.LEFT, padx=4, fill=tk.BOTH, expand=True)
        
        self.card_servers = ModernStatCard(cards_frame, "Active Servers", "🌐", Colors.INFO)
        self.card_servers.pack(side=tk.LEFT, padx=4, fill=tk.BOTH, expand=True)
        
        # Charts section
        charts_frame = tk.Frame(dashboard, bg=Colors.BG_PRIMARY)
        charts_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Request rate chart
        left_chart_frame = tk.Frame(charts_frame, bg=Colors.BG_SECONDARY, relief=tk.RAISED, borderwidth=1)
        left_chart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.chart_requests = ChartWidget(left_chart_frame, "Request Rate (60s)", "line")
        self.chart_requests.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top countries chart
        right_chart_frame = tk.Frame(charts_frame, bg=Colors.BG_SECONDARY, relief=tk.RAISED, borderwidth=1)
        right_chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.chart_countries = ChartWidget(right_chart_frame, "Top Countries", "bar")
        self.chart_countries.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def _create_serverlist_tab(self):
        """Create the modern server list management tab."""
        serverlist = tk.Frame(self.notebook, bg=Colors.BG_SECONDARY)
        self.notebook.add(serverlist, text=f"{Icons.NETWORK} Server List")
        
        # Quick filter bar
        self.filter_bar = QuickFilterBar(serverlist)
        self.filter_bar.pack(side=tk.TOP, fill=tk.X, padx=8, pady=8)
        self.filter_bar.on_search_callback = self._on_server_search
        self.filter_bar.on_filter_callback = self._on_server_filter
        
        # Enhanced toolbar with new actions
        toolbar_frame = tk.Frame(serverlist, bg=Colors.BG_PRIMARY)
        toolbar_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=(0, 8))
        
        # Left side buttons
        left_buttons = tk.Frame(toolbar_frame, bg=Colors.BG_PRIMARY)
        left_buttons.pack(side=tk.LEFT)
        
        ModernButton(left_buttons, "Add Server", self.on_add_server, "success", "➕").pack(side=tk.LEFT, padx=2)
        ModernButton(left_buttons, "Find Servers", self.on_find_servers, "primary", "🌐").pack(side=tk.LEFT, padx=2)
        ModernButton(left_buttons, "Remove", self.on_remove_servers_from_table, "danger", "➖").pack(side=tk.LEFT, padx=2)
        ModernButton(left_buttons, "Test All", self.on_test_servers, "secondary", "🔍").pack(side=tk.LEFT, padx=2)
        
        # Right side buttons
        right_buttons = tk.Frame(toolbar_frame, bg=Colors.BG_PRIMARY)
        right_buttons.pack(side=tk.RIGHT)
        
        ModernButton(right_buttons, "Import", self.on_import_servers, "secondary", "📥").pack(side=tk.LEFT, padx=2)
        ModernButton(right_buttons, "Export", self.on_export_servers_menu, "secondary", "📤").pack(side=tk.LEFT, padx=2)
        ModernButton(right_buttons, "Refresh", self.on_refresh_servers, "secondary", "🔄").pack(side=tk.LEFT, padx=2)
        
        # Server table
        self.server_table = ServerTable(serverlist)
        self.server_table.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
    
    def _create_console_tab(self):
        """Create the console log viewer tab."""
        console = tk.Frame(self.notebook, bg=Colors.BG_PRIMARY)
        self.notebook.add(console, text=f"{Icons.LOG} Console")
        
        # Log viewer
        self.log_viewer = ColoredLogViewer(console)
        self.log_viewer.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.log_viewer.export_callback = self.on_export_logs
        
        # Add welcome message
        self.log_viewer.add_log("INFO", "CS 1.6 Master Server GUI started")
        self.log_viewer.add_log("INFO", "Click 'Start Server' to begin serving")
    
    def _create_config_tab(self):
        """Create the configuration tab."""
        config = tk.Frame(self.notebook, bg=Colors.BG_PRIMARY)
        self.notebook.add(config, text=f"{Icons.SETTINGS} Configuration")
        
        # Info label
        info_label = tk.Label(
            config,
            text="Configuration settings are managed through the visual editor.\nChanges require a server restart to take effect.",
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_NORMAL),
            fg=Colors.TEXT_SECONDARY,
            bg=Colors.BG_PRIMARY,
            justify=tk.CENTER
        )
        info_label.pack(pady=30)
        
        # Edit button
        edit_btn = tk.Button(
            config,
            text=f"{Icons.EDIT} Edit Configuration",
            command=self.on_edit_config,
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_LARGE),
            bg=Colors.PRIMARY,
            fg=Colors.TEXT_WHITE,
            relief=tk.FLAT,
            padx=30,
            pady=15,
            cursor="hand2"
        )
        edit_btn.pack(pady=20)
        
        # Current config display
        config_frame = tk.Frame(config, bg=Colors.BG_SECONDARY, relief=tk.RAISED, borderwidth=1)
        config_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
        
        tk.Label(
            config_frame,
            text="Current Configuration",
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_MEDIUM, Fonts.WEIGHT_BOLD),
            bg=Colors.BG_SECONDARY,
            fg=Colors.TEXT_PRIMARY
        ).pack(pady=10)
        
        self.config_text = tk.Text(
            config_frame,
            font=(Fonts.FAMILY_MONO, Fonts.SIZE_NORMAL),
            bg=Colors.BG_PRIMARY,
            fg=Colors.TEXT_PRIMARY,
            relief=tk.FLAT,
            height=15,
            state=tk.DISABLED
        )
        self.config_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self._update_config_display()
    
    def _create_control_panel(self):
        """Create the control panel with start/stop button."""
        control = tk.Frame(self.root, bg=Colors.BG_SECONDARY, height=Layout.TOOLBAR_HEIGHT + 20)
        control.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        # Start/Stop button
        self.start_stop_btn = tk.Button(
            control,
            text=f"{Icons.START} Start Server",
            command=self.toggle_server,
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_LARGE, Fonts.WEIGHT_BOLD),
            bg=Colors.SUCCESS,
            fg=Colors.TEXT_WHITE,
            relief=tk.FLAT,
            padx=30,
            pady=10,
            cursor="hand2"
        )
        self.start_stop_btn.pack(side=tk.LEFT, padx=10)
        
        # Quick actions
        tk.Button(
            control,
            text=f"{Icons.RELOAD} Reload Servers",
            command=self.on_refresh_servers,
            relief=tk.FLAT,
            bg=Colors.BG_TERTIARY,
            padx=15,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            control,
            text=f"{Icons.CLEAR} Clear Logs",
            command=lambda: self.log_viewer.clear_logs(),
            relief=tk.FLAT,
            bg=Colors.BG_TERTIARY,
            padx=15,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            control,
            text=f"{Icons.ABOUT} About",
            command=self.show_about,
            relief=tk.FLAT,
            bg=Colors.BG_TERTIARY,
            padx=15,
            pady=10
        ).pack(side=tk.RIGHT, padx=5)
        
        # Theme toggle (if Azure theme available)
        if HAS_AZURE_THEME:
            theme_frame = tk.Frame(control, bg=Colors.BG_SECONDARY)
            theme_frame.pack(side=tk.RIGHT, padx=10)
            
            self.theme_toggle_btn = ModernButton(
                theme_frame,
                "🌙 Dark Mode",
                self.toggle_theme,
                "secondary"
            )
            self.theme_toggle_btn.pack(side=tk.LEFT)
    
    def _create_status_bar(self):
        """Create the status bar at the bottom."""
        self.status_bar = tk.Label(
            self.root,
            text="Ready",
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_SMALL),
            fg=Colors.TEXT_SECONDARY,
            bg=Colors.BG_TERTIARY,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padx=10
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _init_server(self):
        """Initialize the server instance."""
        try:
            ensure_vendor_on_path()
            self.server = MasterServer(gui_mode=True)
            
            # Register callbacks
            self.server.register_callback("on_log", self.on_server_log)
            self.server.register_callback("on_request", self.on_server_request)
            self.server.register_callback("on_server_loaded", self.on_servers_loaded)
            self.server.register_callback("on_error", self.on_server_error)
            self.server.register_callback("on_status_change", self.on_server_status_change)
            
            # Load initial server list
            self._refresh_server_list()
            
        except Exception as e:
            show_error(self.root, "Initialization Error", f"Failed to initialize server:\n{e}")
            self.log_viewer.add_log("ERROR", f"Initialization failed: {e}")
    
    def _start_update_loops(self):
        """Start the periodic update loops."""
        self._update_stats()
        self._update_charts()
    
    def _update_stats(self):
        """Update statistics display."""
        if self.server and self.server.stats:
            stats = self.server.stats
            
            # Update stat cards
            self.card_requests.set_value(f"{stats.total_requests:,}")
            self.card_unique_ips.set_value(f"{stats.get_unique_ip_count():,}")
            self.card_rps.set_value(f"{stats.get_current_rps():.2f}")
            self.card_uptime.set_value(stats.get_uptime_formatted())
            
            # Update server count
            servers = self.server.get_servers()
            self.card_servers.set_value(f"{len(servers):,}")
        
        # Schedule next update
        self.stats_update_job = self.root.after(1000, self._update_stats)
    
    def _update_charts(self):
        """Update chart displays."""
        try:
            if self.server and self.server.stats:
                stats = self.server.stats
                
                # Update request rate chart
                rate_history = stats.get_request_rate_history()
                if rate_history and len(rate_history) > 0:
                    self.chart_requests.update_data(rate_history)
                else:
                    # Show empty state
                    self.chart_requests.update_data([])
                
                # Update countries chart
                top_countries = stats.get_top_countries(10)
                if top_countries and len(top_countries) > 0:
                    countries = [c[0] if c[0] else "Unknown" for c in top_countries]
                    counts = [c[1] for c in top_countries]
                    self.chart_countries.update_data(counts, countries)
                else:
                    # Show empty state
                    self.chart_countries.update_data([], [])
            else:
                # No server or stats yet - show empty
                self.chart_requests.update_data([])
                self.chart_countries.update_data([], [])
        except Exception as e:
            print(f"[ERROR] Chart update error: {e}")
            import traceback
            traceback.print_exc()
        
        # Schedule next update
        self.chart_update_job = self.root.after(2000, self._update_charts)
    
    def _refresh_server_list(self):
        """Refresh the server list display."""
        if self.server:
            servers = self.server.get_servers()
            self.server_table.load_servers(servers)
            # Update filter bar stats if it exists
            if hasattr(self, 'filter_bar'):
                self._update_filter_stats()
    
    def _update_config_display(self):
        """Update the configuration display."""
        try:
            cfg_path = os.path.join(BASE_DIR, "ms.cfg")
            if os.path.exists(cfg_path):
                with open(cfg_path, "r", encoding="utf-8") as f:
                    config_content = f.read()
                
                self.config_text.config(state=tk.NORMAL)
                self.config_text.delete(1.0, tk.END)
                self.config_text.insert(1.0, config_content)
                self.config_text.config(state=tk.DISABLED)
        except Exception as e:
            self.log_viewer.add_log("ERROR", f"Failed to read config: {e}")
    
    # ==================== Server Control ====================
    
    def toggle_server(self):
        """Toggle server start/stop."""
        if self.is_running:
            self.stop_server()
        else:
            self.start_server()
    
    def start_server(self):
        """Start the master server."""
        if self.is_running:
            return
        
        try:
            self.log_viewer.add_log("INFO", "Starting server...")
            self.status_bar.config(text="Starting server...")
            
            # Re-initialize server to pick up config changes
            self._init_server()
            
            # Start server in separate thread
            self.server_thread = threading.Thread(target=self.server.run, daemon=True)
            self.server_thread.start()
            
            self.is_running = True
            self.start_stop_btn.config(
                text=f"{Icons.STOP} Stop Server",
                bg=Colors.ERROR,
                activebackground=Colors.ERROR_DARK
            )
            self.log_viewer.add_log("SUCCESS", "Server started successfully")
            
        except Exception as e:
            show_error(self.root, "Start Error", f"Failed to start server:\n{e}")
            self.log_viewer.add_log("ERROR", f"Failed to start server: {e}")
            self.is_running = False
    
    def stop_server(self):
        """Stop the master server."""
        if not self.is_running:
            return
        
        try:
            self.log_viewer.add_log("INFO", "Stopping server...")
            self.status_bar.config(text="Stopping server...")
            
            if self.server:
                self.server.stop()
            
            self.is_running = False
            self.start_stop_btn.config(
                text=f"{Icons.START} Start Server",
                bg=Colors.SUCCESS,
                activebackground=Colors.SUCCESS_DARK
            )
            self.log_viewer.add_log("SUCCESS", "Server stopped")
            self.status_bar.config(text="Server stopped")
            
        except Exception as e:
            show_error(self.root, "Stop Error", f"Failed to stop server:\n{e}")
            self.log_viewer.add_log("ERROR", f"Failed to stop server: {e}")
    
    # ==================== Callbacks ====================
    
    def on_server_log(self, level: str, message: str):
        """Handle server log messages."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_viewer.add_log(level, message, timestamp)
    
    def on_server_request(self, ip: str, country: str):
        """Handle server request event."""
        # Stats are already updated in the server
        pass
    
    def on_servers_loaded(self, count: int):
        """Handle servers loaded event."""
        self._refresh_server_list()
    
    def on_server_error(self, error_type: str, message: str):
        """Handle server error event."""
        self.log_viewer.add_log("ERROR", f"[{error_type}] {message}")
    
    def on_server_status_change(self, status: str):
        """Handle server status change."""
        self.status_indicator.set_status(status)
        self.status_bar.config(text=f"Server {status}")
    
    # ==================== Server List Management ====================
    
    def on_add_server(self):
        """Add a single new server."""
        dialog = AddServerDialog(self.root)
        result = dialog.show()
        
        if result:
            ip, port = result
            servers = self.server.get_servers()
            
            # Check for duplicates
            if (ip, port) in servers:
                show_warning(self.root, "Duplicate Server", f"Server {ip}:{port} already exists")
                return
            
            servers.append((ip, port))
            if self.server.save_servers(servers):
                self.log_viewer.add_log("SUCCESS", f"Added server {ip}:{port}")
                self._refresh_server_list()
                if self.is_running:
                    self.server.load_servers()
    
    def on_find_servers(self):
        """Open server discovery dialog."""
        try:
            dialog = ServerDiscoveryDialog(self.root, self.bulk_add_servers)
        except Exception as e:
            show_error(self.root, "Discovery Error", f"Could not open server discovery:\n{e}")
            self.log_viewer.add_log("ERROR", f"Server discovery error: {e}")
    
    def bulk_add_servers(self, new_servers: List[Tuple[str, int]]):
        """Bulk add servers from discovery dialog."""
        if not new_servers:
            return
        
        servers = self.server.get_servers()
        added = 0
        skipped = 0
        
        for ip, port in new_servers:
            if (ip, port) not in servers:
                servers.append((ip, port))
                added += 1
            else:
                skipped += 1
        
        if added > 0:
            if self.server.save_servers(servers):
                self.log_viewer.add_log("SUCCESS", f"Bulk added {added} servers (skipped {skipped} duplicates)")
                self._refresh_server_list()
                if self.is_running:
                    self.server.load_servers()
                show_info(self.root, "Success", f"Added {added} new servers!\nSkipped {skipped} duplicates.")
        else:
            show_info(self.root, "No New Servers", "All servers already exist in your list.")
    
    def on_remove_servers_from_table(self):
        """Remove selected servers from the table."""
        selected = self.server_table.get_selected()
        if not selected:
            show_warning(self.root, "No Selection", "Please select servers to remove")
            return
        
        self.on_remove_servers(selected)
    
    def on_remove_servers(self, selected: List[Tuple[str, int]]):
        """Remove selected servers."""
        if not selected:
            return
        
        count = len(selected)
        if not show_question(self.root, "Confirm Remove", f"Remove {count} server(s)?"):
            return
        
        servers = self.server.get_servers()
        for server in selected:
            if server in servers:
                servers.remove(server)
        
        if self.server.save_servers(servers):
            self.log_viewer.add_log("SUCCESS", f"Removed {count} server(s)")
            self._refresh_server_list()
            if self.is_running:
                self.server.load_servers()
    
    def on_refresh_servers(self):
        """Refresh server list from file."""
        if self.server:
            self.server.load_servers()
            self._refresh_server_list()
            self.log_viewer.add_log("INFO", "Server list refreshed")
    
    def on_import_servers(self):
        """Import servers from file."""
        filename = open_file_dialog(self.root, "Import Servers")
        if not filename:
            return
        
        try:
            with open(filename, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            imported = []
            for line in lines:
                parsed = self.server._parse_server_line(line)
                if parsed:
                    imported.append(parsed)
            
            if imported:
                servers = self.server.get_servers()
                servers.extend(imported)
                # Remove duplicates
                servers = list(set(servers))
                
                if self.server.save_servers(servers):
                    self.log_viewer.add_log("SUCCESS", f"Imported {len(imported)} server(s)")
                    self._refresh_server_list()
                    if self.is_running:
                        self.server.load_servers()
            else:
                show_warning(self.root, "Import Failed", "No valid servers found in file")
                
        except Exception as e:
            show_error(self.root, "Import Error", f"Failed to import servers:\n{e}")
    
    def on_export_servers_menu(self):
        """Show export menu with format options."""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="📄 Export as TXT", command=lambda: self.on_export_servers("txt"))
        menu.add_command(label="📊 Export as CSV", command=lambda: self.on_export_servers("csv"))
        menu.add_command(label="💾 Export as JSON", command=lambda: self.on_export_servers("json"))
        
        # Show menu at mouse position
        try:
            menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())
        finally:
            menu.grab_release()
    
    def on_export_servers(self, format_type="txt"):
        """Export servers to file in various formats."""
        filetypes = {
            "txt": [("Text Files", "*.txt"), ("All Files", "*.*")],
            "csv": [("CSV Files", "*.csv"), ("All Files", "*.*")],
            "json": [("JSON Files", "*.json"), ("All Files", "*.*")]
        }
        
        filename = save_file_dialog(self.root, f"Export Servers ({format_type.upper()})", filetypes.get(format_type, filetypes["txt"]))
        if not filename:
            return
        
        try:
            servers = self.server.get_servers()
            
            if format_type == "txt":
                with open(filename, "w", encoding="utf-8") as f:
                    f.write("# CS 1.6 Server List\n")
                    f.write("# Exported from Master Server GUI\n\n")
                    for ip, port in servers:
                        f.write(f"{ip}:{port}\n")
            
            elif format_type == "csv":
                import csv
                with open(filename, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["IP", "Port"])
                    for ip, port in servers:
                        writer.writerow([ip, port])
            
            elif format_type == "json":
                import json
                data = [{"ip": ip, "port": port} for ip, port in servers]
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
            
            self.log_viewer.add_log("SUCCESS", f"Exported {len(servers)} server(s) to {filename}")
            show_info(self.root, "Export Success", f"Exported {len(servers)} servers as {format_type.upper()}")
            
        except Exception as e:
            show_error(self.root, "Export Error", f"Failed to export servers:\n{e}")
    
    def on_test_servers(self):
        """Test server connectivity."""
        servers = self.server.get_servers()
        if not servers:
            show_warning(self.root, "No Servers", "No servers to test. Please add some servers first.")
            return
        
        try:
            # Show test dialog
            dialog = ServerTestDialog(self.root, servers)
        except Exception as e:
            show_error(self.root, "Test Error", f"Could not start server test:\n{e}")
            self.log_viewer.add_log("ERROR", f"Server test error: {e}")
    
    def _on_server_search(self, search_term: str):
        """Handle server search."""
        # This will be handled by the server table's filter
        self.server_table.filter_var.set(search_term)
        self._update_filter_stats()
    
    def _on_server_filter(self, filter_key: str):
        """Handle server filter change."""
        # Filter servers based on enabled/disabled/all
        # This functionality would need database support to track enabled/disabled state
        self._update_filter_stats()
    
    def _update_filter_stats(self):
        """Update filter bar statistics."""
        if hasattr(self, 'filter_bar') and hasattr(self, 'server_table'):
            total = len(self.server.get_servers())
            # Count visible items in tree
            visible = len(self.server_table.tree.get_children())
            self.filter_bar.update_stats(total, visible)
    
    def on_export_logs(self, logs: List[str]):
        """Export logs to file."""
        filename = save_file_dialog(self.root, "Export Logs", [("Log Files", "*.log"), ("Text Files", "*.txt")])
        if not filename:
            return
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write("# CS 1.6 Master Server Logs\n")
                f.write(f"# Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                for log in logs:
                    f.write(log + "\n")
            
            show_info(self.root, "Export Success", f"Exported {len(logs)} log entries")
            
        except Exception as e:
            show_error(self.root, "Export Error", f"Failed to export logs:\n{e}")
    
    # ==================== Configuration ====================
    
    def on_edit_config(self):
        """Open configuration editor."""
        # Read current config
        cfg = configparser.ConfigParser()
        cfg.read(os.path.join(BASE_DIR, "ms.cfg"), encoding="utf-8")
        
        config_data = {
            "HOST": cfg.get("OPTIONS", "HOST", fallback="0.0.0.0"),
            "PORTGS": cfg.get("OPTIONS", "PORTGS", fallback="27010"),
            "MODE": cfg.get("OPTIONS", "MODE", fallback="file"),
            "REFRESH": cfg.get("OPTIONS", "REFRESH", fallback="60"),
            "NOPING": cfg.get("OPTIONS", "NOPING", fallback="0"),
            "RANDOM": cfg.get("FILE", "RANDOM", fallback="0"),
            "ENABLE": cfg.get("GEOIP", "ENABLE", fallback="1"),
            "DB_PATH": cfg.get("GEOIP", "DB_PATH", fallback="GeoLite2-Country.mmdb"),
            "ONCE_PER_IP": cfg.get("LOG", "ONCE_PER_IP", fallback="1"),
            "THROTTLE_SECONDS": cfg.get("LOG", "THROTTLE_SECONDS", fallback="10"),
        }
        
        dialog = ConfigEditorDialog(self.root, config_data)
        result = dialog.show()
        
        if result:
            # Save config
            cfg.set("OPTIONS", "HOST", result["HOST"])
            cfg.set("OPTIONS", "PORTGS", result["PORTGS"])
            cfg.set("OPTIONS", "REFRESH", result["REFRESH"])
            cfg.set("OPTIONS", "NOPING", result["NOPING"])
            cfg.set("FILE", "RANDOM", result["RANDOM"])
            cfg.set("GEOIP", "ENABLE", result["ENABLE"])
            cfg.set("GEOIP", "DB_PATH", result["DB_PATH"])
            cfg.set("LOG", "ONCE_PER_IP", result["ONCE_PER_IP"])
            cfg.set("LOG", "THROTTLE_SECONDS", result["THROTTLE_SECONDS"])
            
            with open(os.path.join(BASE_DIR, "ms.cfg"), "w", encoding="utf-8") as f:
                cfg.write(f)
            
            self.log_viewer.add_log("SUCCESS", "Configuration saved")
            self._update_config_display()
            
            if self.is_running:
                show_info(self.root, "Restart Required", 
                         "Configuration saved. Please restart the server for changes to take effect.")
    
    # ==================== Other ====================
    
    def show_about(self):
        """Show about dialog."""
        AboutDialog(self.root)
    
    # ==================== Azure Theme ====================
    
    def _apply_azure_theme(self):
        """Apply the Azure ttk theme."""
        if not HAS_AZURE_THEME or self._theme_loaded:
            return
        
        try:
            # Load the simplified theme (no images required)
            azure_tcl_path = os.path.abspath(os.path.join(BASE_DIR, "azure_simple.tcl"))
            
            # Load the theme script
            self.root.tk.call("source", azure_tcl_path)
            self._theme_loaded = True
            
            # Set initial theme (light)
            self.root.tk.call("set_theme", self.current_theme_mode)
            
            self.log_viewer.add_log("SUCCESS", f"Applied Azure {self.current_theme_mode} theme ✨")
            print(f"[SUCCESS] Applied Azure {self.current_theme_mode} theme")
            
        except Exception as e:
            self.log_viewer.add_log("ERROR", f"Could not apply Azure theme: {e}")
            print(f"[ERROR] Azure theme error: {e}")
            self._theme_loaded = False
    
    def toggle_theme(self):
        """Toggle between light and dark theme."""
        if not HAS_AZURE_THEME or not self._theme_loaded:
            return
        
        try:
            # Toggle mode
            if self.current_theme_mode == "light":
                self.current_theme_mode = "dark"
                self.theme_toggle_btn.config(text="☀️ Light Mode")
            else:
                self.current_theme_mode = "light"
                self.theme_toggle_btn.config(text="🌙 Dark Mode")
            
            # Apply theme (just switch, don't reload)
            self.root.tk.call("set_theme", self.current_theme_mode)
            
            self.log_viewer.add_log("INFO", f"Switched to {self.current_theme_mode} theme")
            
        except Exception as e:
            self.log_viewer.add_log("ERROR", f"Could not toggle theme: {e}")
    
    # ==================== System Tray ====================
    
    def _setup_system_tray(self):
        """Setup system tray icon and menu."""
        if not HAS_SYSTRAY:
            return
        
        try:
            # Create a simple icon
            def create_icon():
                width = 64
                height = 64
                image = Image.new('RGB', (width, height), color=(30, 136, 229))
                dc = ImageDraw.Draw(image)
                # Draw a simple server icon (rectangle with lines)
                dc.rectangle([10, 10, 54, 54], outline='white', width=2)
                dc.line([20, 25, 44, 25], fill='white', width=2)
                dc.line([20, 35, 44, 35], fill='white', width=2)
                dc.line([20, 45, 44, 45], fill='white', width=2)
                return image
            
            # Create menu
            menu = pystray.Menu(
                pystray.MenuItem("Show", self._tray_show, default=True),
                pystray.MenuItem("Start Server" if not self.is_running else "Stop Server", self._tray_toggle_server),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("About", lambda: self.root.after(0, self.show_about)),
                pystray.MenuItem("Exit", self._tray_exit)
            )
            
            # Create icon
            self.tray_icon = pystray.Icon(
                "cs16_master_server",
                create_icon(),
                "CS 1.6 Master Server",
                menu
            )
            
            # Run in separate thread
            self.tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
            self.tray_thread.start()
            
        except Exception as e:
            print(f"System tray setup failed: {e}")
    
    def _tray_show(self):
        """Show main window from tray."""
        self.root.after(0, self._restore_window)
    
    def _restore_window(self):
        """Restore window from minimized/hidden state."""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
    
    def _tray_toggle_server(self):
        """Toggle server from tray."""
        self.root.after(0, self.toggle_server)
    
    def _tray_exit(self):
        """Exit application from tray."""
        self.root.after(0, self._force_exit)
    
    def _minimize_to_tray(self):
        """Minimize window to system tray."""
        if HAS_SYSTRAY and self.tray_icon:
            self.root.withdraw()
        else:
            self.root.iconify()
    
    # ==================== Window Management ====================
    
    def on_closing(self):
        """Handle window close event."""
        # If system tray is available and server is running, minimize to tray instead
        if HAS_SYSTRAY and self.is_running:
            if show_question(self.root, "Minimize to Tray?", 
                           "Server is running. Minimize to system tray?\n(Click 'No' to stop and exit)"):
                self._minimize_to_tray()
                return
        
        if self.is_running:
            if show_question(self.root, "Confirm Exit", "Server is running. Stop and exit?"):
                self.stop_server()
                self.root.after(500, self._cleanup_and_exit)
        else:
            self._cleanup_and_exit()
    
    def _force_exit(self):
        """Force exit without confirmation."""
        if self.is_running:
            self.stop_server()
        self.root.after(500, self._cleanup_and_exit)
    
    def _cleanup_and_exit(self):
        """Cleanup and exit application."""
        # Cancel update jobs
        if self.stats_update_job:
            self.root.after_cancel(self.stats_update_job)
        if self.chart_update_job:
            self.root.after_cancel(self.chart_update_job)
        
        # Stop system tray
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
        
        self.root.destroy()


def main():
    """Main entry point for the GUI application."""
    root = tk.Tk()
    app = MasterServerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

