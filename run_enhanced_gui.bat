@echo off
echo Starting Enhanced 3D File Generator (Modern GUI)
echo ================================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Try to run the modern GUI
echo Starting modern GUI...
python enhanced_3d_gui_modern.py

REM If that fails, try the enhanced version
if %errorlevel% neq 0 (
    echo Modern GUI failed, trying enhanced version...
    python demo_enhanced_3d_app.py
)

REM If that fails, try the original
if %errorlevel% neq 0 (
    echo Enhanced version failed, trying original...
    python 3DFile_FileFolderGenerator.py
)

echo.
echo Press any key to exit...
pause >nul