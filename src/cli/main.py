from __future__ import annotations

from typing import Optional

try:
    import typer
    from rich import print
except Exception:
    # 実行時には依存が必要。インポート時に落とさない
    class _Dummy:
        def __getattr__(self, name):
            raise RuntimeError("CLI dependencies not installed (typer, rich)")

    typer = _Dummy()  # type: ignore
    print = print  # type: ignore

from ..app.utils.timecycle import PomodoroConfig, PomodoroCycle


def _format_state(state: dict) -> str:
    phase_emoji = {
        "focus": "🔴",
        "short_break": "🟢",
        "long_break": "💤",
        "idle": "⚪",
    }.get(state.get("phase", "idle"), "⚪")
    mins = state.get("remaining", 0) // 60
    secs = state.get("remaining", 0) % 60
    return f"{phase_emoji} {state.get('phase')} {mins:02d}:{secs:02d} (cycle {state.get('cycle_count',0)})"


def build_app() -> "typer.Typer":
    app = typer.Typer(help="AI TODO + Pomodoro CLI")
    cycle = PomodoroCycle()

    @app.command("start")
    def start(
        focus: int = typer.Option(25, help="Focus minutes"),
        short: int = typer.Option(5, help="Short break minutes"),
        long: int = typer.Option(20, help="Long break minutes"),
        cycles: int = typer.Option(4, help="Cycles before long break"),
    ) -> None:
        cfg = PomodoroConfig(
            focus_minutes=focus,
            short_break_minutes=short,
            long_break_minutes=long,
            cycles_before_long_break=cycles,
        )
        cycle.reset(cfg)
        cycle.start()
        print(_format_state(cycle.state_dict()))

    @app.command("pause")
    def pause() -> None:
        cycle.pause()
        print(_format_state(cycle.state_dict()))

    @app.command("resume")
    def resume() -> None:
        cycle.resume()
        print(_format_state(cycle.state_dict()))

    @app.command("next")
    def next_cmd() -> None:
        cycle.next_phase()
        print(_format_state(cycle.state_dict()))

    @app.command("reset")
    def reset() -> None:
        cycle.reset()
        print(_format_state(cycle.state_dict()))

    return app


def main() -> None:
    app = build_app()
    try:
        app()  # type: ignore[misc]
    except Exception as e:  # 依存未導入時のメッセージ
        raise SystemExit(str(e))


if __name__ == "__main__":
    main()
