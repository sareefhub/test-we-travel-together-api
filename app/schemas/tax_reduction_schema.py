from enum import Enum
from typing import List
from pydantic import BaseModel

class ProvinceCategory(str, Enum):
    primary   = "primary"
    secondary = "secondary"
    target    = "target"

class TaxReductionBase(BaseModel):
    province_id: int
    province_name: str
    category: ProvinceCategory
    discount_rate: float
    is_primary: bool
    is_secondary: bool
    is_target: bool

    class Config:
        from_attributes = True

class TaxReductionOut(TaxReductionBase):
    """Single province’s tax‐reduction details."""
    pass