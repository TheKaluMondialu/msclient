@echo off
REM CS 1.6 Master Server - Build Script for Windows
REM This script creates standalone .exe files using PyInstaller
REM Builds both console and GUI versions

echo ============================================================
echo CS 1.6 Master Server - Build to EXE
echo ============================================================
echo.
echo This will build:
echo  1. Console version (ms.py - console window)
echo  2. GUI version (gui.py - windowed application)
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.7 or newer.
    pause
    exit /b 1
)

echo [1/6] Checking dependencies...
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo [INFO] PyInstaller not found. Installing...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo [ERROR] Failed to install PyInstaller
        pause
        exit /b 1
    )
)

REM Install GUI dependencies
echo [INFO] Installing GUI dependencies...
python -m pip install -q matplotlib geoip2

echo [2/6] Cleaning previous build artifacts...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "*.spec" del /q *.spec

echo [3/6] Building console version...
python -m PyInstaller --onefile --console --name "CS16MasterServer-Console" ^
    --add-data "ms.cfg;." ^
    --add-data "servers_cs.txt;." ^
    --hidden-import=geoip2.database ^
    --hidden-import=geoip2.errors ^
    ms.py

if errorlevel 1 (
    echo [ERROR] Console build failed!
    pause
    exit /b 1
)

echo [4/6] Building GUI version...
python -m PyInstaller --onefile --windowed --name "CS16MasterServer" ^
    --add-data "ms.cfg;." ^
    --add-data "servers_cs.txt;." ^
    --hidden-import=geoip2.database ^
    --hidden-import=geoip2.errors ^
    --hidden-import=matplotlib ^
    --hidden-import=matplotlib.backends.backend_tkagg ^
    --hidden-import=pystray ^
    --hidden-import=pywinstyles ^
    --icon=NONE ^
    gui.py

if errorlevel 1 (
    echo [ERROR] GUI build failed!
    pause
    exit /b 1
)

echo [5/6] Copying configuration files...
if exist "dist" (
    if not exist "dist\ms.cfg" (
        if exist "ms.cfg" copy "ms.cfg" "dist\"
    )
    if not exist "dist\servers_cs.txt" (
        if exist "servers_cs.txt" copy "servers_cs.txt" "dist\"
    )
    if exist "GeoLite2-Country.mmdb" copy "GeoLite2-Country.mmdb" "dist\"
    if exist "GeoLite2-City.mmdb" copy "GeoLite2-City.mmdb" "dist\"
)

echo [6/6] Finalizing...
if exist "dist\CS16MasterServer.exe" (
    echo.
    echo ============================================================
    echo BUILD SUCCESSFUL!
    echo ============================================================
    echo.
    echo Executables created:
    echo  - dist\CS16MasterServer.exe (GUI version - double-click to run)
    echo  - dist\CS16MasterServer-Console.exe (Console version)
    echo.
    echo Next steps:
    echo 1. Copy the contents of 'dist' folder to your desired location
    echo 2. Run CS16MasterServer.exe to launch the GUI application
    echo 3. Or run CS16MasterServer-Console.exe for console mode
    echo 4. Add your CS 1.6 servers via the GUI or edit servers_cs.txt
    echo 5. Optionally download GeoLite2-Country.mmdb for GeoIP support
    echo.
    echo The GUI provides:
    echo  - Real-time statistics dashboard
    echo  - Interactive server management
    echo  - Color-coded console logs
    echo  - Visual configuration editor
    echo.
    echo ============================================================
) else (
    echo [ERROR] Executable not found in dist folder!
    pause
    exit /b 1
)

pause