from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import get_session
from app.models.province_model import Province as ProvinceModel, ProvinceCategory
from app.models.tax_reduction_model import TaxReduction
from app.schemas.tax_reduction_schema import TaxReductionOut

router = APIRouter(prefix="/tax-reductions", tags=["tax-reductions"])

@router.get("", response_model=List[TaxReductionOut], summary="All provinces tax reduction")
async def list_all_tax_reductions(session: AsyncSession = Depends(get_session)):
    regs = await session.exec(select(ProvinceModel).order_by(ProvinceModel.name))
    provinces = regs.all()
    return [TaxReduction.from_orm(p) for p in provinces]

@router.get("/secondary", response_model=List[TaxReductionOut], summary="Secondary provinces only")
async def list_secondary_tax_reductions(session: AsyncSession = Depends(get_session)):
    regs = await session.exec(
        select(ProvinceModel)
        .where(ProvinceModel.category == ProvinceCategory.secondary)
        .order_by(ProvinceModel.name)
    )
    provinces = regs.all()
    if not provinces:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No secondary provinces found")
    return [TaxReduction.from_orm(p) for p in provinces]
