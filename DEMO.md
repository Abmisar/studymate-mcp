# StudyMate Tools - Live Demo Runbook

CCSW 431 | Covers slides 9 and 10. Run time: about 4 minutes.

Project folder: `C:\Users\abdul\studymate-mcp`
Everything below has been tested on this machine.

---

## Step 0 - Reset before every rehearsal and before the real run

```powershell
cd C:\Users\abdul\studymate-mcp
.\.venv\Scripts\python.exe reset_demo.py
```

This restores `tasks.json` from `tasks.seed.json`, so the task you add on
stage is genuinely new. **Do not skip this.**

Starting data: 6 tasks, 4 open, 2 completed.

Optional pre-flight check with no AI host involved:

```powershell
.\.venv\Scripts\python.exe test_client.py
```

It spawns the server over stdio, lists the tools, calls all three, checks
the JSON really changed, and ends with `ALL CHECKS PASSED`. Run Step 0
again afterwards to clear the self-test task.

---

## Slide 9 - Registration and verification

### 1. Register (already done; this is the command to show on screen)

```powershell
codex mcp add studymate -- C:\Users\abdul\studymate-mcp\.venv\Scripts\python.exe C:\Users\abdul\studymate-mcp\server.py
```

### 2. Verify the server is registered

```powershell
codex mcp list
```

Point at the `studymate` row: the command, the args, status `enabled`.

### 3. Verify the tools are visible from inside Codex

```powershell
cd C:\Users\abdul
codex
```

**Start from your home folder, not the project folder.** If Codex is running
inside `studymate-mcp` it can simply read `tasks.json` with a shell command
and never call the tool, which would undercut the whole point.

No launch flag is needed. `approvals_reviewer` is set to `"user"` on line 18
of `~/.codex/config.toml` for this presentation, so a plain `codex` is
enough. This machine is normally `auto_review`, where an automated reviewer
approves tool calls on your behalf and you never see a prompt - that is what
silently swallowed the slide 10 dialog in two rehearsals. With `"user"` the
decision is yours again.

**Put it back after the talk** - line 18 of `~/.codex/config.toml`:

```toml
approvals_reviewer = "auto_review"
```

Then type:

```
/mcp verbose
```

Plain `/mcp` only shows `studymate: connected (3 tools)`. The `verbose` form
is the one that prints the tool names, so use it. It shows them
alphabetically as `add_task, complete_task, list_tasks`. **This is the
evaluation moment on slide 9.**

The same block shows `Auth: Unsupported` and `Resources: (none)`. Both are
expected and both have good answers below.

### 4. Read - let Codex call the tool

Type into Codex:

```
Use the studymate list_tasks tool to list all open tasks
```

Expect a `list_tasks` call and four open tasks, with no approval dialog.
Say out loud: Codex is not reading our JSON file, it is calling an approved
tool, and the file is not even in this folder.

---

## Slide 10 - Execution and human approval

### 5. Write

```
Use the studymate add_task tool to add "Finalize MCP presentation" for CCSW 431 due 2026-09-28
```

`add_task` and `complete_task` are registered with
`approval_mode = "prompt"`, so Codex asks for confirmation before running
them. The read tool `list_tasks` is registered with `approve`, so it runs
without interrupting you - that is why Step 4 had no dialog.

**Pause on that dialog** - it is the slide 10 "Control" bullet. Approve it.

If no dialog appears, check that line 18 of `~/.codex/config.toml` still
reads `approvals_reviewer = "user"`, and that you launched this Codex session
after it was set - the value is read once at startup. If it still does not
appear, go to Step 9, which blocks the write every time.

### 6. Prove the project data really changed

```
Use the studymate list_tasks tool to list open tasks again
```

The new task appears with its own id. For hard proof, in a second terminal:

```powershell
type C:\Users\abdul\studymate-mcp\tasks.json
```

### 7. Complete a task

```
Use the studymate complete_task tool to mark task 2 as completed
```

Approve, then:

```
Use the studymate list_tasks tool to list completed tasks
```

### 8. Show the schema doing real work (30 seconds, strong closer)

```
Use the studymate add_task tool to add "Bad date test" for CCSW 431 due next week
```

The server rejects it with `due_date must be in YYYY-MM-DD format (got
'next week')`. This is slide 5's "structured schemas are enforced" and
slide 14's "safety depends on how the tools are implemented".

### 9. Proof that the host gates the write tools (tested, always works)

Run these two commands in PowerShell, outside the Codex session. They use the
same approval policy, so the only difference between them is the tool.

Read - runs, no approval needed:

