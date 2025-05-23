# app/db.py

from __future__ import annotations

from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine

_SQLITE_URL = "sqlite+aiosqlite:///evals.db"

engine: AsyncEngine = create_async_engine(
    _SQLITE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

async_session = async_sessionmaker(engine, expire_on_commit=False)


async def init_db() -> None:
    """Create tables if they don't exist."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
