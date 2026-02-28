#!/usr/bin/env python3
"""
Script inline para popular embeddings - pode ser copiado direto para o container
"""

import asyncio
import asyncpg
from pathlib import Path
from sentence_transformers import SentenceTransformer

async def main():
    print("🔄 Populando embeddings...")
    
    # Inicializar modelo
    print("📦 Carregando modelo de embeddings...")
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    
    # Conectar ao banco
    print("🔌 Conectando ao banco...")
    conn = await asyncpg.connect(
        host="postgres",
        port=5432,
        database="regulatory_ai",
        user="postgres",
        password="postgres"
    )
    
    # Arquivos para processar
    repo_path = Path("/app/fake_pix_repo")
    files = [
        "api/endpoints.py",
        "api/schemas.py",
        "domain/models.py",
        "domain/validators.py",
        "database/models.py",
    ]
    
    for file_path in files:
        full_path = repo_path / file_path
        if not full_path.exists():
            print(f"⚠️  Não encontrado: {file_path}")
            continue
        
        print(f"📄 Processando: {file_path}")
        
        # Ler conteúdo
        content = full_path.read_text(encoding='utf-8')
        
        # Gerar embedding
        embedding = model.encode(content)
        embedding_list = embedding.tolist()
        
        # Salvar no banco
        await conn.execute("""
            INSERT INTO code_embeddings (file_path, content, embedding)
            VALUES ($1, $2, $3::vector)
            ON CONFLICT (file_path) 
            DO UPDATE SET 
                content = EXCLUDED.content,
                embedding = EXCLUDED.embedding,
                updated_at = NOW()
        """, file_path, content, embedding_list)
        
        print(f"   ✅ Salvo ({len(embedding)} dims)")
    
    # Verificar
    count = await conn.fetchval("SELECT COUNT(*) FROM code_embeddings")
    print(f"\n✅ Total: {count} embeddings")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
