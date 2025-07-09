from pydantic import BaseModel
from enum import Enum

class ProvinceCategory(str, Enum):
    primary   = "primary"
    secondary = "secondary"
    target    = "target"

class Province(BaseModel):
    id: int
    name: str
    category: ProvinceCategory
    discount_rate: float
    is_primary: bool = False
    is_secondary: bool = False
    is_target: bool = False