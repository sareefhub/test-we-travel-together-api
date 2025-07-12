from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .user_model import User
    from .province_model import Province

class Profile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    target_province_id: Optional[int] = Field(default=None, foreign_key="province.id")

    user: Optional["User"] = Relationship(back_populates="profile")
    target_province: Optional["Province"] = Relationship(back_populates="profiles")
