from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON
from datetime import datetime, date
from typing import Optional, List

class Registration(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # ข้อมูลผู้ใช้ (บังคับ)
    user_id_card: str = Field(..., index=True, title="เลขประจำตัวประชาชน/Tax ID")
    user_full_name: str = Field(..., title="ชื่อ-นามสกุล")
    phone: str = Field(..., title="เบอร์โทรศัพท์")

    # ที่อยู่ (บังคับ)
    address_province: str = Field(..., title="จังหวัด")
    address_district: str = Field(..., title="อำเภอ")
    address_subdistrict: str = Field(..., title="ตำบล")

    # อีเมล (ไม่บังคับ)
    email: Optional[str] = Field(default=None, title="อีเมล")

    # ข้อมูลปีภาษีและการเดินทาง
    tax_year: int = Field(..., ge=2000, le=2100, title="ปีภาษี")
    primary_province_id: int = Field(..., gt=0, title="จังหวัดหลักที่เดินทาง (ID)")
    secondary_province_id: Optional[int] = Field(default=None, gt=0, title="จังหวัดรอง (ID) ถ้ามี")
    travel_start_date: date = Field(..., title="วันที่เริ่มเดินทาง")
    travel_end_date: date = Field(..., title="วันที่สิ้นสุดการเดินทาง")

    # ข้อมูลลดหย่อนและหลักฐาน (receipt_urls เป็น JSON list)
    tax_reduction_amount: int = Field(..., ge=0, title="จำนวนเงินลดหย่อนที่คำนวณเบื้องต้น")
    receipt_urls: Optional[List[str]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
        title="URL รูปภาพใบเสร็จ/หลักฐาน"
    )

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: Optional[datetime] = Field(default=None, nullable=True)
