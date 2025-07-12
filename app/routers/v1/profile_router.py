# app/routers/v1/profile_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.models.profile_model import Profile
from app.models.province_model import Province
from app.schemas.profile_schema import ProfileCreate, ProfileRead, ProfileUpdate
from app.core.security import get_current_user

router = APIRouter(
    prefix="/profile",
    tags=["profile"],
    dependencies=[Depends(get_current_user)],
)

@router.get("/", response_model=ProfileRead)
async def read_profile(
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(Profile)
        .where(Profile.user_id == current_user.id)
        .options(selectinload(Profile.target_province))
    )
    profile = (await session.exec(stmt)).first()
    if not profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Profile not found")
    return profile

@router.post("/", response_model=ProfileRead, status_code=status.HTTP_201_CREATED)
async def create_profile(
    data: ProfileCreate,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    existing = await session.exec(
        select(Profile).where(Profile.user_id == current_user.id)
    )
    if existing.first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Profile already exists")

    profile = Profile(user_id=current_user.id, **data.model_dump(exclude_unset=True))
    session.add(profile)

    if profile.target_province_id:
        prov = await session.get(Province, profile.target_province_id)
        prov.is_target = True
        session.add(prov)

    await session.commit()
    await session.refresh(profile, options=[selectinload(Profile.target_province)])
    return profile

@router.patch("/", response_model=ProfileRead)
async def update_profile(
    data: ProfileUpdate,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(
        select(Profile).where(Profile.user_id == current_user.id)
    )
    profile = result.first()
    if not profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Profile not found")

    updates = data.model_dump(exclude_unset=True)
    old_id = profile.target_province_id
    new_id = updates.get("target_province_id")

    if old_id and old_id != new_id:
        old = await session.get(Province, old_id)
        old.is_target = False
        session.add(old)
    if new_id:
        new = await session.get(Province, new_id)
        new.is_target = True
        session.add(new)

    for k, v in updates.items():
        setattr(profile, k, v)

    session.add(profile)
    await session.commit()
    await session.refresh(profile, options=[selectinload(Profile.target_province)])
    return profile

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(
        select(Profile).where(Profile.user_id == current_user.id)
    )
    profile = result.first()
    if not profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Profile not found")

    if profile.target_province_id:
        prov = await session.get(Province, profile.target_province_id)
        prov.is_target = False
        session.add(prov)

    await session.delete(profile)
    await session.commit()
