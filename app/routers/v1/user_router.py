# app/routers/v1/user_router.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserRead, UserUpdate
from app.core.security import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    payload: UserCreate,
    session: AsyncSession = Depends(get_session),
):

    exists = await session.exec(
        select(User).where(
            (User.username == payload.username) | (User.email == payload.email)
        )
    )
    if exists.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )

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


@router.get(
    "/",
    response_model=List[UserRead],
    dependencies=[Depends(get_current_user)],
)
async def list_users(
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(select(User))
    return result.all()


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    dependencies=[Depends(get_current_user)],
)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    session: AsyncSession = Depends(get_session),
):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    data = payload.model_dump(exclude_unset=True)
    if "password" in data:
        user.hashed_password = data.pop("password") + "_notreallyhashed"

    for key, val in data.items():
        setattr(user, key, val)

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_user)],
)
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await session.delete(user)
    await session.commit()
