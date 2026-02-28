#!/bin/bash
# Check if embeddings exist in database

echo "🔍 Checking embeddings in database..."
echo ""

# Check if code_embeddings table exists and has data
docker compose exec -T postgres psql -U postgres -d regulatory_ai << 'EOF'
-- Check if table exists
SELECT 
    CASE 
        WHEN EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'code_embeddings'
        ) 
        THEN '✅ Table code_embeddings EXISTS'
        ELSE '❌ Table code_embeddings DOES NOT EXIST'
    END as table_status;

-- Count embeddings
SELECT 
    COUNT(*) as total_embeddings,
    COUNT(DISTINCT file_path) as unique_files
FROM code_embeddings;

-- Show sample files (if any)
SELECT file_path, LENGTH(content) as content_length
FROM code_embeddings
LIMIT 5;
EOF

echo ""
echo "📊 Analysis:"
echo "- If total_embeddings = 0: Need to populate embeddings"
echo "- If total_embeddings > 0: CodeReader should work!"
echo ""
echo "To populate embeddings, run:"
echo "  docker compose exec backend python -m backend.scripts.populate_embeddings_sync"
