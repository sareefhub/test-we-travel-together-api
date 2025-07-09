# app/routers/v1/tax_reduction_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import get_session
from app.models.province_model import Province as ProvinceModel
from app.schemas.province_schema import ProvinceCategory

router = APIRouter(
    prefix="/tax-reductions",
    tags=["tax-reductions"],
)

@router.get(
    "/{category}",
    response_model=list[ProvinceModel],
    summary="List provinces by tax category",
)
async def list_by_category(
    category: ProvinceCategory,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(ProvinceModel).where(ProvinceModel.category == category.value)
    result = await session.exec(stmt)
    provinces = result.all()
    if not provinces:
        raise HTTPException(status_code=404, detail="No provinces found")
    return provinces
