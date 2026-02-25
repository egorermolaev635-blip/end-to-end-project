@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title Setup

echo Проверяем conda...

REM ИНИЦИАЛИЗИРУЕМ CONDA
call C:\Users\egore\anaconda3\Scripts\activate.bat base >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Anaconda не найдена по пути C:\Users\egore\anaconda3
    echo Установи Anaconda или исправь путь
    pause
    exit /b 1
)

set ENV_NAME=ds_project
set PYTHON_VER=3.11

echo [OK] Conda работает
echo Создаём %ENV_NAME%...

REM ПРОВЕРКА ENV
conda env list | findstr /C:"%ENV_NAME% " >nul
if !errorlevel! equ 0 (
    echo [OK] %ENV_NAME% уже есть
) else (
    conda create -n %ENV_NAME% python=%PYTHON_VER% -y
)

REM УСТАНОВКА ПАКЕТОВ
conda run -n %ENV_NAME% pip install -r ..\requirements.txt

REM SMOKE TEST
echo Тестируем...
conda run -n %ENV_NAME% python ..\broken_env.py

echo.
echo ========================================
echo ✅ SETUP COMPLETE [OK]  
echo ========================================
pause
