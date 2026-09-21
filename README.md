# StudyMate Tools - MCP Server

A small, real MCP server built for the CCSW 431 presentation
*Build Your Own MCP Server*. It exposes three StudyMate task operations to an
MCP-capable host (Codex) over the local STDIO transport.

| Tool | Kind | Purpose |
|---|---|---|
| `list_tasks(status)` | READ | List tasks by `open`, `completed`, or `all` |
| `add_task(title, due_date, course)` | WRITE | Create a newly validated task |
| `complete_task(task_id)` | WRITE | Mark one task as completed |

Built with the official MCP Python SDK (`FastMCP`). Type hints and docstrings
become the tool schema the host discovers. Project data is a local JSON file.
No network port, no API keys, and the model never gets unrestricted file
access.

## Files

| File | Purpose |
|---|---|
| `server.py` | The MCP server - the code shown on slide 8 |
| `tasks.json` | Live project data the tools read and write |
| `tasks.seed.json` | Clean starting data |
| `reset_demo.py` | Restores `tasks.json` from the seed |
| `test_client.py` | Proves the server works without any AI host |
| `DEMO.md` | Step-by-step runbook for the live demo |

## Setup

```powershell
cd C:\Users\abdul\studymate-mcp
python -m venv .venv
.\.venv\Scripts\pip.exe install "mcp[cli]<2"
```

The SDK is pinned to v1 on purpose: MCP 2.x renamed `FastMCP` to
`MCPServer`, and the presentation shows the `FastMCP` code.
Installed version: 1.30.0.

## Register with Codex

```powershell
codex mcp add studymate -- C:\Users\abdul\studymate-mcp\.venv\Scripts\python.exe C:\Users\abdul\studymate-mcp\server.py
codex mcp list
```

Inside Codex, `/mcp` lists the server and its three tools.

## Human approval on writes

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
on screen looks exactly like no approval at all. For a live demo set it to
`user` and restart Codex:

```toml
approvals_reviewer = "user"
```

## Run the demo

See `DEMO.md`.
