# tests/test_province_targets.py

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
from app.models.province_model import Province
from app.models.province_target_model import ProvinceTarget
from app.routers.v1.province_target_router import router as target_router
from app.schemas.province_target_schema import ProvinceTargetRead

# Mount the province_target router
@pytest.fixture(autouse=True, scope="session")
def include_target_router():
    app.include_router(target_router)
    yield

# Mock authentication
@pytest.fixture(autouse=True)
def override_auth():
    app.dependency_overrides[get_current_user] = lambda: User(id=1, username="tester")
    yield
    app.dependency_overrides.pop(get_current_user, None)

# In-memory DB setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(TEST_DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(autouse=True, scope="module")
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
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

BASE = "/profile/selections"

@ pytest.mark.anyio
async def test_selection_crud(async_session):
    # Pre-seed a province in DB
    province = Province(name="TestProv", category="primary", discount_rate="0%", is_primary=True, is_secondary=False)
    async_session.add(province)
    await async_session.commit()
    await async_session.refresh(province)
    prov_id = province.id

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1) Create selection
        r1 = await client.post(f"{BASE}/", json={"province_id": prov_id})
        assert r1.status_code == status.HTTP_201_CREATED
        sel = ProvinceTargetRead.model_validate(r1.json())
        assert sel.province_id == prov_id
        assert sel.user_id == 1
        selection_id = sel.id

        # 2) List selections
        r2 = await client.get(f"{BASE}/")
        assert r2.status_code == status.HTTP_200_OK
        arr = [ProvinceTargetRead.model_validate(x) for x in r2.json()]
        assert any(x.id == selection_id for x in arr)

        # 3) Delete selection
        r3 = await client.delete(f"{BASE}/{selection_id}")
        assert r3.status_code == status.HTTP_204_NO_CONTENT

        # 4) Confirm deletion
        r4 = await client.get(f"{BASE}/")
        assert r4.status_code == status.HTTP_200_OK
        assert not r4.json()
