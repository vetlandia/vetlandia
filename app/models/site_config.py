from sqlalchemy import Column, String, Text
from sqlalchemy.orm import Session

from app.core.database import Base


class SiteConfig(Base):
    __tablename__ = "site_config"

    key   = Column(String(100), primary_key=True)
    value = Column(Text, nullable=True)


def get_config(db: Session, key: str, default: str = "") -> str:
    row = db.query(SiteConfig).filter(SiteConfig.key == key).first()
    return row.value if row else default


def set_config(db: Session, key: str, value: str) -> None:
    row = db.query(SiteConfig).filter(SiteConfig.key == key).first()
    if row:
        row.value = value
    else:
        db.add(SiteConfig(key=key, value=value))
