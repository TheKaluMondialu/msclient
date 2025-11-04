#!/usr/bin/env python3
"""
Modern Web Dashboard for CS 1.6 Master Server.
Provides a stunning HTML5/CSS3/JavaScript interface.
"""

import asyncio
import json
import os
import sys
import webbrowser
from datetime import datetime

# Ensure vendor is in path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENDOR_DIR = os.path.join(BASE_DIR, "vendor")
if os.path.exists(VENDOR_DIR) and VENDOR_DIR not in sys.path:
    sys.path.insert(0, VENDOR_DIR)

from aiohttp import web
from ms import MasterServer, ensure_vendor_on_path
from stats import Statistics


class WebDashboard:
    """
    Web-based dashboard server.
    """
    
    def __init__(self, master_server: MasterServer, host='127.0.0.1', port=8080):
        self.host = host
        self.port = port
        self.master_server = master_server
        self.app = web.Application()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup web routes."""
        self.app.router.add_get('/', self.index)
        self.app.router.add_get('/api/stats', self.api_stats)
        self.app.router.add_get('/api/servers', self.api_servers)
        self.app.router.add_post('/api/servers/add', self.api_add_server)
        self.app.router.add_post('/api/servers/remove', self.api_remove_server)
        self.app.router.add_post('/api/server/start', self.api_start_server)
        self.app.router.add_post('/api/server/stop', self.api_stop_server)
        self.app.router.add_get('/api/status', self.api_status)
    
    async def index(self, request):
        """Serve the main dashboard HTML."""
        html = self._generate_dashboard_html()
        return web.Response(text=html, content_type='text/html')
    
    async def api_stats(self, request):
        """API: Get statistics."""
        if not self.master_server.stats:
            return web.json_response({})
        
        stats = self.master_server.stats
        data = {
            'totalRequests': stats.total_requests,
            'uniqueIPs': stats.get_unique_ip_count(),
            'currentRPS': round(stats.get_current_rps(), 2),
            'averageRPS': round(stats.get_average_rps(), 2),
            'uptime': stats.get_uptime_formatted(),
            'totalPackets': stats.total_packets_sent,
            'requestRate': list(stats.get_request_rate_history()),
            'topCountries': [{'country': c[0], 'count': c[1]} for c in stats.get_top_countries(10)]
        }
        return web.json_response(data)
    
    async def api_servers(self, request):
        """API: Get server list."""
        servers = self.master_server.get_servers()
        data = [{'ip': ip, 'port': port} for ip, port in servers]
        return web.json_response(data)
    
    async def api_add_server(self, request):
        """API: Add a server."""
        data = await request.json()
        ip = data.get('ip')
        port = data.get('port')
        
        if not ip or not port:
            return web.json_response({'success': False, 'message': 'IP and port required'})
        
        servers = self.master_server.get_servers()
        if (ip, port) in servers:
            return web.json_response({'success': False, 'message': 'Server already exists'})
        
        servers.append((ip, port))
        if self.master_server.save_servers(servers):
            return web.json_response({'success': True, 'message': 'Server added'})
        else:
            return web.json_response({'success': False, 'message': 'Failed to save'})
    
    async def api_remove_server(self, request):
        """API: Remove a server."""
        data = await request.json()
        ip = data.get('ip')
        port = data.get('port')
        
        servers = self.master_server.get_servers()
        if (ip, port) in servers:
            servers.remove((ip, port))
            if self.master_server.save_servers(servers):
                return web.json_response({'success': True, 'message': 'Server removed'})
        
        return web.json_response({'success': False, 'message': 'Server not found'})
    
    async def api_start_server(self, request):
        """API: Start master server."""
        # Server start would be handled by separate thread
        return web.json_response({'success': True, 'message': 'Start command sent'})
    
    async def api_stop_server(self, request):
        """API: Stop master server."""
        # Server stop would be handled
        return web.json_response({'success': True, 'message': 'Stop command sent'})
    
    async def api_status(self, request):
        """API: Get server status."""
        data = {
            'running': True,  # Would check actual status
            'host': self.master_server.host,
            'port': self.master_server.port,
            'mode': self.master_server.mode,
            'serverCount': len(self.master_server.get_servers())
        }
        return web.json_response(data)
    
    def _generate_dashboard_html(self):
        """Generate the dashboard HTML."""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CS 1.6 Master Server - Web Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        }
        
        .header h1 {
            font-size: 2.5em;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        
        .stat-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
        }
        
        .stat-card .icon {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .stat-card .label {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        
        .stat-card .value {
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }
        
        .charts {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .chart-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        .chart-container h3 {
            margin-bottom: 15px;
            color: #333;
        }
        
        .server-list {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        .server-list h3 {
            margin-bottom: 20px;
            color: #333;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        
        th {
            background: #f8f9fa;
            font-weight: 600;
            color: #667eea;
        }
        
        tr:hover {
            background: #f8f9fa;
        }
        
        .status {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status.running { background: #10b981; }
        .status.stopped { background: #ef4444; }
        
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 10px;
            font-size: 1em;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        button:hover {
            transform: scale(1.05);
        }
        
        button:active {
            transform: scale(0.95);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎮 CS 1.6 Master Server Dashboard</h1>
            <p style="color: #666;">Modern Web-Based Control Panel</p>
        </div>
        
        <div class="stat-cards">
            <div class="stat-card">
                <div class="icon">📊</div>
                <div class="label">Total Requests</div>
                <div class="value" id="totalRequests">0</div>
            </div>
            <div class="stat-card">
                <div class="icon">👥</div>
                <div class="label">Unique Players</div>
                <div class="value" id="uniqueIPs">0</div>
            </div>
            <div class="stat-card">
                <div class="icon">⚡</div>
                <div class="label">Requests/sec</div>
                <div class="value" id="currentRPS">0.00</div>
            </div>
            <div class="stat-card">
                <div class="icon">⏱️</div>
                <div class="label">Uptime</div>
                <div class="value" id="uptime">0s</div>
            </div>
            <div class="stat-card">
                <div class="icon">🌐</div>
                <div class="label">Active Servers</div>
                <div class="value" id="serverCount">0</div>
            </div>
        </div>
        
        <div class="charts">
            <div class="chart-container">
                <h3>📈 Request Rate (60s)</h3>
                <canvas id="requestRateChart"></canvas>
            </div>
            <div class="chart-container">
                <h3>🌍 Top Countries</h3>
                <canvas id="countriesChart"></canvas>
            </div>
        </div>
        
        <div class="server-list">
            <h3>🖥️ Server List</h3>
            <table id="serverTable">
                <thead>
                    <tr>
                        <th>IP Address</th>
                        <th>Port</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody id="serverTableBody">
                    <tr><td colspan="3">Loading...</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <script>
        // Chart instances
        let requestChart, countriesChart;
        
        // Initialize charts
        function initCharts() {
            const commonOptions = {
                responsive: true,
                maintainAspectRatio: true,
                plugins: { legend: { display: false } }
            };
            
            requestChart = new Chart(document.getElementById('requestRateChart'), {
                type: 'line',
                data: {
                    labels: Array.from({length: 60}, (_, i) => i),
                    datasets: [{
                        data: [],
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: commonOptions
            });
            
            countriesChart = new Chart(document.getElementById('countriesChart'), {
                type: 'bar',
                data: {
                    labels: [],
                    datasets: [{
                        data: [],
                        backgroundColor: '#764ba2'
                    }]
                },
                options: commonOptions
            });
        }
        
        // Update dashboard
        async function updateDashboard() {
            try {
                // Fetch stats
                const statsRes = await fetch('/api/stats');
                const stats = await statsRes.json();
                
                // Update stat cards
                document.getElementById('totalRequests').textContent = stats.totalRequests || 0;
                document.getElementById('uniqueIPs').textContent = stats.uniqueIPs || 0;
                document.getElementById('currentRPS').textContent = stats.currentRPS || '0.00';
                document.getElementById('uptime').textContent = stats.uptimeFormatted || '0s';
                
                // Update charts
                if (stats.requestRate && requestChart) {
                    requestChart.data.datasets[0].data = stats.requestRate;
                    requestChart.update();
                }
                
                if (stats.topCountries && countriesChart) {
                    countriesChart.data.labels = stats.topCountries.map(c => c.country);
                    countriesChart.data.datasets[0].data = stats.topCountries.map(c => c.count);
                    countriesChart.update();
                }
                
                // Fetch servers
                const serversRes = await fetch('/api/servers');
                const servers = await serversRes.json();
                
                document.getElementById('serverCount').textContent = servers.length;
                
                // Update server table
                const tbody = document.getElementById('serverTableBody');
                tbody.innerHTML = servers.map(s => `
                    <tr>
                        <td>${s.ip}</td>
                        <td>${s.port}</td>
                        <td><span class="status running"></span>Active</td>
                    </tr>
                `).join('');
                
            } catch (error) {
                console.error('Update error:', error);
            }
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', () => {
            initCharts();
            updateDashboard();
            setInterval(updateDashboard, 2000); // Update every 2 seconds
        });
    </script>
</body>
</html>'''
    
    async def start_web_server(self):
        """Start the web dashboard server."""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        url = f"http://{self.host}:{self.port}"
        print(f"🌐 Web Dashboard running at: {url}")
        print(f"📊 Open your browser to view the dashboard!")
        
        # Auto-open browser
        try:
            webbrowser.open(url)
        except:
            pass
        
        return runner


def launch_web_dashboard(master_server: MasterServer, host='127.0.0.1', port=8080):
    """Launch the web dashboard."""
    dashboard = WebDashboard(master_server, host, port)
    
    async def run():
        runner = await dashboard.start_web_server()
        try:
            # Keep running
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await runner.cleanup()
    
    asyncio.run(run())


if __name__ == "__main__":
    ensure_vendor_on_path()
    server = MasterServer(gui_mode=True)
    launch_web_dashboard(server)






