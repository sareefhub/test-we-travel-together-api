# app/schemas/user_schema.py
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserBase(BaseModel):
    username: str
    phone: str = Field(..., description="เบอร์โทรศัพท์ที่ติดต่อได้")
    email: Optional[EmailStr] = Field(default=None, description="อีเมล (ถ้ามี)")
    citizen_id: Optional[str] = Field(
        default=None,
        pattern=r"^\d{13}$",
        description="เลขบัตรประชาชน 13 หลัก"
    )

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    username: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    citizen_id: Optional[str] = Field(
        default=None,
        pattern=r"^\d{13}$",
        description="เลขบัตรประชาชน 13 หลัก"
    )

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
