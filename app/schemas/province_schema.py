# app/schemas/province_schema.py

from typing import Optional
from enum import Enum
from sqlmodel import SQLModel

class ProvinceCategory(str, Enum):
    primary = "primary"
    secondary = "secondary"

class ProvinceBase(SQLModel):
    name: str
    category: ProvinceCategory
    discount_rate: Optional[float] = 0.0
    is_target: bool = False

class ProvinceCreate(ProvinceBase):
    """POST body: name, category, discount_rate, is_target"""
    pass

class ProvinceRead(ProvinceBase):
    """What we return: + id, is_primary, is_secondary"""
    id: int
    is_primary: bool
    is_secondary: bool

class ProvinceUpdate(SQLModel):
    """PUT/PATCH body: any of name, category, discount_rate, is_target"""
    name: Optional[str] = None
    category: Optional[ProvinceCategory] = None
    discount_rate: Optional[float] = None
    is_target: Optional[bool] = None
