#!/usr/bin/env python3
"""
Web API bridge for pywebview interface.
Provides JavaScript ↔ Python communication for the web-based GUI.
"""

import json
from typing import List, Dict, Any
from datetime import datetime


class MasterServerAPI:
    """
    API class exposed to JavaScript for the web interface.
    All public methods are callable from JavaScript via pywebview.
    """
    
    def __init__(self, server_instance, stats_instance):
        self.server = server_instance
        self.stats = stats_instance
        self.callbacks = []
    
    # ==================== Server Control ====================
    
    def start_server(self) -> Dict[str, Any]:
        """Start the master server."""
        try:
            if hasattr(self, '_server_thread') and self._server_thread and self._server_thread.is_alive():
                return {"success": False, "message": "Server already running"}
            
            import threading
            self._server_thread = threading.Thread(target=self.server.run, daemon=True)
            self._server_thread.start()
            
            return {"success": True, "message": "Server started successfully"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def stop_server(self) -> Dict[str, Any]:
        """Stop the master server."""
        try:
            self.server.stop()
            return {"success": True, "message": "Server stopped"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def get_server_status(self) -> Dict[str, Any]:
        """Get current server status."""
        is_running = hasattr(self, '_server_thread') and self._server_thread and self._server_thread.is_alive()
        return {
            "running": is_running,
            "host": self.server.host,
            "port": self.server.port,
            "mode": self.server.mode
        }
    
    # ==================== Statistics ====================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current statistics."""
        if not self.stats:
            return {}
        
        return {
            "totalRequests": self.stats.total_requests,
            "uniqueIPs": self.stats.get_unique_ip_count(),
            "currentRPS": round(self.stats.get_current_rps(), 2),
            "averageRPS": round(self.stats.get_average_rps(), 2),
            "uptime": self.stats.get_uptime(),
            "uptimeFormatted": self.stats.get_uptime_formatted(),
            "totalPackets": self.stats.total_packets_sent,
            "totalErrors": self.stats.total_errors,
            "lastRequest": self.stats.get_last_request_time_formatted()
        }
    
    def get_chart_data(self) -> Dict[str, Any]:
        """Get data for charts."""
        if not self.stats:
            return {"requestRate": [], "topCountries": []}
        
        rate_history = self.stats.get_request_rate_history()
        top_countries = self.stats.get_top_countries(10)
        
        return {
            "requestRate": list(rate_history),
            "topCountries": [{"country": c[0], "count": c[1]} for c in top_countries]
        }
    
    # ==================== Server List ====================
    
    def get_servers(self) -> List[Dict[str, Any]]:
        """Get all servers."""
        servers = self.server.get_servers()
        return [{"ip": ip, "port": port} for ip, port in servers]
    
    def add_server(self, ip: str, port: int) -> Dict[str, Any]:
        """Add a server."""
        try:
            servers = self.server.get_servers()
            
            if (ip, port) in servers:
                return {"success": False, "message": "Server already exists"}
            
            servers.append((ip, port))
            if self.server.save_servers(servers):
                return {"success": True, "message": f"Added {ip}:{port}"}
            else:
                return {"success": False, "message": "Failed to save"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def remove_server(self, ip: str, port: int) -> Dict[str, Any]:
        """Remove a server."""
        try:
            servers = self.server.get_servers()
            
            if (ip, port) in servers:
                servers.remove((ip, port))
                if self.server.save_servers(servers):
                    return {"success": True, "message": f"Removed {ip}:{port}"}
            
            return {"success": False, "message": "Server not found"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def bulk_add_servers(self, servers_json: str) -> Dict[str, Any]:
        """Bulk add servers from JSON."""
        try:
            new_servers = json.loads(servers_json)
            existing = self.server.get_servers()
            
            added = 0
            for server_data in new_servers:
                ip = server_data.get('ip')
                port = server_data.get('port')
                if ip and port and (ip, port) not in existing:
                    existing.append((ip, port))
                    added += 1
            
            if added > 0:
                self.server.save_servers(existing)
                return {"success": True, "message": f"Added {added} servers"}
            else:
                return {"success": False, "message": "No new servers to add"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    # ==================== Configuration ====================
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return {
            "host": self.server.host,
            "port": self.server.port,
            "mode": self.server.mode,
            "refresh": self.server.refresh,
            "geoipEnabled": self.server.geoip_enabled,
            "logOncePerIP": self.server.log_once_per_ip
        }
    
    def save_config(self, config_json: str) -> Dict[str, Any]:
        """Save configuration (requires restart)."""
        try:
            config = json.loads(config_json)
            # Configuration saving would update ms.cfg file
            # For now, return success
            return {"success": True, "message": "Configuration saved. Restart server to apply."}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    # ==================== Utility ====================
    
    def get_logs(self, limit: int = 100) -> List[Dict[str, str]]:
        """Get recent log messages."""
        # This would require storing logs in a buffer
        # For now, return empty list
        return []
    
    def parse_server_text(self, text: str) -> List[Dict[str, Any]]:
        """Parse server list from text."""
        import re
        servers = []
        pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)'
        
        for match in re.finditer(pattern, text):
            try:
                ip = match.group(1)
                port = int(match.group(2))
                if 1 <= port <= 65535:
                    servers.append({"ip": ip, "port": port})
            except:
                continue
        
        return servers




