from __future__ import annotations

from datetime import datetime
from typing import List, Optional

try:
    from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
except Exception:
    # 型付けのためのダミー。実行には fastapi が必須
    class APIRouter:  # type: ignore
        def __init__(self, *args, **kwargs):
            raise RuntimeError("FastAPI is not installed.")

    def Depends(x):  # type: ignore
        return x

    class HTTPException(Exception):  # type: ignore
        def __init__(self, status_code: int, detail: str):
            super().__init__(detail)

    class Request:  # type: ignore
        app: object

    class Response:  # type: ignore
        def __init__(self, status_code: int | None = None):
            ...

    class Query:  # type: ignore
        def __init__(self, default=None, alias: str | None = None):
            ...

    class status:  # type: ignore
        HTTP_201_CREATED = 201
        HTTP_204_NO_CONTENT = 204

from .. import schemas
from ..services import TodoService

router = APIRouter()


def get_service(request: Request) -> TodoService:
    svc = getattr(getattr(request, "app", object()), "state", None)
    if svc and getattr(svc, "todo_service", None) is not None:
        return svc.todo_service  # type: ignore[attr-defined]
    # フォールバック：デフォルト実装（メモリ利用可）
    return TodoService()


@router.get("/", response_model=List[schemas.TaskRead])
def list_tasks(
    q: Optional[str] = None,
    tag: Optional[str] = None,
    done: Optional[bool] = None,
    from_: Optional[datetime] = Query(None, alias="from"),
    to: Optional[datetime] = None,
    svc: TodoService = Depends(get_service),
) -> List[schemas.TaskRead]:
    return svc.list_tasks(q=q, tag=tag, done=done, from_dt=from_, to_dt=to)


@router.post("/", response_model=schemas.TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(payload: schemas.TaskCreate, svc: TodoService = Depends(get_service)) -> schemas.TaskRead:
    return svc.create_task(payload)


@router.get("/{id}", response_model=schemas.TaskRead)
def get_task(id: int, svc: TodoService = Depends(get_service)) -> schemas.TaskRead:
    t = svc.get_task(id)
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    return t


@router.patch("/{id}", response_model=schemas.TaskRead)
def update_task(id: int, payload: schemas.TaskUpdate, svc: TodoService = Depends(get_service)) -> schemas.TaskRead:
    t = svc.update_task(id, payload)
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    return t


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(id: int, svc: TodoService = Depends(get_service)) -> Response:
    ok = svc.delete_task(id)
    if not ok:
        raise HTTPException(status_code=404, detail="Task not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

