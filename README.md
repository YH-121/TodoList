# AI TODO Agent + Pomodoro Timer

Minimal skeleton for API/CLI/GUI integrating TODO management and Pomodoro cycles.

## Quick Start

- API: `uv run uvicorn src.app.main:app --reload`
- CLI: `uv run python -m src.cli.main start --focus 25 --short 5 --long 20 --cycles 4`

## Tasks CRUD

- In-memory mode (no DB): the API works even if SQLModel is not installed. Tests use this path.
- DB mode (SQLite via SQLModel): tables are created automatically if SQLModel is available. Default DB path is `./data/app.sqlite3` and its directory is auto-created.

Examples (PowerShell):

```
# Start API (reload)
uv run uvicorn src.app.main:app --reload

# Create a task
Invoke-RestMethod -Uri http://127.0.0.1:8000/tasks -Method POST -ContentType 'application/json' -Body '{"title":"test"}'

# List tasks
Invoke-RestMethod -Uri http://127.0.0.1:8000/tasks -Method GET

# Get, update, delete
Invoke-RestMethod -Uri http://127.0.0.1:8000/tasks/1 -Method GET
Invoke-RestMethod -Uri http://127.0.0.1:8000/tasks/1 -Method PATCH -ContentType 'application/json' -Body '{"done":true}'
Invoke-RestMethod -Uri http://127.0.0.1:8000/tasks/1 -Method DELETE
```

Or cURL:

```
curl -X POST http://127.0.0.1:8000/tasks -H "content-type: application/json" -d '{"title":"test"}'
```

Interactive docs: open `http://127.0.0.1:8000/docs`.

Note on sound: the `sound` extra is currently empty to avoid Windows build issues with `playsound`. If you need sound later, manually install a backend such as `playsound==1.2.2` or `pygame` and wire it in `src/app/routers/timer.py`.

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
