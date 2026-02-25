@echo off
title Setup
echo ========================================
echo Data Science Project Environment Setup
echo ========================================

REM Find conda automatically
set CONDA_EXE=
for /f "delims=" %%i in ('where conda 2^>nul') do set CONDA_EXE=%%i

if "%CONDA_EXE%"=="" (
    echo [ERROR] conda not found in PATH
    echo Install Anaconda: https://www.anaconda.com/download
    echo Add to PATH: %%USERPROFILE%%\anaconda3\condabin
    pause
    exit /b 1
)

echo [OK] Found conda: %CONDA_EXE%

set ENV_NAME=ds_project
set PYTHON_VER=3.11

REM Check if environment exists
echo [INFO] Checking %ENV_NAME%...
%CONDA_EXE% env list | findstr /C:"%ENV_NAME% " >nul 2^>nul
if !errorlevel! equ 0 (
    echo [OK] %ENV_NAME% exists
) else (
    echo [INFO] Creating %ENV_NAME%...
    %CONDA_EXE% create -n %ENV_NAME% python=%PYTHON_VER% -y
    if errorlevel 1 (
        echo [ERROR] Failed to create environment
        pause
        exit /b 1
    )
)

REM Install packages
echo [INFO] Installing pandas...
%CONDA_EXE% run -n %ENV_NAME% pip install -r ..\requirements.txt

REM Smoke test
echo [INFO] Testing broken_env.py...
%CONDA_EXE% run -n %ENV_NAME% python ..\broken_env.py

echo.
echo ========================================
echo           OK - Setup Complete!
echo ========================================
pause
