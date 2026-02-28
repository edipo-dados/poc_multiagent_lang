@echo off
echo ========================================
echo Iniciando Regulatory AI POC (Local)
echo ========================================
echo.

REM Carregar .env
if exist .env (
    for /f "tokens=1,2 delims==" %%a in (.env) do (
        set %%a=%%b
    )
)

echo 1. Verificando PostgreSQL...
docker compose -f docker-compose-db-only.yml ps | findstr "regulatory_ai_db" >nul
if %ERRORLEVEL% NEQ 0 (
    echo PostgreSQL nao esta rodando. Iniciando...
    call start-db.bat
) else (
    echo ✓ PostgreSQL ja esta rodando
)

echo.
echo 2. Iniciando Backend...
start "Backend" cmd /k "cd backend && set PYTHONPATH=%CD%\.. && python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo.
echo 3. Iniciando Frontend...
start "Frontend" cmd /k "cd frontend && python -m streamlit run app.py"

echo.
echo ========================================
echo ✓ Todos os servicos iniciados!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:8501
echo Docs API: http://localhost:8000/docs
echo.
echo Pressione qualquer tecla para sair...
pause >nul
