#!/usr/bin/env python3
"""
Server discovery and bulk import dialog for CS 1.6 Master Server.
Allows finding and adding multiple servers from various sources.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import List, Tuple, Optional, Callable
import threading
import re
from theme import Colors, Fonts, Layout


class ServerDiscoveryDialog(tk.Toplevel):
    """
    Dialog for discovering and bulk-adding CS 1.6 servers.
    """
    
    def __init__(self, parent, add_callback: Callable):
        super().__init__(parent)
        
        self.title("Discover & Add CS 1.6 Servers")
        self.geometry("800x600")
        self.resizable(True, True)
        
        self.transient(parent)
        self.grab_set()
        
        self.add_callback = add_callback
        self.discovered_servers = []
        self.is_searching = False
        
        # Create UI
        self._create_ui()
    
    def _create_ui(self):
        """Create the dialog UI."""
        # Header
        header = tk.Frame(self, bg=Colors.PRIMARY, height=50)
        header.pack(side=tk.TOP, fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="🌐 Discover CS 1.6 Servers",
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_LARGE, Fonts.WEIGHT_BOLD),
            fg=Colors.TEXT_WHITE,
            bg=Colors.PRIMARY
        ).pack(side=tk.LEFT, padx=Layout.PADDING_LARGE, pady=Layout.PADDING_MEDIUM)
        
        # Main content
        content = tk.Frame(self, bg=Colors.BG_PRIMARY)
        content.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Method selection
        method_frame = tk.Frame(content, bg=Colors.BG_SECONDARY, relief=tk.RAISED, borderwidth=1)
        method_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        tk.Label(
            method_frame,
            text="Choose Discovery Method:",
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_NORMAL, Fonts.WEIGHT_BOLD),
            bg=Colors.BG_SECONDARY
        ).pack(side=tk.TOP, anchor=tk.W, padx=10, pady=5)
        
        # Tabs for different methods
        self.method_notebook = ttk.Notebook(method_frame)
        self.method_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Paste server list
        self._create_paste_tab()
        
        # Tab 2: GameTracker search
        self._create_gametracker_tab()
        
        # Tab 3: IP Range scan
        self._create_scan_tab()
        
        # Results section
        results_frame = tk.Frame(content, bg=Colors.BG_SECONDARY, relief=tk.RAISED, borderwidth=1)
        results_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        tk.Label(
            results_frame,
            text="Discovered Servers:",
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_NORMAL, Fonts.WEIGHT_BOLD),
            bg=Colors.BG_SECONDARY
        ).pack(side=tk.TOP, anchor=tk.W, padx=10, pady=5)
        
        # Server list
        list_frame = tk.Frame(results_frame, bg=Colors.BG_PRIMARY)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbars
        vsb = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        self.server_tree = ttk.Treeview(
            list_frame,
            columns=("IP", "Port", "Name"),
            show="headings",
            yscrollcommand=vsb.set,
            selectmode=tk.EXTENDED
        )
        self.server_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.config(command=self.server_tree.yview)
        
        self.server_tree.heading("IP", text="IP Address")
        self.server_tree.heading("Port", text="Port")
        self.server_tree.heading("Name", text="Server Name")
        
        self.server_tree.column("IP", width=150)
        self.server_tree.column("Port", width=80)
        self.server_tree.column("Name", width=400)
        
        # Status label
        self.status_label = tk.Label(
            results_frame,
            text="0 servers found",
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_SMALL),
            fg=Colors.TEXT_SECONDARY,
            bg=Colors.BG_SECONDARY
        )
        self.status_label.pack(side=tk.TOP, anchor=tk.W, padx=10, pady=5)
        
        # Bottom buttons
        button_frame = tk.Frame(self, bg=Colors.BG_PRIMARY)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            button_frame,
            text="✅ Add Selected Servers",
            command=self.add_selected,
            bg=Colors.SUCCESS,
            fg=Colors.TEXT_WHITE,
            relief=tk.FLAT,
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_NORMAL),
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="➕ Add All",
            command=self.add_all,
            bg=Colors.PRIMARY,
            fg=Colors.TEXT_WHITE,
            relief=tk.FLAT,
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_NORMAL),
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="🗑 Clear Results",
            command=self.clear_results,
            bg=Colors.BG_TERTIARY,
            relief=tk.FLAT,
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_NORMAL),
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Close",
            command=self.destroy,
            relief=tk.FLAT,
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_NORMAL),
            padx=15,
            pady=8
        ).pack(side=tk.RIGHT, padx=5)
    
    def _create_paste_tab(self):
        """Create the paste server list tab."""
        paste_frame = tk.Frame(self.method_notebook, bg=Colors.BG_PRIMARY)
        self.method_notebook.add(paste_frame, text="📋 Paste List")
        
        # Instructions
        tk.Label(
            paste_frame,
            text="Paste server list (one per line, format: IP:PORT or IP:PORT Name):",
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_NORMAL),
            bg=Colors.BG_PRIMARY
        ).pack(side=tk.TOP, anchor=tk.W, padx=10, pady=10)
        
        # Text area
        text_frame = tk.Frame(paste_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.paste_text = scrolledtext.ScrolledText(
            text_frame,
            font=(Fonts.FAMILY_MONO, Fonts.SIZE_NORMAL),
            wrap=tk.WORD,
            height=10
        )
        self.paste_text.pack(fill=tk.BOTH, expand=True)
        
        # Example text
        example = """# Example formats:
