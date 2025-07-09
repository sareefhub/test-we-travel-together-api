from sqlmodel import SQLModel, Field
from pydantic import root_validator
from typing import Optional
from enum import Enum

class ProvinceCategory(str, Enum):
    primary = "primary"
    secondary = "secondary"
    target = "target"

class Province(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    category: ProvinceCategory
    discount_rate: float = 0.0
    is_target: Optional[bool] = Field(default=False)
    is_primary: Optional[bool] = Field(default=False)
    is_secondary: Optional[bool] = Field(default=False)

    @root_validator(pre=True)
    def apply_category_defaults(cls, values):
        cat = values.get("category")
        # จังหวัดหลัก → ส่วนลด 10%
        if cat == ProvinceCategory.primary:
            values["discount_rate"] = 0.10
            values["is_primary"] = True
            values["is_secondary"] = False
            values["is_target"] = False
        # จังหวัดรอง → ส่วนลด 20%
        elif cat == ProvinceCategory.secondary:
            values["discount_rate"] = 0.20
            values["is_primary"] = False
            values["is_secondary"] = True
            values["is_target"] = False
        # จังหวัดเป้าหมาย → flag target
        else:
            values["discount_rate"] = values.get("discount_rate", 0.0)
            values["is_primary"] = False
            values["is_secondary"] = False
            values["is_target"] = True
        return values
