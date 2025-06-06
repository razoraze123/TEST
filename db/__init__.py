from __future__ import annotations

from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base

engine = None
SessionLocal = sessionmaker(autocommit=False, autoflush=False)


def init_engine(path: str | Path):
    """Initialise the global engine and session factory."""
    global engine, SessionLocal
    engine = create_engine(f"sqlite:///{path}")
    SessionLocal.configure(bind=engine)
    return engine
