@echo off
echo ========================================
echo   Regulatory AI POC - Local Setup
echo ========================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado! Instale Python 3.11+
    pause
    exit /b 1
)

REM Verificar se PostgreSQL está rodando
echo Verificando PostgreSQL...
pg_isready -h localhost -p 5432 >nul 2>&1
if errorlevel 1 (
    echo [AVISO] PostgreSQL nao esta rodando!
    echo Por favor, inicie o PostgreSQL ou use SQLite para testes
    echo.
)

REM Criar ambiente virtual se não existir
if not exist "backend\venv" (
    echo Criando ambiente virtual...
    cd backend
    python -m venv venv
    cd ..
)

REM Ativar ambiente virtual e instalar dependências
echo Instalando dependencias...
cd backend
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements-local.txt
cd ..

echo.
echo ========================================
echo   Setup concluido!
echo ========================================
echo.
echo Para iniciar a aplicacao:
echo   1. Backend:  run-backend.bat
echo   2. Frontend: run-frontend.bat
echo.
pause
