"""
Setup PostgreSQL database with pgvector extension and tables.
"""

import asyncio
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from backend.database.models import Base


async def setup_database():
    """Create database, extension, and tables."""
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost:5432/regulatory_ai")
    
    print(f"Connecting to: {database_url.split('@')[1]}")  # Hide password
    
    try:
        # Create engine
        engine = create_async_engine(database_url, echo=True)
        
        # Create pgvector extension
        async with engine.begin() as conn:
            print("\nCreating pgvector extension...")
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            print("✓ pgvector extension created")
        
        # Create all tables
        async with engine.begin() as conn:
            print("\nCreating tables...")
            await conn.run_sync(Base.metadata.create_all)
            print("✓ Tables created")
        
        print("\n✓ Database setup completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Verifique se o PostgreSQL está rodando")
        print("2. Verifique se a senha está correta no arquivo .env")
        print("3. Crie o banco manualmente: CREATE DATABASE regulatory_ai;")
        return False
    
    return True


if __name__ == "__main__":
    # Load .env file
    from pathlib import Path
    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value
    
    asyncio.run(setup_database())
