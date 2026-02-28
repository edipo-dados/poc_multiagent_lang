@echo off
echo ========================================
echo Setup PostgreSQL para Regulatory AI POC
echo ========================================
echo.

REM Configurações padrão do PostgreSQL
set PGHOST=localhost
set PGPORT=5432
set PGUSER=postgres

echo Por favor, digite a senha do usuário postgres:
set /p PGPASSWORD=Senha: 

echo.
echo Criando banco de dados e tabelas...
psql -U %PGUSER% -h %PGHOST% -p %PGPORT% -f setup-postgres.sql

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ Banco de dados configurado com sucesso!
    echo.
    echo Configuração da DATABASE_URL:
    echo DATABASE_URL=postgresql+asyncpg://%PGUSER%:%PGPASSWORD%@%PGHOST%:%PGPORT%/regulatory_ai
    echo.
    echo Salve esta URL em um arquivo .env ou use como variável de ambiente
) else (
    echo.
    echo ✗ Erro ao configurar banco de dados
    echo Verifique se o PostgreSQL está rodando e se a senha está correta
)

pause
