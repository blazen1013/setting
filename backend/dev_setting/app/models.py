from datetime import datetime
from enum import Enum

from sqlalchemy import Column, Date, DateTime, Enum as SqlEnum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class EmployeeStatusEnum(str, Enum):
    WORKING = "WORKING"
    AWAY = "AWAY"
    OUT_ON_BUSINESS = "OUT_ON_BUSINESS"
    OFF_WORK = "OFF_WORK"


class Department(Base):
    __tablename__ = "department"

    dept_id = Column(Integer, primary_key=True, autoincrement=True)
    dept_name = Column(String(50), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    employees = relationship("Employee", back_populates="department")


class Role(Base):
    __tablename__ = "role"

    role_id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String(50), nullable=False, unique=True)
    role_level = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    employees = relationship("Employee", back_populates="role")


class Employee(Base):
    __tablename__ = "employee"

    emp_id = Column(Integer, primary_key=True, autoincrement=True)
    emp_no = Column(String(20), nullable=False, unique=True)
    dept_id = Column(Integer, ForeignKey("department.dept_id"), nullable=False)
    role_id = Column(Integer, ForeignKey("role.role_id"), nullable=False)
    name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    mobile = Column(String(20), nullable=False, unique=True)
    hire_date = Column(Date)
    birthday = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    department = relationship("Department", back_populates="employees")
    role = relationship("Role", back_populates="employees")
    member = relationship("Member", back_populates="employee", uselist=False)
    statuses = relationship("EmployeeStatus", back_populates="employee", cascade="all, delete-orphan")


class Member(Base):
    __tablename__ = "member"

    member_id = Column(Integer, primary_key=True, autoincrement=True)
    login_id = Column(String(50), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    emp_id = Column(Integer, ForeignKey("employee.emp_id"))
    ext_id = Column(Integer, ForeignKey("external_person.ext_id"))
    user_type = Column(String(20), nullable=False)
    last_login_at = Column(DateTime)
    failed_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    employee = relationship("Employee", back_populates="member")


class EmployeeStatus(Base):
    __tablename__ = "employee_status"
    __table_args__ = (
        UniqueConstraint("emp_id", name="uq_employee_status_emp"),
    )

    status_id = Column(Integer, primary_key=True, autoincrement=True)
    emp_id = Column(Integer, ForeignKey("employee.emp_id"), nullable=False)
    status = Column(SqlEnum(EmployeeStatusEnum), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    employee = relationship("Employee", back_populates="statuses")
