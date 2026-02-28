@echo off
echo ========================================
echo   Iniciando Backend com SQLite
echo ========================================
echo.

REM Configurar PYTHONPATH para incluir o diretório raiz
set PYTHONPATH=%CD%

REM Configurar para usar SQLite
set USE_SQLITE=true
set DATABASE_URL=sqlite+aiosqlite:///./regulatory_ai.db
set PIX_REPO_PATH=./fake_pix_repo

echo Backend rodando em: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Banco de dados: SQLite (regulatory_ai.db)
echo PYTHONPATH: %PYTHONPATH%
echo.

REM Iniciar servidor do diretório raiz
cd backend
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
