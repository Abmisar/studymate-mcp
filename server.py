"""StudyMate Tools - a minimal MCP server for the StudyMate project.

Exposes three task operations to any MCP-capable host (Codex, Claude, ...)
over the local STDIO transport:

    list_tasks(status)                  -> READ
    add_task(title, due_date, course)   -> WRITE
    complete_task(task_id)              -> WRITE

Project data lives in a local JSON file next to this script.
No network port, no API keys, no unrestricted file access for the model.
"""

from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

# The server name the host will display.
mcp = FastMCP("StudyMate Tools")

HERE = Path(__file__).resolve().parent
DATA_FILE = HERE / "tasks.json"
SEED_FILE = HERE / "tasks.seed.json"

VALID_STATUS = ("open", "completed", "all")


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def _log(message: str) -> None:
    """Diagnostics go to stderr. stdout is reserved for the MCP protocol."""
    print(f"[studymate] {message}", file=sys.stderr, flush=True)


def _load() -> list[dict[str, Any]]:
    """Read the task list from disk, restoring the seed file if needed."""
    if not DATA_FILE.exists() and SEED_FILE.exists():
        shutil.copyfile(SEED_FILE, DATA_FILE)
        _log("tasks.json was missing - restored from tasks.seed.json")
    if not DATA_FILE.exists():
        return []
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def _save(tasks: list[dict[str, Any]]) -> None:
    """Write the task list back to disk."""
    DATA_FILE.write_text(
        json.dumps(tasks, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _format(tasks: list[dict[str, Any]], heading: str) -> str:
    """Render tasks as a readable, aligned table."""
    if not tasks:
        return f"{heading}: none found."
    width = max(len(t["title"]) for t in tasks)
    lines = [f"{heading} ({len(tasks)}):"]
    for t in tasks:
        mark = "x" if t["status"] == "completed" else " "
        lines.append(
            f"  [{mark}] #{t['id']:<3} {t['title']:<{width}}  "
            f"{t['course']:<10} due {t['due_date']}"
        )
    return "\n".join(lines)


# --------------------------------------------------------------------------
# tools - the type hints and docstrings below become the schema the host sees
# --------------------------------------------------------------------------
@mcp.tool()
def list_tasks(status: str = "open") -> str:
    """List StudyMate tasks by status.

    Args:
        status: Which tasks to return - "open", "completed", or "all".
    """
    if status not in VALID_STATUS:
        raise ValueError(
            f"status must be one of {', '.join(VALID_STATUS)} (got {status!r})"
        )

    tasks = _load()
    selected = tasks if status == "all" else [t for t in tasks if t["status"] == status]
    selected.sort(key=lambda t: t["due_date"])
    _log(f"list_tasks(status={status!r}) -> {len(selected)} task(s)")
    return _format(selected, f"{status.capitalize()} StudyMate tasks")


@mcp.tool()
def add_task(title: str, due_date: str, course: str) -> str:
    """Create a new StudyMate task.

    Args:
        title: Short description of the task.
        due_date: Due date in YYYY-MM-DD format.
        course: Course the task belongs to, for example "CCSW 431".
    """
    title = title.strip()
    course = course.strip()

    if not title:
        raise ValueError("title must not be empty")
    if len(title) > 120:
        raise ValueError("title must be 120 characters or fewer")
    if not course:
        raise ValueError("course must not be empty")
    try:
        datetime.strptime(due_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError(
            f"due_date must be in YYYY-MM-DD format (got {due_date!r})"
        ) from None

    tasks = _load()
    new_id = max((t["id"] for t in tasks), default=0) + 1
    task = {
        "id": new_id,
        "title": title,
        "course": course,
        "due_date": due_date,
        "status": "open",
    }
    tasks.append(task)
    _save(tasks)
    _log(f"add_task -> created #{new_id}")
    return f"Created task #{new_id}: {title} ({course}, due {due_date})"


@mcp.tool()
def complete_task(task_id: int) -> str:
    """Mark one StudyMate task as completed.

    Args:
        task_id: The numeric id of the task to complete.
    """
    tasks = _load()
    for task in tasks:
        if task["id"] == task_id:
            if task["status"] == "completed":
                raise ValueError(f"task #{task_id} is already completed")
            task["status"] = "completed"
            _save(tasks)
            _log(f"complete_task -> completed #{task_id}")
            return f"Completed task #{task_id}: {task['title']}"
    known = ", ".join(str(t["id"]) for t in tasks) or "none"
    raise ValueError(f"no task with id {task_id} (known ids: {known})")


if __name__ == "__main__":
    _log(f"starting StudyMate Tools - data file: {DATA_FILE}")
    mcp.run(transport="stdio")
