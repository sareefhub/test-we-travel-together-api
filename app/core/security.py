# app/core/security.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from typing import Optional

from app.core.config import settings
from app.database import get_session
from app.models.user_model import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")

def create_access_token(data: dict) -> str:
    return jwt.encode(data, settings.jwt_secret_key, algorithm="HS256")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])
        username: Optional[str] = payload.get("sub")
        if not username:
            raise
    except:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")

    result = await session.exec(select(User).where(User.username == username))
    user = result.first()
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    return user
