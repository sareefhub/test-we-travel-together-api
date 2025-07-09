# app/schemas/registration_schema.py

from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field


class RegistrationBase(BaseModel):
    user_id: int = Field(..., gt=0, description="รหัสผู้ใช้ในระบบ")
    tax_year: int = Field(..., ge=2000, le=2100, description="ปีภาษี (เช่น 2024)")
    primary_province_id: int = Field(..., gt=0, description="รหัสจังหวัดหลักที่เดินทาง")
    secondary_province_id: Optional[int] = Field(
        None, gt=0, description="รหัสจังหวัดรอง (ถ้ามี)"
    )
    travel_start_date: date = Field(..., description="วันที่เริ่มเดินทาง")
    travel_end_date: date = Field(..., description="วันที่สิ้นสุดการเดินทาง")
    tax_reduction_amount: int = Field(..., ge=0, description="ยอดรวมค่าใช้จ่ายที่ขอสิทธิ์ (บาท)")
    receipt_urls: Optional[List[str]] = Field(
        None, description="รายการ URL ของใบเสร็จรับเงิน (เช่น PDF/JPG)"
    )


class RegistrationCreate(RegistrationBase):
    """ใช้สำหรับรับข้อมูลสร้าง registration ใหม่"""
    pass


class RegistrationUpdate(BaseModel):
    """ใช้สำหรับอัปเดตข้อมูล registration บางส่วน"""
    tax_year: Optional[int] = Field(None, ge=2000, le=2100)
    primary_province_id: Optional[int] = Field(None, gt=0)
    secondary_province_id: Optional[int] = Field(None, gt=0)
    travel_start_date: Optional[date] = None
    travel_end_date: Optional[date] = None
    tax_reduction_amount: Optional[int] = Field(None, ge=0)
    receipt_urls: Optional[List[str]] = None


class Registration(RegistrationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
