# app/routers/v1/authentication_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserRead, Token
from app.core.security import create_access_token

router = APIRouter(
    prefix="/authentication",
    tags=["authentication"],
)

@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    payload: UserCreate,
    session: AsyncSession = Depends(get_session),
):
    hashed = payload.password + "_notreallyhashed"
    user = User(
        username=payload.username,
        phone=payload.phone,
        email=payload.email,
        citizen_id=payload.citizen_id,
        hashed_password=hashed,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@router.post(
    "/login",
    response_model=Token,
)
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
    return Token(access_token=access_token, token_type="bearer")