192.168.1.100:27015
51.195.85.15:27015 AUREN.AREA-GAMES.RO
177.54.152.56:27015 ClaN Brasilia
game.example.com:27016 My Server"""
        
        self.paste_text.insert(1.0, example)
        
        # Parse button
        tk.Button(
            paste_frame,
            text="🔍 Parse & Find Servers",
            command=self.parse_pasted_text,
            bg=Colors.PRIMARY,
            fg=Colors.TEXT_WHITE,
            relief=tk.FLAT,
            padx=15,
            pady=8
        ).pack(side=tk.TOP, pady=10)
    
    def _create_gametracker_tab(self):
        """Create the GameTracker search tab."""
        gt_frame = tk.Frame(self.method_notebook, bg=Colors.BG_PRIMARY)
        self.method_notebook.add(gt_frame, text="🌐 GameTracker")
        
        # Instructions
        tk.Label(
            gt_frame,
            text="Search for CS 1.6 servers on GameTracker.com:",
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_NORMAL),
            bg=Colors.BG_PRIMARY
        ).pack(side=tk.TOP, anchor=tk.W, padx=10, pady=10)
        
        # Search options
        options_frame = tk.Frame(gt_frame, bg=Colors.BG_SECONDARY)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            options_frame,
            text="Country (optional):",
            bg=Colors.BG_SECONDARY
        ).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.country_var = tk.StringVar()
        country_entry = tk.Entry(options_frame, textvariable=self.country_var, width=20)
        country_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        tk.Label(
            options_frame,
            text="Map (optional):",
            bg=Colors.BG_SECONDARY
        ).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.map_var = tk.StringVar()
        map_entry = tk.Entry(options_frame, textvariable=self.map_var, width=20)
        map_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Info label
        info_text = """GameTracker Integration:
• Manually paste server IPs from gametracker.com/search/cs/
• Copy servers from the website and paste in 'Paste List' tab
• Or use the URL parser below"""
        
        tk.Label(
            gt_frame,
            text=info_text,
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_SMALL),
            fg=Colors.TEXT_SECONDARY,
            bg=Colors.BG_PRIMARY,
            justify=tk.LEFT
        ).pack(side=tk.TOP, anchor=tk.W, padx=10, pady=10)
        
        # URL parser
        url_frame = tk.Frame(gt_frame, bg=Colors.BG_PRIMARY)
        url_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            url_frame,
            text="Or paste GameTracker page content:",
            bg=Colors.BG_PRIMARY
        ).pack(side=tk.TOP, anchor=tk.W, pady=(0, 5))
        
        self.gt_text = scrolledtext.ScrolledText(
            url_frame,
            font=(Fonts.FAMILY_MONO, Fonts.SIZE_SMALL),
            wrap=tk.WORD,
            height=8
        )
        self.gt_text.pack(fill=tk.BOTH, expand=True)
        
        tk.Button(
            gt_frame,
            text="🔍 Extract Servers from Text",
            command=self.parse_gametracker_text,
            bg=Colors.PRIMARY,
            fg=Colors.TEXT_WHITE,
            relief=tk.FLAT,
            padx=15,
            pady=8
        ).pack(side=tk.TOP, pady=10)
    
    def _create_scan_tab(self):
        """Create the IP range scan tab."""
        scan_frame = tk.Frame(self.method_notebook, bg=Colors.BG_PRIMARY)
        self.method_notebook.add(scan_frame, text="🔍 IP Scan")
        
        # Instructions
        tk.Label(
            scan_frame,
            text="Scan an IP range for CS 1.6 servers:",
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_NORMAL),
            bg=Colors.BG_PRIMARY
        ).pack(side=tk.TOP, anchor=tk.W, padx=10, pady=10)
        
        # Input fields
        input_frame = tk.Frame(scan_frame, bg=Colors.BG_SECONDARY)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(input_frame, text="Start IP:", bg=Colors.BG_SECONDARY).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.start_ip_var = tk.StringVar(value="192.168.1.1")
        tk.Entry(input_frame, textvariable=self.start_ip_var, width=20).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(input_frame, text="End IP:", bg=Colors.BG_SECONDARY).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.end_ip_var = tk.StringVar(value="192.168.1.254")
        tk.Entry(input_frame, textvariable=self.end_ip_var, width=20).grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(input_frame, text="Port:", bg=Colors.BG_SECONDARY).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.port_var = tk.StringVar(value="27015")
        tk.Entry(input_frame, textvariable=self.port_var, width=20).grid(row=2, column=1, padx=5, pady=5)
        
        # Warning
        warning_text = """⚠️ Warning: IP scanning can be slow and may be blocked by firewalls.
