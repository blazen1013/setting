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


class InvalidCredentialsError(Exception):
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
    # 조인으로 중복이 생기지 않는다면 unique() 불필요; 안전하게 all() 사용
    return list(db.execute(stmt).scalars().all())


def get_employee(db: Session, emp_id: int) -> Employee:
    return _get_employee(db, emp_id)


def get_member_by_login_id(db: Session, login_id: str) -> Member:
    stmt = select(Member).where(Member.login_id == login_id)
    member = db.execute(stmt).scalar_one_or_none()
    if not member:
        raise MemberNotFoundError(f"Member with login_id {login_id} not found")
    return member


def verify_password(plain_password: str, stored_password: str) -> bool:
    """
    평문과 bcrypt 해시 모두 지원.
    - stored_password가 bcrypt 형태면 passlib.verify 사용
    - 아니면 평문으로 간주하여 문자열 비교
    """
    try:
        if isinstance(stored_password, str) and stored_password.startswith("$2") and len(stored_password) >= 50:
            return pwd_context.verify(plain_password, stored_password)
        return plain_password == stored_password
    except Exception:
        return False


def authenticate_member(db: Session, login_id: str, password: str) -> Member:
    try:
        member = get_member_by_login_id(db, login_id)
    except MemberNotFoundError as exc:
        raise InvalidCredentialsError("Invalid login credentials") from exc

    if not verify_password(password, member.password_hash):
        raise InvalidCredentialsError("Invalid login credentials")

    return member


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

    # 기본 정보 갱신
    if name is not None:
        employee.name = name
    if email is not None:
        employee.email = email
    if mobile is not None:
        employee.mobile = mobile

    # 상태 갱신 (있으면 업데이트, 없으면 생성)
    if status is not None:
        status_record = db.execute(
            select(EmployeeStatus).where(EmployeeStatus.emp_id == emp_id)
        ).scalar_one_or_none()

        if status_record:
            status_record.status = status
            # updated_at 필드가 있다면 갱신
            if hasattr(status_record, "updated_at"):
                setattr(status_record, "updated_at", datetime.utcnow())
        else:
            payload = {"emp_id": emp_id, "status": status}
            # created_at 필드가 있다면 세팅
            if hasattr(EmployeeStatus, "created_at"):
                payload["created_at"] = datetime.utcnow()
            db.add(EmployeeStatus(**payload))

    # 비밀번호 변경: 요청에 따라 '그대로' 저장 (평문/해시 모두 허용)
    if password is not None:
        member = _get_member_by_employee(db, emp_id)
        # 보안상 권장되진 않지만, 요구사항대로 해시 없이 저장 가능하게 유지
        member.password_hash = password

    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee
