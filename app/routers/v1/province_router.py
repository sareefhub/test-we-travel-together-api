from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import get_session
from app.models import Province as ProvModel
from app.schemas.province_schema import ProvinceOut, ProvinceCreate, ProvinceUpdate

router = APIRouter(prefix="/provinces", tags=["provinces"])


@router.get(
    "",
    response_model=List[ProvinceOut],
    summary="List all provinces",
    description="Retrieve all provinces.",
)
async def list_provinces(
    session: AsyncSession = Depends(get_session),
) -> List[ProvinceOut]:
    stmt = select(ProvModel).order_by(ProvModel.name)
    result = await session.exec(stmt)
    return result.all()


@router.get(
    "/{province_id}",
    response_model=ProvinceOut,
    summary="Get province by ID",
    description="Get a province by its ID.",
)
async def get_province(
    province_id: int,
    session: AsyncSession = Depends(get_session),
) -> ProvinceOut:
    province = await session.get(ProvModel, province_id)
    if not province:
        raise HTTPException(status_code=404, detail="Province not found")
    return province


@router.post(
    "",
    response_model=ProvinceOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new province",
    description="Create a new province.",
)
async def create_province(
    province_in: ProvinceCreate,
    session: AsyncSession = Depends(get_session),
) -> ProvinceOut:
    # สร้าง ORM object ได้โดยไม่ต้องมี id ใน input
    db_province = ProvModel(**province_in.dict())
    session.add(db_province)
    await session.commit()
    await session.refresh(db_province)
    return db_province


@router.put(
    "/{province_id}",
    response_model=ProvinceOut,
    summary="Update a province",
    description="Update a province by its ID.",
)
async def update_province(
    province_id: int,
    province_in: ProvinceUpdate,
    session: AsyncSession = Depends(get_session),
) -> ProvinceOut:
    province = await session.get(ProvModel, province_id)
    if not province:
        raise HTTPException(status_code=404, detail="Province not found")

    update_data = province_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(province, key, value)

    session.add(province)
    await session.commit()
    await session.refresh(province)
    return province


@router.delete(
    "/{province_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a province",
    description="Delete a province by its ID.",
)
async def delete_province(
    province_id: int,
    session: AsyncSession = Depends(get_session),
):
    province = await session.get(ProvModel, province_id)
    if not province:
        raise HTTPException(status_code=404, detail="Province not found")
    await session.delete(province)
    await session.commit()
    return None