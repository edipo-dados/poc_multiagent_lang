@echo off
echo Parando processos Python existentes...
taskkill /F /IM python.exe /T 2>nul

echo.
echo Aguardando 2 segundos...
timeout /t 2 /nobreak >nul

echo.
echo Iniciando backend...
cd backend
set PYTHONPATH=%CD%\..
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
