from sqlmodel import SQLModel
from app.database import engine

async def init_db() -> None:
    """
    สร้างทุกตารางในฐานข้อมูล จาก SQLModel.metadata
    เรียกก่อนแอป FastAPI start ขึ้น
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
