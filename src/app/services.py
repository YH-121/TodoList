from __future__ import annotations

from contextlib import AbstractContextManager
from datetime import datetime
from typing import Callable, Iterable, List, Optional

from . import schemas
from .db import get_session
from .utils.timecycle import PomodoroCycle, PomodoroConfig

try:
    from sqlmodel import Session, select
    SQLMODEL_AVAILABLE = True
except Exception:
    Session = object  # type: ignore
    SQLMODEL_AVAILABLE = False


class TodoService:
    def __init__(
        self,
        session_factory: Optional[Callable[[], AbstractContextManager[Optional[Session]]]] = None,
        use_memory: Optional[bool] = None,
    ) -> None:
        self._session_factory = session_factory or (lambda: get_session())
        self._use_memory = bool(use_memory) or not SQLMODEL_AVAILABLE
        self._store: dict[int, schemas.Task] = {}
        self._next_id = 1

    # ---- In-memory helpers ----
    def _mem_create(self, payload: schemas.TaskCreate) -> schemas.TaskRead:
        now = datetime.utcnow()
        task = schemas.Task(
            id=self._next_id,
            title=payload.title,
            description=payload.description,
            due_at=payload.due_at,
            priority=payload.priority,
            tags=list(payload.tags or []),
            done=payload.done if hasattr(payload, "done") else False,
            created_at=now,
            updated_at=now,
        )
        self._store[self._next_id] = task
        self._next_id += 1
        return schemas.TaskRead.model_validate(task)  # type: ignore[attr-defined]

    def _mem_list(
        self,
        q: Optional[str],
        tag: Optional[str],
        done: Optional[bool],
        from_dt: Optional[datetime],
        to_dt: Optional[datetime],
    ) -> List[schemas.TaskRead]:
        items: Iterable[schemas.Task] = self._store.values()
        if q:
            ql = q.lower()
            items = [
                t
                for t in items
                if ql in t.title.lower()
                or (t.description or "").lower().find(ql) >= 0
            ]
        if tag:
            items = [t for t in items if tag in (t.tags or [])]
        if done is not None:
            items = [t for t in items if bool(t.done) is bool(done)]
        if from_dt:
            items = [t for t in items if t.due_at and t.due_at >= from_dt]
        if to_dt:
            items = [t for t in items if t.due_at and t.due_at <= to_dt]
        return [schemas.TaskRead.model_validate(t) for t in items]  # type: ignore[attr-defined]

    def _mem_get(self, id: int) -> Optional[schemas.Task]:
        return self._store.get(id)

    def _mem_update(self, id: int, patch: schemas.TaskUpdate) -> Optional[schemas.TaskRead]:
        t = self._store.get(id)
        if not t:
            return None
        data = patch.model_dump(exclude_unset=True)  # type: ignore[attr-defined]
        for k, v in data.items():
            setattr(t, k, v)
        t.updated_at = datetime.utcnow()
        return schemas.TaskRead.model_validate(t)  # type: ignore[attr-defined]

    def _mem_delete(self, id: int) -> bool:
        return self._store.pop(id, None) is not None

    # ---- Public API ----
    def create_task(self, payload: schemas.TaskCreate) -> schemas.TaskRead:
        if self._use_memory:
            return self._mem_create(payload)
        with self._session_factory() as session:
            if session is None:
                # DB 未利用時のフォールバック
                return self._mem_create(payload)
            task = schemas.Task(**payload.model_dump())  # type: ignore[arg-type, attr-defined]
            session.add(task)
            session.commit()
            session.refresh(task)
            return schemas.TaskRead.model_validate(task)  # type: ignore[attr-defined]

    def list_tasks(
        self,
        q: Optional[str] = None,
        tag: Optional[str] = None,
        done: Optional[bool] = None,
        from_dt: Optional[datetime] = None,
        to_dt: Optional[datetime] = None,
    ) -> List[schemas.TaskRead]:
        if self._use_memory:
            return self._mem_list(q, tag, done, from_dt, to_dt)
        with self._session_factory() as session:
            if session is None:
                return self._mem_list(q, tag, done, from_dt, to_dt)
            stmt = select(schemas.Task)
            if q:
                like = f"%{q}%"
                stmt = stmt.where(
                    (schemas.Task.title.ilike(like))
                    | (schemas.Task.description.ilike(like))  # type: ignore[arg-type]
                )
            if done is not None:
                stmt = stmt.where(schemas.Task.done == bool(done))
            if from_dt is not None:
                stmt = stmt.where(schemas.Task.due_at >= from_dt)
            if to_dt is not None:
                stmt = stmt.where(schemas.Task.due_at <= to_dt)
            # Note: SQLite JSON contains for tag is non-trivial; skip for robustness
            rows = session.exec(stmt).all()
            return [schemas.TaskRead.model_validate(t) for t in rows]  # type: ignore[attr-defined]

    def get_task(self, id: int) -> Optional[schemas.TaskRead]:
        if self._use_memory:
            t = self._mem_get(id)
            return schemas.TaskRead.model_validate(t) if t else None  # type: ignore[attr-defined]
        with self._session_factory() as session:
            if session is None:
                t = self._mem_get(id)
                return schemas.TaskRead.model_validate(t) if t else None  # type: ignore[attr-defined]
            obj = session.get(schemas.Task, id)
            return schemas.TaskRead.model_validate(obj) if obj else None  # type: ignore[attr-defined]

    def update_task(self, id: int, patch: schemas.TaskUpdate) -> Optional[schemas.TaskRead]:
        if self._use_memory:
            return self._mem_update(id, patch)
        with self._session_factory() as session:
            if session is None:
                return self._mem_update(id, patch)
            obj = session.get(schemas.Task, id)
            if not obj:
                return None
            data = patch.model_dump(exclude_unset=True)  # type: ignore[attr-defined]
            for k, v in data.items():
                setattr(obj, k, v)
            obj.updated_at = datetime.utcnow()
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return schemas.TaskRead.model_validate(obj)  # type: ignore[attr-defined]

    def delete_task(self, id: int) -> bool:
        if self._use_memory:
            return self._mem_delete(id)
        with self._session_factory() as session:
            if session is None:
                return self._mem_delete(id)
            obj = session.get(schemas.Task, id)
            if not obj:
                return False
            session.delete(obj)
            session.commit()
            return True


class TimerService:
    def __init__(self, config: PomodoroConfig | None = None) -> None:
        self.cycle = PomodoroCycle(config)

    def start(self, config: PomodoroConfig | None = None) -> dict:
        if config:
            self.cycle.reset(config)
        self.cycle.start()
        return self.cycle.state_dict()

    def pause(self) -> dict:
        self.cycle.pause()
        return self.cycle.state_dict()

    def resume(self) -> dict:
        self.cycle.resume()
        return self.cycle.state_dict()

    def reset(self) -> dict:
        self.cycle.reset()
        return self.cycle.state_dict()

    def next(self) -> dict:
        self.cycle.next_phase()
        return self.cycle.state_dict()

    def state(self) -> dict:
        return self.cycle.state_dict()
