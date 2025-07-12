# app/routers/v1/province_router.py

from typing import List, Union
from fastapi import APIRouter, Depends, Body, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.models.province_model import Province
from app.schemas.province_schema import (
    ProvinceCreate,
    ProvinceRead,
    ProvinceUpdate,
    ProvinceCategory,
)
from app.core.security import get_current_user

router = APIRouter(
    prefix="/provinces",
    tags=["provinces"],
    dependencies=[Depends(get_current_user)],
)


@router.post(
    "/",
    response_model=Union[ProvinceRead, List[ProvinceRead]],
    status_code=status.HTTP_201_CREATED,
)
async def create_province(
    payload: Union[ProvinceCreate, List[ProvinceCreate]] = Body(...),
    session: AsyncSession = Depends(get_session),
):
    items = payload if isinstance(payload, list) else [payload]
    created: List[Province] = []

    for data in items:
        prov = Province.model_validate(data.model_dump())
        prov.is_primary = data.category == ProvinceCategory.primary
        prov.is_secondary = data.category == ProvinceCategory.secondary
        session.add(prov)
        created.append(prov)

    await session.commit()
    for prov in created:
        await session.refresh(prov)

    return created if isinstance(payload, list) else created[0]


@router.get("/", response_model=List[ProvinceRead])
async def list_provinces(session: AsyncSession = Depends(get_session)):
    result = await session.exec(select(Province))
    return result.all()


@router.get("/{province_id}", response_model=ProvinceRead)
async def read_province(
    province_id: int,
    session: AsyncSession = Depends(get_session),
):
    prov = await session.get(Province, province_id)
    if not prov:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Province not found")
    return prov


@router.put("/{province_id}", response_model=ProvinceRead)
async def replace_province(
    province_id: int,
    payload: ProvinceUpdate,
    session: AsyncSession = Depends(get_session),
):
    prov = await session.get(Province, province_id)
    if not prov:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Province not found")

    for key, val in payload.model_dump(exclude_unset=False).items():
        if val is not None:
            setattr(prov, key, val)

    if payload.category is not None:
        prov.is_primary = payload.category == ProvinceCategory.primary
        prov.is_secondary = payload.category == ProvinceCategory.secondary

    session.add(prov)
    await session.commit()
    await session.refresh(prov)
    return prov


@router.patch("/{province_id}", response_model=ProvinceRead)
async def update_province(
    province_id: int,
    payload: ProvinceUpdate,
    session: AsyncSession = Depends(get_session),
):
    prov = await session.get(Province, province_id)
    if not prov:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Province not found")

    for key, val in payload.dict(exclude_unset=True).items():
        setattr(prov, key, val)

    if payload.category is not None:
        prov.is_primary = payload.category == ProvinceCategory.primary
        prov.is_secondary = payload.category == ProvinceCategory.secondary

    session.add(prov)
    await session.commit()
    await session.refresh(prov)
    return prov


@router.delete("/{province_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_province(
    province_id: int,
    session: AsyncSession = Depends(get_session),
):
    prov = await session.get(Province, province_id)
    if not prov:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Province not found")
    await session.delete(prov)
    await session.commit()
