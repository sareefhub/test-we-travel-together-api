from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.user_model import User
from app.schemas.authentication_schema import UserRead
from app.core.security import get_current_user
from app.database import get_session

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[UserRead])
async def list_users(
    session: AsyncSession = Depends(get_session),
    current=Depends(get_current_user),
):
    stmt = select(User)
    result = await session.exec(stmt)
    return result.all()
