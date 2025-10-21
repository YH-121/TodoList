from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional

try:
    from sqlmodel import SQLModel, Session, create_engine
    from sqlalchemy.engine import Engine
except Exception:  # SQLModel/SQLAlchemy 未導入時のフォールバック
    SQLModel = object  # type: ignore
    Session = object  # type: ignore
    Engine = object  # type: ignore

    def create_engine(*args, **kwargs):  # type: ignore
        return None


_ENGINE_CACHE: dict[str, Optional[Engine]] = {}


def _ensure_sqlite_dir(db_url: str) -> None:
    if not db_url.startswith("sqlite"):
        return
    # sqlite:///./path/to/file.sqlite3  or sqlite:///C:/abs/path/file.sqlite3
    prefix = "sqlite:///"
    if db_url == "sqlite:///:memory:":
        return
    if db_url.startswith(prefix):
        db_path = db_url[len(prefix) :]
        # Normalize Windows backslashes if present
        db_path = db_path.replace("\\", "/")
        p = Path(db_path)
        if not p.is_absolute():
            p = Path.cwd() / p
        p.parent.mkdir(parents=True, exist_ok=True)


def get_engine(db_url: str = "sqlite:///./data/app.sqlite3") -> Optional[Engine]:
    if db_url in _ENGINE_CACHE:
        return _ENGINE_CACHE[db_url]
    try:
        if not callable(create_engine):  # type: ignore[truthy-bool]
            _ENGINE_CACHE[db_url] = None
            return None
        _ensure_sqlite_dir(db_url)
        engine = create_engine(db_url, echo=False)
        _ENGINE_CACHE[db_url] = engine
        return engine
    except Exception:
        _ENGINE_CACHE[db_url] = None
        return None


@contextmanager
def get_session(db_url: str | None = None) -> Iterator[Optional[Session]]:
    engine = get_engine(db_url or "sqlite:///./data/app.sqlite3")
    if engine is None or Session is object:
        yield None
        return
    session = Session(engine)  # type: ignore[call-arg]
    try:
        yield session
    finally:
        session.close()
