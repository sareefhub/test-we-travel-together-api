from contextlib import asynccontextmanager
from fastapi import FastAPI
import app.models as models
from app.routers import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: สร้างตารางก่อน
    await models.init_db()
    yield
    # Shutdown: (ถ้ามี cleanup)

app = FastAPI(lifespan=lifespan)
app.include_router(router)
