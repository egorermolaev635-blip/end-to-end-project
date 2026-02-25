@echo off
title Setup
echo ========================================
echo Data Science Project Environment Setup
echo ========================================

REM Check files first
if not exist "..\broken_env.py" (
    echo [ERROR] broken_env.py not found!
    pause
    exit /b 1
)
if not exist "..\requirements.txt" (
    echo [ERROR] requirements.txt not found!
    pause
    exit /b 1
)

echo [OK] Files found OK

REM Try to find conda
where conda >nul 2>nul
if %errorlevel%==0 (
    echo [OK] conda found in PATH
    call conda env list | findstr ds_project >nul
    if %errorlevel%==0 (
        echo [OK] ds_project exists
    ) else (
        echo [INFO] Creating ds_project...
        call conda create -n ds_project python=3.11 -y
    )
    echo [INFO] Installing packages...
    call conda run -n ds_project pip install -r ..\requirements.txt
    echo [INFO] Testing...
    call conda run -n ds_project python ..\broken_env.py
    echo.
    echo ========================================
    echo           SUCCESS - Setup Complete!
    echo ========================================
    pause
    exit /b 0
) else (
    echo.
    echo ========================================
    echo [INFO] conda not in PATH - use Anaconda Prompt:
    echo 1. Start Menu -^> "Anaconda Prompt"
    echo 2. cd %~dp0..
    echo 3. scripts\setup_env.bat
    echo ========================================
    pause
)
