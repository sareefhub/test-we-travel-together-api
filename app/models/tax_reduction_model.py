from sqlmodel import SQLModel, Field
from enum import Enum

class ProvinceCategory(str, Enum):
    primary = "primary"
    secondary = "secondary"
    target = "target"

class TaxReduction(SQLModel, table=False):
    province_id: int = Field(..., alias="id")
    province_name: str = Field(..., alias="name")
    category: ProvinceCategory
    discount_rate: float
    is_primary: bool
    is_secondary: bool
    is_target: bool

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
