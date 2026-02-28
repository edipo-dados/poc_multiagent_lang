@echo off
echo ========================================
echo   Iniciando Frontend (Streamlit)
echo ========================================
echo.

REM Criar venv do frontend se não existir
if not exist "frontend\venv" (
    echo Criando ambiente virtual do frontend...
    cd frontend
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    cd ..
) else (
    cd frontend
    call venv\Scripts\activate.bat
    cd ..
)

cd frontend

REM Configurar variável de ambiente
set BACKEND_URL=http://localhost:8000

echo Frontend rodando em: http://localhost:8501
echo.

REM Iniciar Streamlit
streamlit run app.py
