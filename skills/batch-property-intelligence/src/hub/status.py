"""
Status file the watcher writes and the launcher polls.

Tiny JSON file at data/status.json. No locking — eventual consistency is
fine for the launcher's 1s poll cadence.
"""

import json
from datetime import datetime
from pathlib import Path


DEFAULT_STATUS_PATH = Path("data/status.json")


def write_status(
    state: str,
    last_event: str | None = None,
    db_stats: dict | None = None,
    path: Path = DEFAULT_STATUS_PATH,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "state": state,
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "last_event": last_event,
        "db": db_stats or {},
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def read_status(path: Path = DEFAULT_STATUS_PATH) -> dict:
    if not path.exists():
        return {"state": "unknown", "updated_at": None, "last_event": None, "db": {}}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"state": "unknown", "updated_at": None, "last_event": "status file unreadable", "db": {}}
