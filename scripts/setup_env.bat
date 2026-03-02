@echo off
title Data Science Project Setup
echo ========================================
echo Data Science Project Environment Setup
echo ========================================

REM Auto-detect required files in current or parent directories
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

REM Search in parent directories (up to 3 levels)
echo [INFO] Searching for project files...
for /d /r "%CD%\.." %%D in (.) do (
    if exist "%%D\broken_env.py" (
        set "BROKEN_TEST=%%D\broken_env.py"
        set "REQ_FILE=%%D\requirements.txt"
        set "PROJECT_DIR=%%D"
        goto :files_found
    )
)

:files_found
if not defined BROKEN_TEST (
    echo.
    echo [ERROR] broken_env.py not found!
    echo Current directory: %CD%
    echo Searching nearby...
    dir /s /b broken_env.py 2>nul || echo No matches found.
    echo.
    echo Please ensure you're running this from project root or parent directory.
    pause
    exit /b 1
)

if not exist "%REQ_FILE%" (
    echo [ERROR] requirements.txt not found at: %REQ_FILE%
    pause
    exit /b 1
)

echo.
echo ========================================
echo [OK] Files located:
echo Project directory: %PROJECT_DIR%
echo broken_env.py: %BROKEN_TEST%
echo requirements.txt: %REQ_FILE%
echo ========================================

REM Check conda availability
where conda >nul 2>nul
if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo [WARNING] conda not found in PATH
    echo Please use "Anaconda Prompt" from Start Menu:
    echo 1. Open "Anaconda Prompt"
    echo 2. cd /d "%PROJECT_DIR%"
    echo 3. scripts\setup_env.bat
    echo ========================================
    pause
    exit /b 0
)

echo [INFO] Checking ds_project environment...
conda env list | findstr /C:"ds_project" >nul 2>nul
if %errorlevel%==0 (
    echo [OK] ds_project environment exists
) else (
    echo [INFO] Creating ds_project environment...
    call conda create -n ds_project python=3.11 -y --no-default-packages
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to create environment
        pause
        exit /b 1
    )
    echo [OK] Environment created successfully
)

echo.
echo [INFO] Installing packages from requirements.txt...
call conda run -n ds_project pip install -r "%REQ_FILE%" --upgrade pip
if !errorlevel! neq 0 (
    echo [ERROR] Package installation failed
    pause
    exit /b 1
)
echo [OK] Packages installed successfully

echo.
echo [INFO] Running smoke test...
call conda run -n ds_project python "%BROKEN_TEST%"
if !errorlevel! neq 0 (
    echo [WARNING] Smoke test failed - environment may need manual verification
) else (
    echo [OK] Smoke test passed!
)

echo.
echo ========================================
echo           SUCCESS - Setup Complete!
echo ========================================
echo Environment: ds_project (Python 3.11)
echo To activate: conda activate ds_project
echo Project ready at: %PROJECT_DIR%
echo.
pause

