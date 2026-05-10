@echo off
setlocal

cd /d "%~dp0"

set "PYTHON=%~dp0venv\Scripts\python.exe"
set "LOGIN_URL=http://127.0.0.1:8000/accounts/login/"

if not exist "%PYTHON%" (
    echo Errore: non trovo il virtual environment in venv\Scripts\python.exe
    echo Controlla che il venv sia presente nella cartella del progetto.
    pause
    exit /b 1
)

echo Avvio il server Django...
start "Django GMR" "%PYTHON%" manage.py runserver

timeout /t 3 /nobreak >nul

start "" "%LOGIN_URL%"

echo.
echo Server avviato.
echo Pagina di login aperta: %LOGIN_URL%
echo.
echo Nota: il login avviene con l'utente che il browser usa gia' di default,
echo oppure con l'utente che inserirai manualmente nella pagina.
echo.
pause