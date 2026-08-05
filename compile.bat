@echo off
title Virtual Radiosonde Plotter Compiler (TensorFlow Env)
color 0A

echo ========================================================
echo   Virtual Radiosonde Plotter - PyInstaller Compiler
echo   Conda Environment: D:\conda_env\tensorflow
echo ========================================================
echo.

echo [1/3] Closing any running instances of VirtualRadiosondePlotter.exe...
taskkill /F /IM VirtualRadiosondePlotter.exe >nul 2>&1

echo.
echo [2/3] Building executable using TensorFlow Conda Environment...
D:\conda_env\tensorflow\Scripts\pyinstaller.exe --noconfirm VirtualRadiosondePlotter.spec

if %ERRORLEVEL% NEQ 0 (
    echo.
    color 0C
    echo ========================================================
    echo   [ERROR] Compilation failed! Please check error log.
    echo ========================================================
    echo.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [3/3] Build complete!
echo.
echo ========================================================
echo   [SUCCESS] Executable built successfully!
echo   Output Path: dist\VirtualRadiosondePlotter\VirtualRadiosondePlotter.exe
echo ========================================================
echo.

pause
