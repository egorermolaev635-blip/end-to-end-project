@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title Data Project Setup

echo ========================================
echo Data Science Project Environment Setup  
echo ========================================


set ENV_NAME=ds_project
set PYTHON_VER=3.11

:: Пути к файлам
set REQ_FILE=%~dp0..\requirements.txt
set BROKEN_TEST=%~dp0..\broken_env.py

:: Найти conda
set CONDA_EXE=
for /f "delims=" %%i in ('where conda 2^>nul') do set CONDA_EXE=%%i
if "%CONDA_EXE%"=="" (
    echo [ERROR] conda not found! Установи Anaconda.
    echo https://www.anaconda.com/download
    pause
    exit /b 1
)

echo [OK] conda: %CONDA_EXE%

:: Проверка окружения
conda env list | findstr /C:"%ENV_NAME% " >nul 2>&1
if !errorlevel! equ 0 (
    echo [OK] %ENV_NAME% exists
) else (
    echo [INFO] Creating %ENV_NAME%...
    call "%CONDA_EXE%" create -n %ENV_NAME% python=%PYTHON_VER% -y
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to create env
        pause
        exit /b 1
    )
)

:: Установка зависимостей
echo [INFO] Installing requirements...
call "%CONDA_EXE%" run -n %ENV_NAME% pip install -r "%REQ_FILE%"
if !errorlevel! neq 0 (
    echo [ERROR] Failed pip install
    pause
    exit /b 1
)
echo [OK] Requirements OK

:: SMOKE TEST
echo [INFO] Testing broken_env.py...
call "%CONDA_EXE%" run -n %ENV_NAME% python "%BROKEN_TEST%"
if !errorlevel! equ 0 (
    echo.
    echo ========================================
    echo           ✅ SETUP COMPLETE [OK]
    echo ========================================
    pause
) else (
    echo [ERROR] Smoke test FAILED!
    pause
    exit /b 1
)
