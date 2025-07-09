from fastapi import APIRouter
from .registration_router import router as registration_router

router = APIRouter(prefix="/v1")
router.include_router(registration_router)