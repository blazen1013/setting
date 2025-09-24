from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from .models import EmployeeStatusEnum


class EmployeeStatusBase(BaseModel):
    status: EmployeeStatusEnum = Field(..., description="현재 상태")


class EmployeeStatusCreate(EmployeeStatusBase):
    pass


class EmployeeStatusResponse(EmployeeStatusBase):
    updated_at: datetime

    # Pydantic v2: orm_mode -> from_attributes
    model_config = ConfigDict(from_attributes=True)


class EmployeeBase(BaseModel):
    name: str = Field(..., max_length=50)
    email: EmailStr
    mobile: str = Field(..., max_length=20)


class EmployeeResponse(EmployeeBase):
    emp_id: int
    emp_no: str
    dept_id: int
    role_id: int
    status: Optional[EmployeeStatusResponse]

    model_config = ConfigDict(from_attributes=True)


class EmployeeUpdate(EmployeeBase):
    status: Optional[EmployeeStatusEnum] = None
    password: Optional[str] = Field(
        default=None, min_length=8, description="새로운 비밀번호"
    )
