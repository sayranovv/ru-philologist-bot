from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URL

Base = declarative_base()


class UserQuery(Base):
    __tablename__ = 'user_queries'

    id: int = Column(Integer, primary_key=True, index=True)
    user_id: int = Column(Integer, index=True, nullable=False)
    command: str = Column(String(50), nullable=False)
    query_text: str = Column(Text, nullable=False)
    response_text: str = Column(Text, nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.utcnow, index=True)


engine = create_engine(
    DATABASE_URL,
    connect_args={'check_same_thread': False} if 'sqlite' in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_session():
    return SessionLocal()
