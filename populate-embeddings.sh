#!/bin/bash
# Populate embeddings in database - wrapper script for Docker

echo "🔄 Populating embeddings in database..."
echo ""

# Run the populate script inside the backend container
docker compose exec backend python /app/backend/scripts/populate_embeddings_sync.py

echo ""
echo "✅ Done! Check output above for results."
