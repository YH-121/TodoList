from __future__ import annotations

from typing import Any, Dict

try:
    from fastapi import APIRouter
except Exception:
    class APIRouter:  # type: ignore
        def __init__(self, *args, **kwargs):
            raise RuntimeError("FastAPI is not installed.")

from ..utils.timecycle import PomodoroConfig, PomodoroCycle, Phase

router = APIRouter()

_cycle = PomodoroCycle(PomodoroConfig())


@router.post("/start")
def start_timer(cfg: Dict[str, Any] | None = None) -> dict:
    if cfg:
        config = PomodoroConfig(**cfg)
    else:
        config = _cycle.config
    _cycle.reset(config)
    _cycle.start()
    return _cycle.state_dict()


@router.post("/pause")
def pause_timer() -> dict:
    _cycle.pause()
    return _cycle.state_dict()


@router.post("/resume")
def resume_timer() -> dict:
    _cycle.resume()
    return _cycle.state_dict()


@router.post("/reset")
def reset_timer() -> dict:
    _cycle.reset()
    return _cycle.state_dict()


@router.post("/next")
def next_cycle() -> dict:
    _cycle.next_phase()
    return _cycle.state_dict()


@router.get("/state")
def state() -> dict:
    return _cycle.state_dict()
