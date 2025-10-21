# AI TODO Agent + Pomodoro Timer

Minimal skeleton for API/CLI/GUI integrating TODO management and Pomodoro cycles.

## Quick Start

- API: `uv run uvicorn src.app.main:app --reload`
- CLI: `uv run python -m src.cli.main start --focus 25 --short 5 --long 20 --cycles 4`

## Timer Settings

```
{
  "focus_minutes": 25,
  "short_break_minutes": 5,
  "long_break_minutes": 20,
  "cycles_before_long_break": 4
}
```

See `docs/` for API and architecture notes.
