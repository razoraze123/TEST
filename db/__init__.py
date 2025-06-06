from __future__ import annotations

from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base

engine = None
SessionLocal = sessionmaker(autocommit=False, autoflush=False)


def init_engine(path: str | Path):
    """Initialise the global engine and session factory.

    Ensures the parent directory exists before opening the SQLite
    database so that ``create_engine`` does not fail if the file or its
    folder is missing.
    """
    global engine, SessionLocal
    db_path = Path(path)
    if db_path.parent and not db_path.parent.exists():
        db_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{db_path}")
    SessionLocal.configure(bind=engine)
    return engine
