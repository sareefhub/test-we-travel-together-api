# app/database.py
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings

# ต้องขึ้นต้นด้วย sqlite+aiosqlite://
DATABASE_URL = settings.database_url

# สร้าง async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
)

# sessionmaker ที่คืน AsyncSession ของ SQLModel
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# dependency
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
