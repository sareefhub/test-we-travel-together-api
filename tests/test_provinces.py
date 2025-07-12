# tests/test_provinces.py

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
from app.routers.v1.province_router import router as provinces_router

# mount provinces_router ชั่วคราว
@pytest.fixture(autouse=True, scope="session")
def include_provinces():
    app.include_router(provinces_router)
    yield

# mock authentication
@pytest.fixture(autouse=True)
def override_auth():
    app.dependency_overrides[get_current_user] = lambda: User(id=1, username="test")
    yield
    app.dependency_overrides.pop(get_current_user, None)

# in-memory async DB setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(autouse=True, scope="module")
async def setup_db():
    # create all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    # drop all tables
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

BASE = "/provinces"

@pytest.mark.anyio
async def test_crud_province(async_session):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1) Create first province
        single = {"name": "กรุงเทพ", "category": "primary", "discount_rate": "10%"}
        r = await client.post(f"{BASE}/", json=single)
        if r.status_code != status.HTTP_201_CREATED:
            print("CREATE ERROR:", r.status_code, r.json())
        assert r.status_code == status.HTTP_201_CREATED

        payload = r.json()
        arr = payload if isinstance(payload, list) else [payload]
        assert len(arr) == 1
        p1 = arr[0]
        assert p1["name"] == "กรุงเทพ"
        pid = p1["id"]

        # 2) Create second province
        second = {"name": "เชียงใหม่", "category": "secondary", "discount_rate": "5%"}
        r2 = await client.post(f"{BASE}/", json=second)
        assert r2.status_code == status.HTTP_201_CREATED
        payload2 = r2.json()
        arr2 = payload2 if isinstance(payload2, list) else [payload2]
        assert arr2[0]["name"] == "เชียงใหม่"

        # 3) List all provinces
        r3 = await client.get(f"{BASE}/")
        assert r3.status_code == status.HTTP_200_OK
        allp = r3.json()
        assert any(p["name"] == "กรุงเทพ" for p in allp)
        assert any(p["name"] == "เชียงใหม่" for p in allp)

        # 4) Read existing province
        r4 = await client.get(f"{BASE}/{pid}")
        assert r4.status_code == status.HTTP_200_OK
        assert r4.json()["name"] == "กรุงเทพ"

        # 5) Read non-existing province
        r5 = await client.get(f"{BASE}/9999")
        assert r5.status_code == status.HTTP_404_NOT_FOUND

        # 6) Replace via PUT
        upd = {"name": "กทม", "category": "primary", "discount_rate": "0%"}
        r6 = await client.put(f"{BASE}/{pid}", json=upd)
        assert r6.status_code == status.HTTP_200_OK
        assert r6.json()["name"] == "กทม"

        # 7) Partial update via PATCH
        r7 = await client.patch(f"{BASE}/{pid}", json={"discount_rate": "20%"})
        assert r7.status_code == status.HTTP_200_OK
        assert r7.json()["discount_rate"] == "20%"

        # 8) Delete province
        r8 = await client.delete(f"{BASE}/{pid}")
        assert r8.status_code == status.HTTP_204_NO_CONTENT

        # 9) Confirm deletion
        r9 = await client.get(f"{BASE}/{pid}")
        assert r9.status_code == status.HTTP_404_NOT_FOUND
