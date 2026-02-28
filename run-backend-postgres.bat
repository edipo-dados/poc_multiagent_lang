@echo off
echo Iniciando backend com PostgreSQL...

REM Carregar variáveis do .env
if exist .env (
    for /f "tokens=1,2 delims==" %%a in (.env) do (
        set %%a=%%b
    )
)

cd backend
set PYTHONPATH=%CD%\..
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
