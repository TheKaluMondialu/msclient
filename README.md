# CS 1.6 Master Server - Ultimate Edition

A powerful and feature-rich Counter-Strike 1.6 Master Server implementation written in Python.

## Features

- 🎮 **Full CS 1.6 Master Server Protocol Support**
- 🗄️ **Dual Mode Operation**: File-based or Database storage
- 🌍 **GeoIP Integration**: Track player locations with MaxMind GeoLite2
- 📊 **Real-time Statistics**: Monitor requests, unique IPs, and more
- 🎨 **Multiple Interfaces**:
  - Modern Desktop GUI (Tkinter with Azure theme)
  - Web Dashboard (Browser-based with real-time charts)
  - Console Mode (Lightweight CLI)
- 🔍 **Server Discovery**: Bulk import servers from various sources
- ⚡ **High Performance**: Handles thousands of requests efficiently
- 🛡️ **Cross-Platform**: Works on Windows and Linux

## Quick Start

### Desktop GUI Mode
```bash
python launcher.py
# Choose option 1 for Desktop GUI
```

### Web Dashboard Mode
```bash
python launcher.py
# Choose option 2 for Web Dashboard
```

### Console Mode
```bash
python launcher.py
# Choose option 3 for Console Mode
```

## Configuration

Edit `ms.cfg` to configure the master server:

```ini
[OPTIONS]
HOST = 0.0.0.0
PORTGS = 27010
REFRESH = 60
MODE = database  # or "file"
DEBUG = 1        # Enable debug logging

[DATABASE]
DB_PATH = servers.db

[GEOIP]
ENABLE = 1
DB_PATH = GeoLite2-Country.mmdb
```

## Requirements

- Python 3.8+
- Dependencies are auto-installed to `./vendor` on first run

## Adding Servers

Add CS 1.6 servers in `servers_cs.txt` (file mode) or use the GUI to manage servers in database mode:

```
192.168.1.100:27015
game.example.com:27016
```

## GeoIP Database

For GeoIP functionality:
1. Register for a free MaxMind account at https://www.maxmind.com
2. Download GeoLite2-Country.mmdb or GeoLite2-City.mmdb
3. Place the .mmdb file in the project directory

## Debug Mode

Enable debug mode to see detailed logs:
- Set `DEBUG = 1` in `ms.cfg`
- See real-time request information, packet details, and server health

## License

Open Source - Feel free to use and modify

## Author

Created by TheKaluMondialu

## Links

- GitHub: https://github.com/TheKaluMondialu/msclient



