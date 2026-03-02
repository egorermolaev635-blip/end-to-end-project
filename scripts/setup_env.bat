@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title Data Science Project Setup
echo ========================================
echo Data Science Project Environment Setup
echo ========================================

REM Auto-detect required files
set "BROKEN_TEST="
set "REQ_FILE="
set "PROJECT_DIR="

REM Check current directory first
if exist "broken_env.py" (
    set "BROKEN_TEST=%CD%\broken_env.py"
    set "REQ_FILE=%CD%\requirements.txt"
    set "PROJECT_DIR=%CD%"
    goto :files_found
)

REM Search in parent directories (max 3 levels up)
echo [INFO] Searching for project files...
set MAX_DEPTH=3
set CURRENT_DIR=%CD%
:search_loop
if %MAX_DEPTH%==0 goto :no_files
if exist "%CURRENT_DIR%\broken_env.py" (
    if exist "%CURRENT_DIR%\requirements.txt" (
        set "BROKEN_TEST=%CURRENT_DIR%\broken_env.py"
        set "REQ_FILE=%CURRENT_DIR%\requirements.txt"
        set "PROJECT_DIR=%CURRENT_DIR%"
        goto :files_found
    )
)
cd ..
set /a MAX_DEPTH-=1
set "CURRENT_DIR=%CD%"
if not "%CURRENT_DIR%"=="%~dp0.." goto :search_loop

:no_files
echo.
echo [ERROR] broken_env.py not found!
echo Current directory: %CD%
echo Searching nearby...
dir /s /b broken_env.py 2>nul || echo No matches found.
echo.
echo Please ensure you're running this from project root.
pause
exit /b 1

:files_found
echo.
echo ========================================
echo [OK] Files located:
echo Project directory: %PROJECT_DIR%
echo broken_env.py: %BROKEN_TEST%
echo requirements.txt: %REQ_FILE%
echo ========================================

REM Check conda
where conda >nul 2>nul
if !errorlevel! neq 0 (
    echo.
    echo ========================================
    echo [WARNING] conda not found - use Anaconda Prompt:
    echo 1. Win+R ^> "Anaconda Prompt"
    echo 2. cd /d "%PROJECT_DIR%"
    echo 3. scripts\setup_env.bat
    echo ========================================
    pause
    exit /b 0
)

echo [INFO] Checking ds_project environment...
conda env list | findstr /C:"ds_project" >nul 2>nul
if !errorlevel!==0 (
    echo [OK] ds_project environment exists
) else (
    echo [INFO] Creating ds_project environment...
    call conda create -n ds_project python=3.11 -y
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to create environment
        pause
        exit /b 1
    )
)

echo [INFO] Installing packages...
call conda run -n ds_project pip install -r "%REQ_FILE%"
if !errorlevel! neq 0 (
    echo [ERROR] Package installation failed
    pause
    exit /b 1
)

echo [INFO] Running smoke test...
call conda run -n ds_project python "%BROKEN_TEST%"
if !errorlevel! neq 0 (
    echo [WARNING] Smoke test failed
) else (
    echo [OK] Smoke test passed!
)

echo.
echo ========================================
echo           SUCCESS - Setup Complete!
echo ========================================
echo Environment: ds_project (Python 3.11)
echo Activate: conda activate ds_project
echo Project: %PROJECT_DIR%
pause

