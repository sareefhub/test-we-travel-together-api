# tests/test_authentication.py

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import status
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_session

# 1) use SQLModel’s async engine
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)

# 2) make the sessionmaker yield SQLModel’s AsyncSession
AsyncSessionLocal = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

@pytest.fixture(autouse=True, scope="module")
async def setup_db():
    # create tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    # drop tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"

@pytest.fixture
async def async_session():
    async with AsyncSessionLocal() as session:
        yield session

@pytest.fixture(autouse=True)
def override_get_session(async_session):
    app.dependency_overrides[get_session] = lambda: async_session
    yield
    app.dependency_overrides.clear()

@pytest.mark.anyio
async def test_register_and_login(async_session):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # register
        payload = {
            "username": "testuser",
            "password": "secret",
            "phone": "0812345678",
            "email": "test@example.com",
            "citizen_id": "1234567890123",
        }
        resp = await ac.post("/v1/authentication/register", json=payload)
        assert resp.status_code == status.HTTP_201_CREATED

        # login success
        resp2 = await ac.post(
            "/v1/authentication/login",
            data={"username": "testuser", "password": "secret"},
        )
        assert resp2.status_code == status.HTTP_200_OK

        # login failure
        resp3 = await ac.post(
            "/v1/authentication/login",
            data={"username": "testuser", "password": "wrongpass"},
        )
        assert resp3.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp3.json()["detail"] == "Invalid credentials"
