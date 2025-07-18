# app/models/user_model.py
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

from .province_target_model import ProvinceTarget

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    phone: str = Field(nullable=False, index=True, unique=True)
    email: Optional[str] = Field(default=None, index=True, unique=True)
    citizen_id: Optional[str] = Field(default=None, index=True, unique=True)
    hashed_password: str

    targets: List[ProvinceTarget] = Relationship(back_populates="user")
