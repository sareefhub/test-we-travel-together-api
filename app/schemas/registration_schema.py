from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import date, datetime

class RegistrationBase(BaseModel):
    # ข้อมูลผู้ใช้ (บังคับ)
    user_id_card: str = Field(..., title="เลขประจำตัวประชาชน/Tax ID")
    user_full_name: str = Field(..., title="ชื่อ-นามสกุล")
    phone: str = Field(..., title="เบอร์โทรศัพท์")

    # ที่อยู่ (บังคับ)
    address_province: str = Field(..., title="จังหวัด")
    address_district: str = Field(..., title="อำเภอ")
    address_subdistrict: str = Field(..., title="ตำบล")

    # อีเมล (ไม่บังคับ)
    email: Optional[EmailStr] = Field(None, title="อีเมล")

    # ข้อมูลปีภาษีและการเดินทาง
    tax_year: int = Field(..., ge=2000, le=2100, title="ปีภาษี")
    primary_province_id: int = Field(..., gt=0, title="จังหวัดหลักที่เดินทาง (ID)")
    secondary_province_id: Optional[int] = Field(None, gt=0, title="จังหวัดรอง (ID) ถ้ามี")
    travel_start_date: date = Field(..., title="วันที่เริ่มเดินทาง")
    travel_end_date: date = Field(..., title="วันที่สิ้นสุดการเดินทาง")

    # ข้อมูลลดหย่อนและหลักฐาน
    tax_reduction_amount: int = Field(..., ge=0, title="จำนวนเงินลดหย่อนที่คำนวณเบื้องต้น")
    receipt_urls: Optional[List[str]] = Field(None, title="URL รูปภาพใบเสร็จ/หลักฐาน")

class RegistrationCreate(RegistrationBase):
    """ใช้สำหรับสร้าง Registration ใหม่"""

class RegistrationUpdate(BaseModel):
    """ใช้สำหรับอัปเดตสถานะหรือข้อมูลเสริม"""
    tax_year: Optional[int] = Field(None, ge=2000, le=2100, title="ปีภาษี")
    primary_province_id: Optional[int] = Field(None, gt=0, title="จังหวัดหลักที่เดินทาง (ID)")
    secondary_province_id: Optional[int] = Field(None, gt=0, title="จังหวัดรอง (ID)")
    travel_start_date: Optional[date] = Field(None, title="วันที่เริ่มเดินทาง")
    travel_end_date: Optional[date] = Field(None, title="วันที่สิ้นสุดการเดินทาง")
    tax_reduction_amount: Optional[int] = Field(None, ge=0, title="จำนวนเงินลดหย่อนที่อนุมัติ")
    receipt_urls: Optional[List[str]] = Field(None, title="URL หลักฐานที่อัปเดต")
    # ถ้าต้องการเพิ่มสถานะการอนุมัติให้ใส่ field status เพิ่มเองได้

class Registration(RegistrationBase):
    """Model สำหรับแสดงผล (Out)"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Alias สำหรับ response model
RegistrationOut = Registration