Use responsibly and only scan networks you have permission to scan."""
        
        tk.Label(
            scan_frame,
            text=warning_text,
            font=(Fonts.FAMILY_DEFAULT, Fonts.SIZE_SMALL),
            fg=Colors.WARNING,
            bg=Colors.BG_PRIMARY,
            justify=tk.LEFT
        ).pack(side=tk.TOP, anchor=tk.W, padx=10, pady=10)
        
        # Progress
        self.scan_progress = ttk.Progressbar(scan_frame, mode='indeterminate')
        self.scan_progress.pack(fill=tk.X, padx=10, pady=10)
        
        # Scan button
        self.scan_btn = tk.Button(
            scan_frame,
            text="🔍 Start Scan",
            command=self.start_scan,
            bg=Colors.PRIMARY,
            fg=Colors.TEXT_WHITE,
            relief=tk.FLAT,
            padx=15,
            pady=8
        )
        self.scan_btn.pack(side=tk.TOP, pady=10)
    
    def parse_pasted_text(self):
        """Parse servers from pasted text."""
        text = self.paste_text.get(1.0, tk.END)
        
        # Clear existing results first
        self.clear_results()
        
        # Show processing message
        self.status_label.config(text="Parsing servers...", fg=Colors.INFO)
        self.update()
        
        servers = self._extract_servers_from_text(text, extract_names=True)
        
        if servers:
            self._add_to_results(servers)
            self.status_label.config(
                text=f"✅ Found {len(servers)} servers in pasted text!",
                fg=Colors.SUCCESS
            )
        else:
            self.status_label.config(
                text="❌ No valid servers found. Try format: IP:PORT",
                fg=Colors.ERROR
            )
    
    def parse_gametracker_text(self):
        """Parse servers from GameTracker page content."""
        text = self.gt_text.get(1.0, tk.END)
        
        # Clear existing results first
        self.clear_results()
        
        # Show processing message
        self.status_label.config(text="Extracting servers...", fg=Colors.INFO)
        self.update()
        
        servers = self._extract_servers_from_text(text, extract_names=True)
        
        if servers:
            self._add_to_results(servers)
            self.status_label.config(
                text=f"✅ Extracted {len(servers)} servers from GameTracker data!",
                fg=Colors.SUCCESS
            )
        else:
            self.status_label.config(
                text="❌ No servers found. Make sure you pasted GameTracker page content.",
                fg=Colors.ERROR
            )
    
    def _extract_servers_from_text(self, text: str, extract_names: bool = False) -> List[Tuple]:
        """Extract server IP:Port from text. Returns [(ip, port, name), ...]"""
        servers = []
        servers_dict = {}  # Use dict to avoid duplicates while preserving names
        
        # Multiple patterns to catch various formats
        patterns = [
            # Pattern 1: Standard IP:PORT
            r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)',
            # Pattern 2: Domain:PORT
            r'([a-zA-Z0-9][-a-zA-Z0-9.]+\.[a-zA-Z]{2,}):(\d+)',
        ]
        
        # Process entire text to find all IP:PORT matches
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                try:
                    ip = match.group(1)
                    port = int(match.group(2))
                    
                    # Validate port range (CS 1.6 servers typically use 27000-27999)
                    if not (1 <= port <= 65535):
                        continue
                    
                    # Skip common non-server IPs
                    if ip.startswith('127.') or ip == '0.0.0.0':
                        continue
                    
                    # Extract server name if requested
                    name = ""
                    if extract_names:
                        # Get surrounding context
                        start = max(0, match.start() - 100)
                        end = min(len(text), match.end() + 100)
                        context = text[start:end]
                        
                        # Try to find server name patterns
                        # Look for text before IP that might be a name
                        before_match = context[:match.start() - start].strip()
                        # Look for text after IP:PORT
                        after_match = context[match.end() - start:].strip()
                        
                        # Try to extract name from after (more reliable)
                        if after_match:
                            # Get first line/sentence after match
                            name_match = re.match(r'[^\n\r<>]{1,100}', after_match)
                            if name_match:
                                potential_name = name_match.group(0).strip()
                                # Clean up common separators and HTML
                                potential_name = re.sub(r'[<>]', '', potential_name)
                                potential_name = potential_name.strip('-|/\\ \t')
                                if potential_name and len(potential_name) > 2:
                                    name = potential_name[:80]  # Limit length
                    
                    # Store server (dict prevents duplicates)
                    key = (ip, port)
                    if key not in servers_dict:
                        servers_dict[key] = name
                    elif name and not servers_dict[key]:
                        # Update with name if we found one
                        servers_dict[key] = name
                        
                except (ValueError, IndexError):
                    continue
        
        # Convert dict to list
        servers = [(ip, port, name) for (ip, port), name in servers_dict.items()]
        
        # Sort by IP
        servers.sort(key=lambda x: tuple(int(p) for p in x[0].split('.')))
        
        return servers
    
    def _add_to_results(self, servers: List[Tuple]):
        """Add servers to the results tree."""
        for ip, port, name in servers:
            # Check if already in results
            exists = False
            for item in self.server_tree.get_children():
                values = self.server_tree.item(item)["values"]
                if values[0] == ip and values[1] == port:
                    exists = True
                    break
            
            if not exists:
                self.server_tree.insert("", tk.END, values=(ip, port, name))
                self.discovered_servers.append((ip, port, name))
        
        # Update count
        total = len(self.server_tree.get_children())
        self.status_label.config(text=f"{total} servers found")
    
    def start_scan(self):
        """Start IP range scan."""
        if self.is_searching:
            return
        
        try:
            start_ip = self.start_ip_var.get()
            end_ip = self.end_ip_var.get()
            port = int(self.port_var.get())
            
            self.is_searching = True
            self.scan_btn.config(state=tk.DISABLED, text="⏳ Scanning...")
            self.scan_progress.start()
            
            # Run scan in thread
            thread = threading.Thread(
                target=self._scan_ip_range,
                args=(start_ip, end_ip, port),
                daemon=True
            )
            thread.start()
            
        except ValueError:
            self.status_label.config(text="Invalid port number", fg=Colors.ERROR)
    
    def _scan_ip_range(self, start_ip: str, end_ip: str, port: int):
        """Scan IP range for servers (runs in thread)."""
        import socket
        
        # Parse IP range
        try:
            start_parts = [int(p) for p in start_ip.split('.')]
            end_parts = [int(p) for p in end_ip.split('.')]
        except:
            self.after(0, lambda: self.status_label.config(text="Invalid IP range", fg=Colors.ERROR))
            self._scan_complete()
            return
        
        found = []
        
        # Simple scan - just check if port is open
        # Only scan last octet for performance
        if start_parts[:3] == end_parts[:3]:
            base = '.'.join(str(p) for p in start_parts[:3])
            for i in range(start_parts[3], end_parts[3] + 1):
                ip = f"{base}.{i}"
                
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.5)
                    result = sock.connect_ex((ip, port))
                    sock.close()
                    
                    if result == 0:
                        found.append((ip, port, ""))
                        self.after(0, lambda s=(ip, port, ""): self._add_to_results([s]))
                except:
                    pass
        
        self.after(0, lambda: self.status_label.config(
            text=f"Scan complete: found {len(found)} servers",
            fg=Colors.SUCCESS if found else Colors.WARNING
        ))
        self._scan_complete()
    
    def _scan_complete(self):
        """Scan complete callback."""
        self.is_searching = False
        self.scan_btn.config(state=tk.NORMAL, text="🔍 Start Scan")
        self.scan_progress.stop()
    
    def add_selected(self):
        """Add selected servers."""
        selected = self.server_tree.selection()
        if not selected:
            self.status_label.config(text="No servers selected", fg=Colors.WARNING)
            return
        
        servers_to_add = []
        for item in selected:
            values = self.server_tree.item(item)["values"]
            if len(values) >= 2:
                servers_to_add.append((values[0], int(values[1])))
        
        if servers_to_add and self.add_callback:
            self.add_callback(servers_to_add)
            self.status_label.config(
                text=f"Added {len(servers_to_add)} servers to list!",
                fg=Colors.SUCCESS
            )
    
    def add_all(self):
        """Add all discovered servers."""
        servers_to_add = []
        for item in self.server_tree.get_children():
            values = self.server_tree.item(item)["values"]
            if len(values) >= 2:
                servers_to_add.append((values[0], int(values[1])))
        
        if not servers_to_add:
            self.status_label.config(text="No servers to add", fg=Colors.WARNING)
            return
        
        if self.add_callback:
            self.add_callback(servers_to_add)
            self.status_label.config(
                text=f"Added all {len(servers_to_add)} servers to list!",
                fg=Colors.SUCCESS
            )
    
    def clear_results(self):
        """Clear all results."""
        for item in self.server_tree.get_children():
            self.server_tree.delete(item)
        self.discovered_servers.clear()
        self.status_label.config(text="0 servers found", fg=Colors.TEXT_SECONDARY)

