from __future__ import annotations

from datetime import datetime
from typing import Optional

try:
    from sqlmodel import SQLModel, Field
except Exception:
    # SQLModel が未導入でも型崩れしない最低限のフォールバック
    from pydantic import BaseModel as SQLModel  # type: ignore

    def Field(default=None, **kwargs):  # type: ignore
        return default


class TaskBase(SQLModel):
    title: str
    due: Optional[datetime] = None


class Task(TaskBase, table=True):  # type: ignore[call-arg]
    id: Optional[int] = Field(default=None, primary_key=True)
    status: str = "todo"


class TaskCreate(TaskBase):
    pass


class TaskRead(TaskBase):
    id: int
    status: str
