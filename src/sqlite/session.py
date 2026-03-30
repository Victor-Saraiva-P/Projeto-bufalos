from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.config import SQLITE_PATH


def sqlite_url(sqlite_path: str = SQLITE_PATH) -> str:
    return f"sqlite:///{sqlite_path}"


def criar_engine_sqlite(sqlite_path: str = SQLITE_PATH):
    Path(sqlite_path).parent.mkdir(parents=True, exist_ok=True)
    return create_engine(sqlite_url(sqlite_path), future=True)


def criar_tabelas_sqlite(sqlite_path: str = SQLITE_PATH) -> None:
    from src import models as _models  # noqa: F401
    from src.sqlite.base import Base

    engine = criar_engine_sqlite(sqlite_path)
    Base.metadata.create_all(engine)


def recriar_tabelas_sqlite(sqlite_path: str = SQLITE_PATH) -> None:
    from src import models as _models  # noqa: F401
    from src.sqlite.base import Base

    engine = criar_engine_sqlite(sqlite_path)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def criar_sessionmaker_sqlite(sqlite_path: str = SQLITE_PATH) -> sessionmaker[Session]:
    engine = criar_engine_sqlite(sqlite_path)
    return sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        future=True,
    )
