from __future__ import annotations

from typing import List

from . import schemas
from .utils.timecycle import PomodoroCycle, PomodoroConfig


class TodoService:
    def list_tasks(self) -> List[schemas.TaskRead]:
        return []

    def create_task(self, payload: schemas.TaskCreate) -> schemas.TaskRead:
        return schemas.TaskRead(id=0, title=payload.title, due=payload.due, status="todo")


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
