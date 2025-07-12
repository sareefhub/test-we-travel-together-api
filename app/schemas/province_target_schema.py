# app/schemas/province_target_schema.py
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ProvinceTargetCreate(BaseModel):
    province_id: int

class ProvinceTargetRead(BaseModel):
    id: int
    user_id: int
    username: str
    province_id: int
    province_name: str
    selected_at: datetime
    discount_rate: str
    category: str
    is_primary: bool
    is_secondary: bool

    model_config = ConfigDict(from_attributes=True)
