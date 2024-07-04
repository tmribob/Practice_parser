from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from src.config import settings

engine = create_engine(
    url=settings.database_url_psycopg,
    pool_pre_ping=True,
)


session_creation = sessionmaker(engine)

class Base(DeclarativeBase):
    pass


