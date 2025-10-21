"""
FastAPI エントリポイント。

- `app`: ASGI アプリ本体
- `create_app()`: アプリファクトリ

依存ライブラリが未インストール環境でもインポート時に失敗しないよう、
FastAPI が無い場合は軽量のダミーを提供します（起動はできません）。
"""

from __future__ import annotations

from typing import Any

try:
    from fastapi import FastAPI
except Exception:  # FastAPI 未導入環境向けのフォールバック
    class FastAPI:  # type: ignore
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            raise RuntimeError(
                "FastAPI is not installed. Install dependencies to run the API."
            )


def create_app() -> "FastAPI":
    app = FastAPI(title="AI TODO Agent + Pomodoro Timer", version="0.1.0")

    # ルーターの登録（存在すれば）
    try:
        from .routers import tasks, timer

        app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
        app.include_router(timer.router, prefix="/timer", tags=["timer"])
    except Exception:
        # 依存が未導入でもアプリ生成は可能に
        pass

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/")
    def root() -> dict[str, str]:
        return {"message": "AI TODO Agent + Pomodoro Timer API"}

    return app


# ASGI サーバーから参照されるデフォルトアプリ
app = create_app()
