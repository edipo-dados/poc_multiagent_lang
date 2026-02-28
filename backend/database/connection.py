"""
Database connection management with async SQLAlchemy.

Provides async engine and session factory for PostgreSQL with pgvector.
"""

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

# Database URL from environment variable
# Suporta PostgreSQL (produção) e SQLite (desenvolvimento local)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./regulatory_ai.db"  # SQLite por padrão para dev local
)

# Ajustar configurações baseado no tipo de banco
is_sqlite = "sqlite" in DATABASE_URL.lower()

# Create async engine
engine_kwargs = {
    "echo": False,  # Set to True for SQL query logging
}

if not is_sqlite:
    # Configurações específicas para PostgreSQL
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
        "poolclass": NullPool if "pytest" in os.environ.get("_", "") else None,
    })

engine = create_async_engine(DATABASE_URL, **engine_kwargs)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_session() -> AsyncSession:
    """
    Dependency for FastAPI endpoints to get database session.
    
    Usage:
        @app.get("/endpoint")
        async def endpoint(session: AsyncSession = Depends(get_session)):
            # Use session here
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
