from typing import Optional
from enum import Enum
from sqlmodel import SQLModel, Field
from pydantic import field_validator

class ProvinceCategory(str, Enum):
    primary = "primary"
    secondary = "secondary"

class ProvinceBase(SQLModel):
    name: str
    category: ProvinceCategory
    discount_rate: str = Field(default="0%")

    @field_validator("discount_rate")
    def ensure_percent_format(cls, v: str) -> str:
        if not v.endswith("%"):
            raise ValueError("discount_rate must end with '%' (e.g. '10%')")
        return v

class ProvinceCreate(ProvinceBase):
    pass

class ProvinceRead(ProvinceBase):
    id: int
    is_primary: bool
    is_secondary: bool

    model_config = {"from_attributes": True}

class ProvinceUpdate(SQLModel):
    name: Optional[str] = None
    category: Optional[ProvinceCategory] = None
    discount_rate: Optional[str] = None
