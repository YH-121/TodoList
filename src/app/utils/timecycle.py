from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Phase(str, Enum):
    IDLE = "idle"
    FOCUS = "focus"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"


@dataclass
class PomodoroConfig:
    focus_minutes: int = 25
    short_break_minutes: int = 5
    long_break_minutes: int = 20
    cycles_before_long_break: int = 4

    @property
    def focus_seconds(self) -> int:
        return self.focus_minutes * 60

    @property
    def short_break_seconds(self) -> int:
        return self.short_break_minutes * 60

    @property
    def long_break_seconds(self) -> int:
        return self.long_break_minutes * 60


class PomodoroCycle:
    def __init__(self, config: PomodoroConfig | None = None) -> None:
        self.config = config or PomodoroConfig()
        self.phase: Phase = Phase.IDLE
        self.remaining: int = 0
        self.cycle_count: int = 0  # 完了した FOCUS 数
        self.running: bool = False
        self.paused: bool = False

    # 状態操作
    def reset(self, config: PomodoroConfig | None = None) -> None:
        if config:
            self.config = config
        self.phase = Phase.IDLE
        self.remaining = 0
        self.cycle_count = 0
        self.running = False
        self.paused = False

    def start(self) -> None:
        if self.phase == Phase.IDLE:
            self.phase = Phase.FOCUS
            self.remaining = self.config.focus_seconds
        self.running = True
        self.paused = False

    def pause(self) -> None:
        if self.running:
            self.paused = True

    def resume(self) -> None:
        if self.running and self.paused:
            self.paused = False

    def next_phase(self) -> None:
        # 明示遷移（残り時間に関わらず）
        if self.phase == Phase.FOCUS:
            self.cycle_count += 1
            if self.cycle_count % self.config.cycles_before_long_break == 0:
                self.phase = Phase.LONG_BREAK
                self.remaining = self.config.long_break_seconds
            else:
                self.phase = Phase.SHORT_BREAK
                self.remaining = self.config.short_break_seconds
        elif self.phase in (Phase.SHORT_BREAK, Phase.LONG_BREAK):
            self.phase = Phase.FOCUS
            self.remaining = self.config.focus_seconds
        elif self.phase == Phase.IDLE:
            self.phase = Phase.FOCUS
            self.remaining = self.config.focus_seconds

    def tick(self, seconds: int = 1) -> None:
        if not self.running or self.paused:
            return
        self.remaining = max(0, self.remaining - seconds)
        if self.remaining == 0:
            # 自動遷移
            self.next_phase()

    # 観測
    def state_dict(self) -> dict:
        return {
            "phase": self.phase.value,
            "remaining": self.remaining,
            "cycle_count": self.cycle_count,
            "running": self.running,
            "paused": self.paused,
            "config": {
                "focus_minutes": self.config.focus_minutes,
                "short_break_minutes": self.config.short_break_minutes,
                "long_break_minutes": self.config.long_break_minutes,
                "cycles_before_long_break": self.config.cycles_before_long_break,
            },
        }
