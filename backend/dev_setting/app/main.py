from datetime import datetime
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from . import crud, schemas
from .config import get_settings
from .database import engine, get_db
from .models import Base, EmployeeStatusEnum

settings = get_settings()
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)

# CORS
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _latest_status(employee) -> Optional[schemas.EmployeeStatusResponse]:
    if not getattr(employee, "statuses", None):
        return None
    status_record = max(employee.statuses, key=lambda s: s.updated_at or datetime.min)
    # v2: from_orm -> model_validate (schemas에 from_attributes=True 이미 설정됨)
    return schemas.EmployeeStatusResponse.model_validate(status_record)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/employees", response_model=list[schemas.EmployeeResponse])
def read_employees(db: Session = Depends(get_db)):
    employees = crud.list_employees(db)
    out: list[schemas.EmployeeResponse] = []
    for e in employees:
        out.append(
            schemas.EmployeeResponse(
                emp_id=e.emp_id,
                emp_no=e.emp_no,
                dept_id=e.dept_id,
                role_id=e.role_id,
                name=e.name,
                email=e.email,
                mobile=e.mobile,
                status=_latest_status(e),
            )
        )
    return out

@app.put("/employees/{emp_id}", response_model=schemas.EmployeeResponse)
def update_employee(emp_id: int, payload: schemas.EmployeeUpdate, db: Session = Depends(get_db)):
    try:
        employee = crud.update_employee_profile(
            db,
            emp_id,
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
    # 이름 충돌 피하려고 변수명 변경
    return {"options": [opt.value for opt in EmployeeStatusEnum]}
