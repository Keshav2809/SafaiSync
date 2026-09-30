@echo off
title SafaiSync

cd /d "%~dp0"

echo =====================================
echo        Starting SafaiSync...
echo =====================================
echo.

if not exist "venv\Scripts\python.exe" (
    echo First time setup...
    python -m venv venv
    echo.
    echo Installing required packages...
    venv\Scripts\python.exe -m pip install -r requirements.txt
    echo.
)

echo Checking database...
venv\Scripts\python.exe manage.py migrate

echo.
echo Starting SafaiSync server...
echo.

start "" http://127.0.0.1:8000/

venv\Scripts\python.exe manage.py runserver

pause