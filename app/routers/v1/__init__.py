from fastapi import APIRouter
from .authentication_router import router as registration_router
from .province_router import router as province_router
from .user_router import router as user_router 
from .province_target_router import router as province_target_router

router = APIRouter(prefix="/v1")
router.include_router(registration_router)
router.include_router(province_router)
router.include_router(user_router)
router.include_router(province_target_router)
