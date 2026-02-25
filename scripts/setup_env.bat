@echo off
title Setup
echo ========================================
echo Data Science Project Environment Setup
echo ========================================

set PROJECT_DIR=%CD%
set BROKEN_TEST=%PROJECT_DIR%\broken_env.py
set REQ_FILE=%PROJECT_DIR%\requirements.txt

echo Project directory: %PROJECT_DIR%

if not exist "%BROKEN_TEST%" (
    echo [ERROR] broken_env.py not found at: %BROKEN_TEST%
    pause
    exit /b 1
)
if not exist "%REQ_FILE%" (
    echo [ERROR] requirements.txt not found at: %REQ_FILE%
    pause
    exit /b 1
)

echo [OK] All files found

where conda >nul 2>nul
if %errorlevel%==0 (
    echo [OK] conda found in PATH
    
    conda env list | findstr ds_project >nul
    if %errorlevel%==0 (
        echo [OK] ds_project environment exists
    ) else (
        echo [INFO] Creating ds_project environment...
        conda create -n ds_project python=3.11 -y
    )
    
    echo [INFO] Installing packages...
    conda run -n ds_project pip install -r "%REQ_FILE%"
    
    echo [INFO] Running smoke test...
    conda run -n ds_project python "%BROKEN_TEST%"
    
    echo.
    echo ========================================
    echo           SUCCESS - Setup Complete!
    echo ========================================
    pause
) else (
    echo.
    echo ========================================
    echo [INFO] conda not in PATH. Use Anaconda Prompt:
    echo 1. Start Menu --^> "Anaconda Prompt"
    echo 2. cd %PROJECT_DIR%
    echo 3. scripts\setup_env.bat
    echo ========================================
    pause
)
