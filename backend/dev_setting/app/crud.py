from datetime import datetime
from typing import List, Optional

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Employee, EmployeeStatus, EmployeeStatusEnum, Member

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class EmployeeNotFoundError(Exception):
    pass


class MemberNotFoundError(Exception):
    pass


def _get_employee(db: Session, emp_id: int) -> Employee:
    employee = db.get(Employee, emp_id)
    if not employee:
        raise EmployeeNotFoundError(f"Employee {emp_id} not found")
    return employee


def _get_member_by_employee(db: Session, emp_id: int) -> Member:
    stmt = select(Member).where(Member.emp_id == emp_id)
    result = db.execute(stmt).scalar_one_or_none()
    if not result:
        raise MemberNotFoundError(f"Member for employee {emp_id} not found")
    return result


def list_employees(db: Session) -> List[Employee]:
    stmt = select(Employee).order_by(Employee.emp_id)
    return list(db.execute(stmt).scalars().unique())


def update_employee_profile(
    db: Session,
    emp_id: int,
    *,
    name: Optional[str] = None,
    email: Optional[str] = None,
    mobile: Optional[str] = None,
    status: Optional[EmployeeStatusEnum] = None,
    password: Optional[str] = None,
) -> Employee:
    employee = _get_employee(db, emp_id)

    if name is not None:
        employee.name = name
    if email is not None:
        employee.email = email
    if mobile is not None:
        employee.mobile = mobile

    if status is not None:
        status_record = db.execute(
            select(EmployeeStatus).where(EmployeeStatus.emp_id == emp_id)
        ).scalar_one_or_none()
        if status_record:
            status_record.status = status
            status_record.updated_at = datetime.utcnow()
        else:
            status_record = EmployeeStatus(emp_id=emp_id, status=status)
            db.add(status_record)

    if password:
        member = _get_member_by_employee(db, emp_id)
        member.password_hash = pwd_context.hash(password)
        member.updated_at = datetime.utcnow()

    db.flush()
    return employee
