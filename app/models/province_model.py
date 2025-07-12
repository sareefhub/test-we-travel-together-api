from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from app.models.province_target_model import ProvinceTarget

class Province(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    category: str
    discount_rate: str = Field(default="0%")
    is_primary: bool = Field(default=False)
    is_secondary: bool = Field(default=False)

    targets: List["ProvinceTarget"] = Relationship(back_populates="province")
