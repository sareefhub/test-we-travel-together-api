# app/routers/v1/province_target_router.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.models.province_target_model import ProvinceTarget
from app.models.province_model import Province
from app.schemas.province_target_schema import ProvinceTargetCreate, ProvinceTargetRead
from app.core.security import get_current_user

router = APIRouter(
    prefix="/profile/selections",
    tags=["province_targets"],
    dependencies=[Depends(get_current_user)],
)

@router.post("/", response_model=ProvinceTargetRead, status_code=status.HTTP_201_CREATED)
async def create_selection(
    data: ProvinceTargetCreate,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    prov = await session.get(Province, data.province_id)
    if not prov:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Province not found")

    sel = ProvinceTarget(user_id=current_user.id, province_id=prov.id)
    session.add(sel)
    await session.commit()
    await session.refresh(sel)

    return ProvinceTargetRead(
        id=sel.id,
        user_id=sel.user_id,
        username=current_user.username,
        province_id=sel.province_id,
        province_name=prov.name,
        selected_at=sel.selected_at,
        discount_rate=prov.discount_rate,
        category=prov.category,
        is_primary=prov.is_primary,
        is_secondary=prov.is_secondary,
    )

@router.get("/", response_model=List[ProvinceTargetRead])
async def list_selections(
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(ProvinceTarget).where(ProvinceTarget.user_id == current_user.id)
    selections = (await session.exec(stmt)).all()

    output: List[ProvinceTargetRead] = []
    for sel in selections:
        prov = await session.get(Province, sel.province_id)
        output.append(ProvinceTargetRead(
            id=sel.id,
            user_id=sel.user_id,
            username=current_user.username,
            province_id=sel.province_id,
            province_name=prov.name,
            selected_at=sel.selected_at,
            discount_rate=prov.discount_rate,
            category=prov.category,
            is_primary=prov.is_primary,
            is_secondary=prov.is_secondary,
        ))
    return output

@router.delete("/{selection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_selection(
    selection_id: int,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    sel = await session.get(ProvinceTarget, selection_id)
    if not sel or sel.user_id != current_user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Selection not found")
    await session.delete(sel)
    await session.commit()
