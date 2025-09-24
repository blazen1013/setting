# main.py
from datetime import datetime
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import crud, schemas
from .config import get_settings
from .database import engine, get_db
from .models import Base, EmployeeStatusEnum

settings = get_settings()
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBasic()


def _latest_status(employee) -> Optional[schemas.EmployeeStatusResponse]:
    """직원의 최신 상태 한 건만 추려서 스키마로 변환"""
    if not getattr(employee, "statuses", None):
        return None
    status_record = max(
        employee.statuses,
        key=lambda s: getattr(s, "updated_at", None) or datetime.min,
    )
    # pydantic v2: from_attributes=True 가 schemas 쪽에 설정되어 있어야 함
    return schemas.EmployeeStatusResponse.model_validate(status_record)


@app.get("/health")
def health_check():
    return {"status": "ok"}


def _get_current_member(
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """HTTP Basic 인증 → Member 조회 및 emp_id 연결 검증"""
    try:
        member = crud.authenticate_member(db, credentials.username, credentials.password)
    except crud.InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        ) from None

    if member.emp_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No employee is associated with this account",
        )
    return member


@app.get("/employees/me", response_model=schemas.EmployeeResponse)
def read_current_employee(
    current_member=Depends(_get_current_member),
    db: Session = Depends(get_db),
):
    """현재 로그인한 본인 정보 조회"""
    employee = crud.get_employee(db, current_member.emp_id)
    return schemas.EmployeeResponse(
        emp_id=employee.emp_id,
        emp_no=employee.emp_no,
        dept_id=employee.dept_id,
        role_id=employee.role_id,
        name=employee.name,
        email=employee.email,
        mobile=employee.mobile,
        status=_latest_status(employee),
    )


@app.put("/employees/me", response_model=schemas.EmployeeResponse)
def update_current_employee(
    payload: schemas.EmployeeUpdate,
    current_member=Depends(_get_current_member),
    db: Session = Depends(get_db),
):
    """현재 로그인한 본인 정보 수정만 허용"""
    try:
        employee = crud.update_employee_profile(
            db,
            current_member.emp_id,
            name=payload.name,
            email=payload.email,
            mobile=payload.mobile,
            status=payload.status,
            password=payload.password,
        )
    except crud.EmployeeNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except crud.MemberNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    return schemas.EmployeeResponse(
        emp_id=employee.emp_id,
        emp_no=employee.emp_no,
        dept_id=employee.dept_id,
        role_id=employee.role_id,
        name=employee.name,
        email=employee.email,
        mobile=employee.mobile,
        status=_latest_status(employee),
    )


@app.get("/employee-status-options")
def get_status_options():
    """프론트 select용 상태 옵션 제공 (문자열/라벨)"""
    options = [
        {"value": e.value if hasattr(e, "value") else str(e), "label": e.name}
        for e in EmployeeStatusEnum
    ]
    return {"options": options}
