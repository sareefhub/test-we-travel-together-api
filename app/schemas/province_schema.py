from pydantic import BaseModel, root_validator
from typing import Optional
from enum import Enum

class ProvinceCategory(str, Enum):
    primary = "primary"
    secondary = "secondary"
    target = "target"

class ProvinceBase(BaseModel):
    name: str
    category: ProvinceCategory
    discount_rate: float = 0.0
    is_target: Optional[bool] = False
    is_primary: Optional[bool] = False
    is_secondary: Optional[bool] = False

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
        # จังหวัดเป้าหมาย (default) → ส่วนลดตาม field หรือ 0
        else:
            values["is_primary"] = False
            values["is_secondary"] = False
            values["is_target"] = True
            # discount_rate ยังคงใช้ค่าที่ส่งมา (default 0.0)
        return values

class ProvinceCreate(ProvinceBase):
    pass

class ProvinceUpdate(ProvinceBase):
    pass

class ProvinceOut(ProvinceBase):
    id: int

    class Config:
        from_attributes = True
