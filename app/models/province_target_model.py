# app/models/province_target_model.py

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .user_model import User
    from .province_model import Province

class ProvinceTarget(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    province_id: int = Field(foreign_key="province.id", index=True)
    selected_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional["User"] = Relationship(back_populates="targets")
    province: Optional["Province"] = Relationship(back_populates="targets")
