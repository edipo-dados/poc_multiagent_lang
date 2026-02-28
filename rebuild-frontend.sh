#!/bin/bash
# Rebuild frontend container with latest code changes

echo "🔄 Rebuilding frontend container..."
echo ""

# Stop and remove frontend container
echo "1. Stopping frontend container..."
docker compose down frontend

# Rebuild with no cache
echo ""
echo "2. Rebuilding frontend image (no cache)..."
docker compose build --no-cache frontend

# Start frontend
echo ""
echo "3. Starting frontend..."
docker compose up -d frontend

# Wait a bit for startup
echo ""
echo "⏳ Waiting for frontend to start..."
sleep 5

# Check status
echo ""
echo "✅ Frontend status:"
docker compose ps frontend

echo ""
echo "📊 Frontend logs (last 20 lines):"
docker compose logs frontend --tail=20

echo ""
echo "🎉 Frontend rebuild complete!"
echo "🌐 Access at: http://localhost:8501"
