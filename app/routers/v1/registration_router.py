# app/api/registration_router.py

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.schemas.registration_schema import (
    Registration,
    RegistrationCreate,
    RegistrationUpdate,
)
from app.models import get_session
from app.models.registration_model import Registration as RegistrationModel

router = APIRouter(prefix="/registrations", tags=["registrations"])


@router.get(
    "",
    summary="Get all registrations",
    description="Retrieve a list of all travel registrations.",
    response_model=List[Registration],
)
async def get_registrations(
    skip: int = 0,
    limit: int = 100,
    tax_year: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
) -> List[Registration]:
    # Query ด้วย select, filter ตาม tax_year ถ้ามี
    query = select(RegistrationModel)
    if tax_year is not None:
        query = query.where(RegistrationModel.tax_year == tax_year)
    query = query.offset(skip).limit(limit)

    result = await session.exec(query)
    regs = result.all()
    # แปลงเป็น Pydantic model
    return [Registration.model_validate(r) for r in regs]


@router.get(
    "/{registration_id}",
    summary="Get a registration by ID",
    description="Retrieve a specific registration by its ID.",
    response_model=Registration,
)
async def get_registration(
    registration_id: int,
    session: AsyncSession = Depends(get_session),
) -> Registration:
    # อ่านจาก DB
    reg = await session.get(RegistrationModel, registration_id)
    if not reg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found"
        )
    return Registration.model_validate(reg)


@router.post(
    "",
    summary="Create a new registration",
    description="Create a new travel registration for tax deduction.",
    response_model=Registration,
    status_code=status.HTTP_201_CREATED,
)
async def create_registration(
    registration_in: RegistrationCreate,
    session: AsyncSession = Depends(get_session),
) -> Registration:
    # สร้าง instance แล้วบันทึก
    db_reg = RegistrationModel(**registration_in.model_dump())
    session.add(db_reg)
    await session.commit()
    await session.refresh(db_reg)
    return Registration.model_validate(db_reg)


@router.put(
    "/{registration_id}",
    summary="Update an existing registration",
    description="Update fields of an existing registration.",
    response_model=Registration,
)
async def update_registration(
    registration_id: int,
    registration_up: RegistrationUpdate,
    session: AsyncSession = Depends(get_session),
) -> Registration:
    # ดึง record เดิม
    db_reg = await session.get(RegistrationModel, registration_id)
    if not db_reg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found"
        )

    # นำข้อมูลจาก body มาอัปเดตเฉพาะ field ที่ส่งมา
    update_data = registration_up.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_reg, field, value)

    # ตั้ง updated_at อัตโนมัติ
    db_reg.updated_at = datetime.utcnow()

    session.add(db_reg)
    await session.commit()
    await session.refresh(db_reg)
    return Registration.model_validate(db_reg)


@router.delete(
    "/{registration_id}",
    summary="Delete a registration",
    description="Delete a registration by its ID.",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_registration(
    registration_id: int,
    session: AsyncSession = Depends(get_session),
):
    # ดึง record แล้วลบทิ้ง
    db_reg = await session.get(RegistrationModel, registration_id)
    if not db_reg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found"
        )

    await session.delete(db_reg)
    await session.commit()
    return None
