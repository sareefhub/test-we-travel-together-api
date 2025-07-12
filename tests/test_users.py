# tests/test_users.py

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
from app.core.security import get_current_user
from app.models.user_model import User
from app.routers.v1.user_router import router as users_router
from app.schemas.user_schema import UserRead

# 0) Mount the users_router temporarily
@pytest.fixture(autouse=True, scope="session")
def include_users_router():
    app.include_router(users_router)
    yield

# 1) Mock authentication for protected endpoints
@pytest.fixture(autouse=True)
def override_auth():
    # Simulate a logged-in user with id=1
    app.dependency_overrides[get_current_user] = lambda: User(id=1, username="admin")
    yield
    app.dependency_overrides.pop(get_current_user, None)

# 2) In-memory async DB setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(
    TEST_DATABASE_URL, echo=False, connect_args={"check_same_thread": False}
)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(autouse=True, scope="module")
async def setup_db():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

@pytest.fixture
async def async_session():
    async with AsyncSessionLocal() as session:
        yield session

@pytest.fixture(autouse=True)
def override_session(async_session):
    app.dependency_overrides[get_session] = lambda: async_session
    yield
    app.dependency_overrides.pop(get_session, None)

@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"

BASE = "/users"

@pytest.mark.anyio
async def test_user_crud(async_session):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # --- Create first user ---
        payload1 = {
            "username": "user1",
            "phone": "0812345678",
            "email": "user1@example.com",
            "citizen_id": "4816447203381",
            "password": "secret1"
        }
        r1 = await client.post(f"{BASE}/", json=payload1)
        assert r1.status_code == status.HTTP_201_CREATED
        user1 = UserRead.model_validate(r1.json())
        assert user1.username == "user1"
        assert user1.email == "user1@example.com"

        # --- Fail on duplicate username/email ---
        r_dup = await client.post(f"{BASE}/", json=payload1)
        assert r_dup.status_code == status.HTTP_400_BAD_REQUEST

        # --- List users (requires auth) ---
        r_list = await client.get(f"{BASE}/")
        assert r_list.status_code == status.HTTP_200_OK
        users = [UserRead.model_validate(u) for u in r_list.json()]
        assert any(u.username == "user1" for u in users)

        # --- Update user (PATCH) ---
        update_payload = {"phone": "0999999999", "password": "newpass"}
        r_patch = await client.patch(f"{BASE}/{user1.id}", json=update_payload)
        assert r_patch.status_code == status.HTTP_200_OK
        patched = UserRead.model_validate(r_patch.json())
        assert patched.phone == "0999999999"
        # password isn't returned in response model

        # --- Delete user ---
        r_del = await client.delete(f"{BASE}/{user1.id}")
        assert r_del.status_code == status.HTTP_204_NO_CONTENT

        # --- Confirm deletion ---
        r_get = await client.get(f"{BASE}/{user1.id}")
        # There's no GET /users/{id} endpoint, so expect 404 on listing that id via list filter:
        # We check list to ensure user1 is gone:
        r_list2 = await client.get(f"{BASE}/")
        remaining = [u["id"] for u in r_list2.json()]
        assert user1.id not in remaining
