@echo off
REM ============================================================
REM Golden Emirat v2.0 - Windows Launcher
REM ============================================================

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║   🥇 GOLDEN EMIRAT v2.0 - Starting...                  ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

REM Check Python
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERROR] Python not found!
    pause
    exit /b 1
)

REM Activate virtual environment (optional)
IF EXIST "venv\Scripts\activate.bat" (
    echo [*] Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Install dependencies if needed
IF NOT EXIST "venv\Lib\site-packages\PyQt6" (
    echo [*] Installing dependencies...
    pip install -r requirements.txt
)

REM Run the bot
echo [*] Starting Golden Emirat...
python main_golden.py

pause