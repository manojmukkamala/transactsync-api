import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .models import Account, Cycle, EmailCheckpoint, Transaction

# Database configuration
DATABASE_URL = os.getenv(
    'DATABASE_URL', 'postgresql://transactsync:transactsync@localhost:5432/transactsync'
)
ASYNC_DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://')

# Create async database engine
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)

# Create async session factory
async_session_local = async_sessionmaker(
    bind=async_engine,
    autocommit=False,
    autoflush=False,
)


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession]:
    """
    Get an async database session.
    Yields:
        AsyncSession: An async SQLModel session for database operations.
    """
    async with async_session_local() as session:
        yield session


async def init_db() -> None:
    """Initialize the database and create tables if they don't exist"""
    # Use SQLModel to create tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Account.metadata.create_all)
        await conn.run_sync(Transaction.metadata.create_all)
        await conn.run_sync(EmailCheckpoint.metadata.create_all)
        await conn.run_sync(Cycle.metadata.create_all)
