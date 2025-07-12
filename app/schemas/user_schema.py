from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    username: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"