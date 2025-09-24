# app/database.py
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    future=True,             # 2.x 스타일 보장(권장)
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,  # 커밋 후에도 객체 값 유지(응답 직전 접근 편함)
    bind=engine,
    class_=Session,
)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
        db.commit()          # 요청 단위 트랜잭션(원하시면 제거 가능)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
