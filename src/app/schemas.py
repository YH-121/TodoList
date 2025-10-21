from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

try:
    from sqlmodel import Field, SQLModel
    from sqlalchemy import Column
    from sqlalchemy.dialects.sqlite import JSON
    SQLMODEL_AVAILABLE = True
except Exception:
    from pydantic import BaseModel as SQLModel  # type: ignore

    def Field(default=None, **kwargs):  # type: ignore
        return default

    def Column(*args, **kwargs):  # type: ignore
        return None

    class JSON:  # type: ignore
        pass

    SQLMODEL_AVAILABLE = False


def _utcnow() -> datetime:
    return datetime.utcnow()


class TaskBase(SQLModel):
    title: str
    description: Optional[str] = None
    due_at: Optional[datetime] = None
    priority: Literal["low", "normal", "high"] = "normal"
    # SQLModel あり: JSON カラムで保持 / なし: Pydantic リスト
    if SQLMODEL_AVAILABLE:
        tags: list[str] = Field(default_factory=list, sa_column=Column(JSON))  # type: ignore[arg-type]
    else:
        tags: list[str] = []  # type: ignore[assignment]
    done: bool = False


class Task(TaskBase, table=True):  # type: ignore[call-arg]
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)


class TaskCreate(TaskBase):
    pass


class TaskRead(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime


class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_at: Optional[datetime] = None
    priority: Optional[Literal["low", "normal", "high"]] = None
    tags: Optional[list[str]] = None
    done: Optional[bool] = None
