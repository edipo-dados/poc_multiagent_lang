@echo off
echo ========================================
echo   Iniciando Backend (FastAPI)
echo ========================================
echo.

cd backend
call venv\Scripts\activate.bat

REM Configurar variáveis de ambiente
set DATABASE_URL=postgresql://postgres:postgres@localhost:5432/regulatory_ai
set PIX_REPO_PATH=../fake_pix_repo

echo Backend rodando em: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.

REM Iniciar servidor
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
