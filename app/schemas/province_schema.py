from pydantic import BaseModel, model_validator
from enum import Enum
from typing import Optional

class ProvinceCategory(str, Enum):
    primary   = "primary"
    secondary = "secondary"
    target    = "target"

class ProvinceBase(BaseModel):
    name: str
    category: ProvinceCategory
    discount_rate: float = 0.0
    is_target: Optional[bool] = False
    is_primary: Optional[bool] = False
    is_secondary: Optional[bool] = False

    @model_validator(mode="after")
    def apply_category_defaults(cls, m: "ProvinceBase") -> "ProvinceBase":
        m.is_primary = m.is_secondary = m.is_target = False
        if m.category is ProvinceCategory.primary:
            m.discount_rate = 0.10
            m.is_primary = True
        elif m.category is ProvinceCategory.secondary:
            m.discount_rate = 0.20
            m.is_secondary = True
        else:
            m.is_target = True
        return m

class ProvinceCreate(ProvinceBase):
    pass

class ProvinceUpdate(ProvinceBase):
    pass

class ProvinceOut(ProvinceBase):
    id: int

    class Config:
        from_attributes = True
        validate_by_name    = True