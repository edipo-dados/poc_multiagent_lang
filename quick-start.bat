@echo off
echo ========================================
echo Regulatory AI POC - Quick Start
echo ========================================
echo.

echo [1/5] Parando containers antigos...
docker-compose down

echo.
echo [2/5] Construindo e iniciando servicos...
docker-compose up -d --build

echo.
echo [3/5] Aguardando servicos iniciarem (30s)...
timeout /t 30 /nobreak

echo.
echo [4/5] Verificando status dos containers...
docker ps

echo.
echo [5/5] Verificando saude do backend...
curl http://localhost:8000/health

echo.
echo ========================================
echo Servicos iniciados!
echo ========================================
echo.
echo Frontend: http://localhost:8501
echo Backend:  http://localhost:8000
echo.
echo Para ver logs do backend:
echo   docker logs multi-agent-ia-backend-1 -f
echo.
pause
