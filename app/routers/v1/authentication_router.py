# app/routers/v1/authentication_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.models.user_model import User
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    username: str,
    email: str,
    password: str,
    session: AsyncSession = Depends(get_session),
):
    hashed = password + "_notreallyhashed"
    user = User(username=username, email=email, hashed_password=hashed)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return {"id": user.id, "username": user.username}

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(
        select(User).where(User.username == form_data.username)
    )
    user = result.first()
    if not user or (form_data.password + "_notreallyhashed") != user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
