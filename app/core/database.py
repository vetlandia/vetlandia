from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.db_url,
    pool_pre_ping=True,   # detecta conexões mortas antes do query (Railway mata idle connections)
    pool_size=5,
    max_overflow=10,
    pool_recycle=300,     # recicla antes do Railway desconectar (Railway timeout ~5-10 min)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