```powershell
cd C:\Users\abdul\studymate-mcp
codex exec --skip-git-repo-check -s read-only -c approval_policy='"never"' "Use the studymate list_tasks tool to list open tasks."
```

Write - blocked:

```powershell
codex exec --skip-git-repo-check -s read-only -c approval_policy='"never"' "Use the studymate add_task tool to add 'GATE PROBE' for CCSW 431 due 2026-10-05."
```

Codex reports:

```
mcp: studymate/add_task (failed)
MCP tool call requires approval, but approval policy is never
```

and `tasks.json` is unchanged. Same policy, same server: the read went through
and the write did not. That split comes from the per-tool `approval_mode`
settings, and the host enforced it - not the model's good manners. This is the
strongest version of the slide 10 argument.

## Plan B if the Codex session misbehaves on stage

Check your Codex quota before you start - `/status` inside Codex shows it
and when it resets. Every step that uses Codex spends quota; `test_client.py`
below spends none.

Non-interactive, tested, no TUI needed:

```powershell
codex exec --skip-git-repo-check -s read-only "Use the studymate list_tasks tool to list open tasks."
```

Or drop the AI host entirely and run the scripted proof, which needs no
network and no host:

```powershell
.\.venv\Scripts\python.exe test_client.py
```

Last resort, if you want a clickable interface: the official MCP Inspector. It
downloads itself through npx on first run, so do not reach for this on stage
unless you have already run it once beforehand.

```powershell
.\.venv\Scripts\mcp.exe dev server.py
```

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `studymate` missing from `codex mcp list` | Re-run the `codex mcp add` command in Step 1 |
| Tools do not appear in `/mcp` | Quit Codex and relaunch; servers are spawned at startup |
| The write runs with no confirmation dialog | `approvals_reviewer` is back to `auto_review`, or this session started before it was set to `"user"`. Check line 18 of `~/.codex/config.toml`, then quit and relaunch Codex |
| The task you add is already in the list | You skipped Step 0. Run `reset_demo.py` |
| Another server in the list shows red or failed | Not part of this demo. Say it is a different server whose login expired, and carry on |
| A red `exec_command failed ... apply deny-read ACLs` line | The Windows sandbox refused a shell command Codex tried first. It then used the MCP tool instead. This appeared in every tested run and never broke the demo |
| Want to remove the server afterwards | `codex mcp remove studymate` |

---

## Facts worth knowing before questions

- The SDK is pinned to `mcp<2` (installed: 1.30.0) on purpose. MCP 2.x
  renamed `FastMCP` to `MCPServer`, and slide 8 shows the `FastMCP` code.
  The live code and the slide match exactly.
- Approval configuration lives in `~/.codex/config.toml`:

```toml
[mcp_servers.studymate]
default_tools_approval_mode = "approve"

[mcp_servers.studymate.tools.add_task]
approval_mode = "prompt"

[mcp_servers.studymate.tools.complete_task]
approval_mode = "prompt"
```

  Codex validates these values and rejects anything else. The accepted set is
  `auto`, `prompt`, `writes`, `approve`. Tested on this machine: `approve`
  runs the tool without asking, `prompt` requires a human decision first.
- Those per-tool modes decide **whether** Codex asks. A separate setting,
  `approvals_reviewer` on line 18 of the same file, decides **who answers**.
  `auto_review` hands the question to an automated reviewer and looks on
  screen exactly like no approval at all; `user` puts it in front of you.
  Both failed rehearsals were this setting, not the server and not the
  per-tool approval modes.
- `codex mcp get studymate` prints the resolved settings, which is a quick way
  to confirm the approval mode is really in effect.

## One-line answers for likely questions

- **Why MCP instead of a REST call?** The host discovers the tools and their
  schemas at runtime, and the same server works in any MCP-capable host
  without new glue code.
- **Is the model reading our files?** No. It sees three tool schemas. All
  file access happens inside the server process.
- **What stops a bad write?** Type and format validation inside the tool,
  plus host-level human approval on the two write tools.
- **Is this production ready?** No. It is a local demo over stdio with JSON
  storage. A remote deployment would add authentication and authorization.
- **Where did the schema come from?** Python type hints and docstrings. The
  SDK generates the JSON schema the host sees.
- **Why does it say `Auth: Unsupported`?** The server runs locally over stdio,
  launched by the host itself. There is no network endpoint, so there is
  nothing to authenticate against. This is the local-first point on slide 13.
  A remote server would need authentication, which is the risk noted on
  slide 14.
- **Why are Resources and Prompts empty?** Slide 2 lists all three MCP
  building blocks, but this server deliberately exposes only tools. Task
  operations are actions, not context to load. Exposing nothing further is
  the least-capability principle from slide 13.
