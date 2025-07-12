from fastapi import APIRouter
from .authentication_router import router as registration_router
from .province_router import router as province_router
from .tax_reduction_router import router as tax_reduction_router

router = APIRouter(prefix="/v1")
router.include_router(registration_router)
router.include_router(province_router)
router.include_router(tax_reduction_router)
