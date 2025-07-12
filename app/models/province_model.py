from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .profile_model import Profile

class Province(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    category: str
    discount_rate: float = Field(default=0.0)
    is_primary: bool = Field(default=False)
    is_secondary: bool = Field(default=False)
    is_target: bool = Field(default=False)

    profiles: list["Profile"] = Relationship(back_populates="target_province")
