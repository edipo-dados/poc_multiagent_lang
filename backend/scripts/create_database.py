"""
Create regulatory_ai database in PostgreSQL.
"""

import asyncio
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


async def create_database():
    """Create regulatory_ai database."""
    
    # Connect to default postgres database
    admin_url = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
    
    print("Conectando ao PostgreSQL...")
    
    try:
        engine = create_async_engine(admin_url, isolation_level="AUTOCOMMIT")
        
        async with engine.connect() as conn:
            # Check if database exists
            result = await conn.execute(text("SELECT 1 FROM pg_database WHERE datname='regulatory_ai'"))
            exists = result.scalar()
            
            if exists:
                print("✓ Banco 'regulatory_ai' já existe")
            else:
                print("Criando banco 'regulatory_ai'...")
                await conn.execute(text("CREATE DATABASE regulatory_ai"))
                print("✓ Banco criado com sucesso!")
        
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"✗ Erro: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(create_database())
    if success:
        print("\nAgora execute: python backend/scripts/setup_database.py")
