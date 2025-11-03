#!/usr/bin/env python3
"""
Database storage module for CS 1.6 Master Server.
Provides SQLite-based server list management.
"""

import sqlite3
import os
from typing import List, Tuple, Optional
from datetime import datetime


class ServerDatabase:
    """
    SQLite database manager for server list.
    """
    
    def __init__(self, db_path: str = "servers.db"):
        """Initialize database connection."""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Connect to SQLite database."""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
    
    def _create_tables(self):
        """Create database tables if they don't exist."""
        # Servers table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS servers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip TEXT NOT NULL,
                port INTEGER NOT NULL,
                name TEXT,
                description TEXT,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                enabled INTEGER DEFAULT 1,
                UNIQUE(ip, port)
            )
        """)
        
        # Statistics table (optional - for future use)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS server_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                requests INTEGER DEFAULT 0,
                FOREIGN KEY (server_id) REFERENCES servers(id)
            )
        """)
        
        self.conn.commit()
    
    def add_server(self, ip: str, port: int, name: str = None, description: str = None) -> bool:
        """Add a server to the database."""
        try:
            self.cursor.execute(
                "INSERT INTO servers (ip, port, name, description) VALUES (?, ?, ?, ?)",
                (ip, port, name, description)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Server already exists
            return False
        except Exception as e:
            print(f"Error adding server: {e}")
            return False
    
    def remove_server(self, ip: str, port: int) -> bool:
        """Remove a server from the database."""
        try:
            self.cursor.execute(
                "DELETE FROM servers WHERE ip = ? AND port = ?",
                (ip, port)
            )
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Error removing server: {e}")
            return False
    
    def remove_server_by_id(self, server_id: int) -> bool:
        """Remove a server by ID."""
        try:
            self.cursor.execute("DELETE FROM servers WHERE id = ?", (server_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Error removing server: {e}")
            return False
    
    def get_all_servers(self, enabled_only: bool = True) -> List[Tuple[str, int]]:
        """Get all servers from database."""
        try:
            if enabled_only:
                self.cursor.execute(
                    "SELECT ip, port FROM servers WHERE enabled = 1 ORDER BY id"
                )
            else:
                self.cursor.execute(
                    "SELECT ip, port FROM servers ORDER BY id"
                )
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting servers: {e}")
            return []
    
    def get_servers_detailed(self) -> List[dict]:
        """Get all servers with detailed information."""
        try:
            self.cursor.execute(
                """SELECT id, ip, port, name, description, added_date, enabled 
                   FROM servers ORDER BY id"""
            )
            rows = self.cursor.fetchall()
            servers = []
            for row in rows:
                servers.append({
                    'id': row[0],
                    'ip': row[1],
                    'port': row[2],
                    'name': row[3],
                    'description': row[4],
                    'added_date': row[5],
                    'enabled': bool(row[6])
                })
            return servers
        except Exception as e:
            print(f"Error getting detailed servers: {e}")
            return []
    
    def update_server(self, ip: str, port: int, name: str = None, description: str = None) -> bool:
        """Update server information."""
        try:
            self.cursor.execute(
                "UPDATE servers SET name = ?, description = ? WHERE ip = ? AND port = ?",
                (name, description, ip, port)
            )
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating server: {e}")
            return False
    
    def toggle_server(self, ip: str, port: int, enabled: bool) -> bool:
        """Enable or disable a server."""
        try:
            self.cursor.execute(
                "UPDATE servers SET enabled = ? WHERE ip = ? AND port = ?",
                (1 if enabled else 0, ip, port)
            )
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Error toggling server: {e}")
            return False
    
    def server_exists(self, ip: str, port: int) -> bool:
        """Check if a server exists in the database."""
        try:
            self.cursor.execute(
                "SELECT COUNT(*) FROM servers WHERE ip = ? AND port = ?",
                (ip, port)
            )
            count = self.cursor.fetchone()[0]
            return count > 0
        except Exception as e:
            print(f"Error checking server: {e}")
            return False
    
    def get_server_count(self, enabled_only: bool = True) -> int:
        """Get total number of servers."""
        try:
            if enabled_only:
                self.cursor.execute("SELECT COUNT(*) FROM servers WHERE enabled = 1")
            else:
                self.cursor.execute("SELECT COUNT(*) FROM servers")
            return self.cursor.fetchone()[0]
        except Exception as e:
            print(f"Error counting servers: {e}")
            return 0
    
    def import_from_file(self, file_path: str) -> Tuple[int, int]:
        """Import servers from text file. Returns (added, skipped)."""
        added = 0
        skipped = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    if ':' not in line:
                        continue
                    
                    try:
                        ip, port_str = line.split(':', 1)
                        ip = ip.strip()
                        port = int(port_str.strip())
                        
                        if self.add_server(ip, port):
                            added += 1
                        else:
                            skipped += 1
                    except Exception:
                        skipped += 1
        except Exception as e:
            print(f"Error importing from file: {e}")
        
        return added, skipped
    
    def export_to_file(self, file_path: str) -> bool:
        """Export servers to text file."""
        try:
            servers = self.get_all_servers(enabled_only=False)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("# CS 1.6 Server List\n")
                f.write(f"# Exported from database on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("# Format: IP:PORT\n\n")
                
                for ip, port in servers:
                    f.write(f"{ip}:{port}\n")
            
            return True
        except Exception as e:
            print(f"Error exporting to file: {e}")
            return False
    
    def clear_all(self) -> bool:
        """Remove all servers from database."""
        try:
            self.cursor.execute("DELETE FROM servers")
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error clearing database: {e}")
            return False
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def __del__(self):
        """Destructor to ensure connection is closed."""
        self.close()




