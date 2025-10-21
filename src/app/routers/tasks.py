from __future__ import annotations

from typing import List

try:
    from fastapi import APIRouter
except Exception:
    # 型付けのためのダミー。実行には fastapi が必要
    class APIRouter:  # type: ignore
        def __init__(self, *args, **kwargs):
            raise RuntimeError("FastAPI is not installed.")

from .. import schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.TaskRead])
def list_tasks() -> List[schemas.TaskRead]:
    # TODO: DB から取得。いまは空配列を返す
    return []


@router.post("/", response_model=schemas.TaskRead)
def create_task(payload: schemas.TaskCreate) -> schemas.TaskRead:
    # TODO: DB に保存。いまは入力値から簡易生成
    return schemas.TaskRead(id=0, title=payload.title, due=payload.due, status="todo")
