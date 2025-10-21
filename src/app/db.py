from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator, Optional

try:
    from sqlmodel import SQLModel, Session, create_engine
except Exception:
    SQLModel = object  # type: ignore
    Session = object  # type: ignore

    def create_engine(*args, **kwargs):  # type: ignore
        return None


ENGINE_URL = "sqlite:///./app.db"
engine = create_engine(ENGINE_URL, echo=False) if callable(create_engine) else None


def init_db() -> None:
    try:
        if engine is not None and hasattr(SQLModel, "metadata"):
            SQLModel.metadata.create_all(engine)  # type: ignore[attr-defined]
    except Exception:
        pass


@contextmanager
def get_session() -> Iterator[Optional[Session]]:
    if engine is None or Session is object:
        yield None
        return
    session = Session(engine)  # type: ignore[call-arg]
    try:
        yield session
    finally:
        session.close()
