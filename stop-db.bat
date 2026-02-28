@echo off
echo Parando PostgreSQL...
docker compose -f docker-compose-db-only.yml down
echo ✓ PostgreSQL parado
