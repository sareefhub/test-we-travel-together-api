from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Registration(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    tax_year: int
    primary_province_id: int
    secondary_province_id: Optional[int] = None
    travel_start_date: datetime
    travel_end_date: datetime
    tax_reduction_amount: int
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)