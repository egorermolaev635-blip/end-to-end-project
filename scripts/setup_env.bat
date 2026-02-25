@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title Data Project Setup

echo ========================================
echo Data Science Project Environment Setup
echo ========================================

:: НАЙТИ CONDA АВТОМАТИЧЕСКИ
set CONDA_EXE=
for /f "delims=" %%i in ('where conda 2^>nul') do set CONDA_EXE=%%i

if "%CONDA_EXE%"=="" (
    echo [ERROR] conda not found in PATH
    echo 1. Установи Anaconda https://www.anaconda.com/download  
    echo 2. Добавь в PATH: %%USERPROFILE%%\anaconda3\condabin
    pause
    exit /b 1
)

echo [OK] Found conda: %CONDA_EXE%

set ENV_NAME=ds_project
set PYTHON_VER=3.11

:: ПРОВЕРИТЬ ENV
echo [INFO] Checking %ENV_NAME%...
%CONDA_EXE% env list | findstr /C:"%ENV_NAME% " >nul
if !errorlevel! equ 0 (
    echo [OK] %ENV_NAME% exists
) else (
    echo [INFO] Creating %ENV_NAME%...
    %CONDA_EXE% create -n %ENV_NAME% python=%PYTHON_VER% -y
)

:: УСТАНОВКА ПАКЕТОВ  
echo [INFO] Installing pandas...
%CONDA_EXE% run -n %ENV_NAME% pip install pandas numpy -r ..\requirements.txt

:: SMOKE TEST
echo [INFO] Testing broken_env.py...
%CONDA_EXE% run -n %ENV_NAME% python ..\broken_env.py

echo.
echo ========================================
echo           ✅ SETUP COMPLETE [OK]
echo ========================================
pause
