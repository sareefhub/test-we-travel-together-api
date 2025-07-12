# app/schemas/profile_schema.py
from typing import Optional
from sqlmodel import SQLModel, Field
from app.schemas.province_schema import ProvinceRead

class ProfileBase(SQLModel):
    target_province_id: Optional[int] = Field(default=None)

class ProfileCreate(ProfileBase):
    pass

class ProfileRead(ProfileBase):
    id: int
    user_id: int
    target_province: Optional[ProvinceRead] = None

class ProfileUpdate(SQLModel):
    target_province_id: Optional[int] = None
