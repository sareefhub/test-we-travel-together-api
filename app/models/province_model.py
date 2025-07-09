from typing import Optional
from sqlmodel import SQLModel, Field

class Province(SQLModel, table=True):
    # แก้ตรงนี้: กำหนด id ให้ Optional พร้อม default=None
    id: Optional[int] = Field(default=None, primary_key=True)

    name: str
    category: str
    discount_rate: float

    is_primary: bool = False
    is_secondary: bool = False
    is_target: bool = False