from __future__ import annotations

from typing import Any

try:
    from fastapi import FastAPI
except Exception:  # FastAPI 未導入環境でもフォールバック
    class FastAPI:  # type: ignore
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            raise RuntimeError(
                "FastAPI is not installed. Install dependencies to run the API."
            )


def create_app(use_memory: bool = False) -> "FastAPI":
    app = FastAPI(title="AI TODO Agent + Pomodoro Timer", version="0.1.0")

    # DB 初期化（存在時のみ）。サービスもここでバインド
    try:
        from .db import get_engine
        from sqlmodel import SQLModel
        engine = None if use_memory else get_engine()
        if engine is not None and hasattr(SQLModel, "metadata"):
            SQLModel.metadata.create_all(engine)  # type: ignore[attr-defined]

        from .services import TodoService

        # engine がない場合はメモリ利用
        app.state.todo_service = TodoService(use_memory=(engine is None))
    except Exception:
        # 依存が未導入でもアプリ生成は可能に
        pass

    # ルーターの登録（存在すれば）
    try:
        from .routers import tasks, timer

        app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
        app.include_router(timer.router, prefix="/timer", tags=["timer"])
    except Exception:
        pass

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/")
    def root() -> dict[str, str]:
        return {"message": "AI TODO Agent + Pomodoro Timer API"}

    return app


# ASGI サーバから参照されるデフォルトアプリ
app = create_app()

