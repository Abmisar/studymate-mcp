# StudyMate Tools

A small, complete MCP server: three task-management tools that an AI host can
discover and call over the local stdio transport. Built for the CCSW 431
presentation *Build Your Own MCP Server*, and kept deliberately readable -
`server.py` is one file, no framework around it.

The Model Context Protocol lets a host (Codex, Claude, any MCP client) find
tools at runtime and call them. The model never touches your files. It sees
three tool schemas; every read and write happens inside this server process.

## The tools

| Tool | Kind | Purpose |
|---|---|---|
| `list_tasks(status)` | READ | List tasks by `open`, `completed`, or `all` |
| `add_task(title, due_date, course)` | WRITE | Create a validated task |
| `complete_task(task_id)` | WRITE | Mark one task as completed |

Project data is a local JSON file. No network port, no API keys, no
unrestricted file access for the model.

## See it work

You do not need an AI host, a network connection or an API key to prove the
server works. Python 3.10 or newer is the only requirement.

**Windows**

```powershell
git clone https://github.com/Abmisar/studymate-mcp
cd studymate-mcp
python -m venv .venv
.\.venv\Scripts\pip.exe install "mcp[cli]<2"
.\.venv\Scripts\python.exe test_client.py
```

**macOS / Linux**

```bash
git clone https://github.com/Abmisar/studymate-mcp
cd studymate-mcp
python3 -m venv .venv
.venv/bin/pip install "mcp[cli]<2"
.venv/bin/python test_client.py
```

`test_client.py` spawns `server.py` over stdio exactly the way a host does,
lists the tools, calls all three, checks that the JSON file really changed,
and exercises the validation paths. Abridged output:

```text
Tools exposed by the server:
  - list_tasks(status)
  - add_task(title, due_date, course)
  - complete_task(task_id)

--- list_tasks(open) ---
Open StudyMate tasks (4):
  [ ] #1   Submit Lab 2 solution         CECY 482   due 2026-09-23
  [ ] #2   Finish Lab 2 report           CCSW 431   due 2026-09-24
  [ ] #3   Review MCP reference servers  CCSW 431   due 2026-09-27
  [ ] #4   Prepare subnetting exercises  Networks   due 2026-09-30

--- add_task ---
Created task #7: SELF-TEST task (CCSW 431, due 2026-10-01)

--- add_task with a bad date (isError) ---
Error executing tool add_task: due_date must be in YYYY-MM-DD format (got 'next week')

ALL CHECKS PASSED
```

The seed holds six tasks, two of them already completed, so the next new id
is 7. The run leaves a `SELF-TEST task` behind - clear it with
`reset_demo.py`.

## The schema is generated, not hand-written

This is the part worth understanding. You write an ordinary typed function
with a docstring:

```python
@mcp.tool()
def add_task(title: str, due_date: str, course: str) -> str:
    """Create a new StudyMate task.

    Args:
        title: Short description of the task.
        due_date: Due date in YYYY-MM-DD format.
        course: Course the task belongs to, for example "CCSW 431".
    """
```

and the SDK derives the schema the host discovers, from the type hints and
the docstring alone:

```json
{
  "properties": {
    "title":    { "type": "string" },
    "due_date": { "type": "string" },
    "course":   { "type": "string" }
  },
  "required": ["title", "due_date", "course"]
}
```

(Trimmed for readability: the SDK also emits a display `title` for each
field.) Nothing here is maintained by hand, so the schema cannot drift away
from the code.

Types are not the whole story, though - `due_date: str` only says "a string".
The format check lives in the function body, which is why
`due_date="next week"` comes back as a tool error rather than a bad row in
the data file. Same for an unknown status and an unknown task id.

## Use it with Codex

Register the server with absolute paths on your own machine:

```powershell
codex mcp add studymate -- <repo>\.venv\Scripts\python.exe <repo>\server.py
```

```bash
codex mcp add studymate -- <repo>/.venv/bin/python <repo>/server.py
```

`codex mcp list` shows it as `enabled`. Inside Codex, `/mcp verbose` prints
the three tool names - plain `/mcp` only reports the count. Then ask for
something in words:

```
Use the studymate list_tasks tool to list all open tasks
```

Launch the host from a folder **outside** this repo. Started inside it, the
host can simply read `tasks.json` with a shell command and never call a tool
at all.

## Human approval on the writes

`~/.codex/config.toml` keeps the read tool automatic and asks for
confirmation before either write tool runs:

```toml
[mcp_servers.studymate]
default_tools_approval_mode = "approve"

[mcp_servers.studymate.tools.add_task]
approval_mode = "prompt"

[mcp_servers.studymate.tools.complete_task]
approval_mode = "prompt"
```

Those modes decide **whether** Codex asks. One more setting decides **who
answers**: `approvals_reviewer`, at the top level of the same file. Leave it
at `auto_review` and an automated reviewer approves the write for you, which
on screen looks exactly like no approval at all. To see the confirmation
yourself, set it to `user` and restart Codex:

```toml
approvals_reviewer = "user"
```

The split is enforced by the host, not by the model's good manners. Under a
policy that refuses approvals outright, the read still runs and the write
comes back `MCP tool call requires approval, but approval policy is never`.

## What is in the repo

| File | Purpose |
|---|---|
| `server.py` | The MCP server - the code shown on slide 8 |
| `test_client.py` | Proves the server works without any AI host |
| `tasks.seed.json` | Clean starting data |
| `reset_demo.py` | Restores `tasks.json` from the seed |
| `DEMO.md` | Runbook for the live presentation |

`tasks.json` is not in the repo. It is live data: `server.py` creates it from
`tasks.seed.json` the first time a tool runs.

## Notes

The SDK is pinned to v1 on purpose. MCP 2.x renamed `FastMCP` to
`MCPServer`, and the presentation slides show the `FastMCP` code. Installed
and tested against 1.30.0.

`DEMO.md` is the presenter's own runbook and its paths are the presenter's,
not yours. This README is the one written for anyone cloning the repo.

This is a teaching demo, not a production service: local stdio transport,
JSON file storage, single user. A remote deployment would need authentication
and authorization on top.
