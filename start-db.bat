@echo off
echo Iniciando PostgreSQL com pgvector no Docker...
docker compose -f docker-compose-db-only.yml up -d

echo.
echo Aguardando banco inicializar...
timeout /t 5 /nobreak >nul

echo.
echo ✓ PostgreSQL rodando em localhost:5432
echo   Usuario: postgres
echo   Senha: postgres
echo   Banco: regulatory_ai
echo.
echo Agora execute: python backend/scripts/setup_database.py
