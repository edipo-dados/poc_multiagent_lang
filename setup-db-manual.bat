@echo off
echo ========================================
echo Setup PostgreSQL Database
echo ========================================
echo.

set PGPATH="C:\Program Files\PostgreSQL\18\bin\psql.exe"
set PGHOST=localhost
set PGPORT=5432
set PGUSER=postgres

echo Digite a senha do PostgreSQL:
set /p PGPASSWORD=

echo.
echo Criando banco de dados...
%PGPATH% -U %PGUSER% -h %PGHOST% -p %PGPORT% -c "CREATE DATABASE regulatory_ai;"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Criando extensao pgvector...
    %PGPATH% -U %PGUSER% -h %PGHOST% -p %PGPORT% -d regulatory_ai -c "CREATE EXTENSION IF NOT EXISTS vector;"
    
    echo.
    echo ✓ Banco configurado com sucesso!
    echo.
    echo Atualize o arquivo .env com sua senha:
    echo DATABASE_URL=postgresql+asyncpg://postgres:SUA_SENHA@localhost:5432/regulatory_ai
) else (
    echo.
    echo ✗ Erro ao criar banco
    echo Verifique se a senha esta correta
)

pause
