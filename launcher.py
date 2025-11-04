#!/usr/bin/env python3
"""
CS 1.6 Master Server - Unified Launcher
Launch with GUI, Web Dashboard, or Console mode.
"""

import sys
import os

# Setup vendor path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENDOR_DIR = os.path.join(BASE_DIR, "vendor")
if os.path.exists(VENDOR_DIR) and VENDOR_DIR not in sys.path:
    sys.path.insert(0, VENDOR_DIR)


def show_launcher_menu():
    """Show launcher menu to choose interface mode."""
    print("=" * 70)
    print(" CS 1.6 MASTER SERVER - ULTIMATE EDITION")
    print("=" * 70)
    print()
    print("Choose your interface:")
    print()
    print("  1. 🎨 Desktop GUI (Tkinter with Azure theme)")
    print("     - Modern desktop application")
    print("     - Azure Fluent Design theme")
    print("     - Native controls and dialogs")
    print()
    print("  2. 🌐 Web Dashboard (Browser-based)")
    print("     - Stunning glass-morphism design")
    print("     - Real-time charts with Chart.js")
    print("     - Access from any browser")
    print()
    print("  3. 💻 Console Mode (Command-line)")
    print("     - Lightweight text interface")
    print("     - Perfect for servers/headless")
    print()
    print("  4. 🚀 Hybrid Mode (Both GUI + Web)")
    print("     - Desktop GUI with embedded web dashboard")
    print("     - Best of both worlds!")
    print()
    print("=" * 70)
    
    choice = input("\nEnter your choice (1-4) [default: 1]: ").strip()
    return choice if choice else "1"


def launch_desktop_gui():
    """Launch the Tkinter desktop GUI."""
    print("\n🎨 Launching Desktop GUI...")
    try:
        import gui
        gui.main()
    except Exception as e:
        print(f"Error launching GUI: {e}")
        import traceback
        traceback.print_exc()


def launch_web_dashboard():
    """Launch the web dashboard."""
    print("\n🌐 Launching Web Dashboard...")
    print("Starting web server...")
    
    try:
        from ms import MasterServer
        import asyncio
        from aiohttp import web
        import webbrowser
        import threading
        
        # Create server instance
        server = MasterServer(gui_mode=True)
        
        # Start master server in background
        def run_master_server():
            try:
                server.run()
            except Exception as e:
                print(f"Master server error: {e}")
        
        master_thread = threading.Thread(target=run_master_server, daemon=True)
        master_thread.start()
        
        # Setup web routes
        async def handle_index(request):
            with open(os.path.join(BASE_DIR, 'web_ui.html'), 'r', encoding='utf-8') as f:
                html = f.read()
            return web.Response(text=html, content_type='text/html')
        
        async def handle_stats(request):
            stats = server.stats
            if not stats:
                return web.json_response({})
            
            return web.json_response({
                'totalRequests': stats.total_requests,
                'uniqueIPs': stats.get_unique_ip_count(),
                'currentRPS': round(stats.get_current_rps(), 2),
                'uptimeFormatted': stats.get_uptime_formatted(),
                'requestRate': list(stats.get_request_rate_history()),
                'topCountries': [{'country': c[0], 'count': c[1]} for c in stats.get_top_countries(10)]
            })
        
        async def handle_servers(request):
            servers = server.get_servers()
            return web.json_response([{'ip': ip, 'port': port} for ip, port in servers])
        
        # Create web app
        app = web.Application()
        app.router.add_get('/', handle_index)
        app.router.add_get('/api/stats', handle_stats)
        app.router.add_get('/api/servers', handle_servers)
        
        # Run web server
        async def start_web():
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, '127.0.0.1', 8080)
            await site.start()
            
            url = "http://127.0.0.1:8080"
            print(f"\n✅ Web Dashboard running at: {url}")
            print(f"🌐 Opening browser...")
            print(f"\n📊 Press Ctrl+C to stop")
            
            # Open browser
            webbrowser.open(url)
            
            # Keep running
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\n\nShutting down...")
                await runner.cleanup()
        
        asyncio.run(start_web())
        
    except Exception as e:
        print(f"Error launching web dashboard: {e}")
        import traceback
        traceback.print_exc()


def launch_console():
    """Launch console mode."""
    print("\n💻 Launching Console Mode...")
    try:
        import ms
        ms.main()
    except Exception as e:
        print(f"Error launching console: {e}")
        import traceback
        traceback.print_exc()


def launch_hybrid():
    """Launch hybrid mode - GUI with embedded web server."""
    print("\n🚀 Launching Hybrid Mode...")
    print("Starting Desktop GUI with Web Dashboard...")
    
    try:
        # Start web server in background
        import threading
        import asyncio
        from aiohttp import web
        from ms import MasterServer
        
        # This would launch both GUI and web server
        # For now, just launch GUI
        launch_desktop_gui()
        
    except Exception as e:
        print(f"Error launching hybrid mode: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main launcher entry point."""
    # Check if command line argument provided
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode in ('gui', '1'):
            launch_desktop_gui()
        elif mode in ('web', '2'):
            launch_web_dashboard()
        elif mode in ('console', '3'):
            launch_console()
        elif mode in ('hybrid', '4'):
            launch_hybrid()
        else:
            print(f"Unknown mode: {mode}")
            print("Usage: launcher.py [gui|web|console|hybrid]")
    else:
        # Show interactive menu
        choice = show_launcher_menu()
        
        if choice == "1":
            launch_desktop_gui()
        elif choice == "2":
            launch_web_dashboard()
        elif choice == "3":
            launch_console()
        elif choice == "4":
            launch_hybrid()
        else:
            print("Invalid choice. Launching Desktop GUI by default...")
            launch_desktop_gui()


if __name__ == "__main__":
    main()






