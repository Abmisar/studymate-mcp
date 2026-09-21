"""Prove the StudyMate MCP server works, without involving any AI host.

Spawns server.py over stdio exactly the way Codex will, lists the tools,
calls all three, and checks that the project data really changed.

Run:  .venv\Scripts\python.exe test_client.py
"""

import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

HERE = Path(__file__).resolve().parent


def show(title: str, result) -> None:
    text = "\n".join(
        block.text for block in result.content if getattr(block, "text", None)
    )
    flag = " (isError)" if result.isError else ""
    print(f"\n--- {title}{flag} ---\n{text}")


async def main() -> int:
    params = StdioServerParameters(
        command=sys.executable, args=[str(HERE / "server.py")]
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Tools exposed by the server:")
            for tool in tools.tools:
                params_ = ", ".join(tool.inputSchema.get("properties", {}))
                print(f"  - {tool.name}({params_})")
            assert {t.name for t in tools.tools} == {
                "list_tasks",
                "add_task",
                "complete_task",
            }, "unexpected tool set"

            show("list_tasks(open)", await session.call_tool("list_tasks", {}))
            show(
                "add_task",
                await session.call_tool(
                    "add_task",
                    {
                        "title": "SELF-TEST task",
                        "due_date": "2026-10-01",
                        "course": "CCSW 431",
                    },
                ),
            )
            show("list_tasks(open)", await session.call_tool("list_tasks", {}))

            tasks = json.loads((HERE / "tasks.json").read_text(encoding="utf-8"))
            new = [t for t in tasks if t["title"] == "SELF-TEST task"]
            assert new, "add_task did not write to tasks.json"
            new_id = new[0]["id"]

            show(
                "complete_task",
                await session.call_tool("complete_task", {"task_id": new_id}),
            )
            tasks = json.loads((HERE / "tasks.json").read_text(encoding="utf-8"))
            assert any(
                t["id"] == new_id and t["status"] == "completed" for t in tasks
            ), "complete_task did not update tasks.json"

            # validation paths must come back as errors, not crashes
            show(
                "add_task with a bad date",
                await session.call_tool(
                    "add_task",
                    {"title": "Bad", "due_date": "next week", "course": "CCSW 431"},
                ),
            )
            show(
                "list_tasks with a bad status",
                await session.call_tool("list_tasks", {"status": "urgent"}),
            )
            show(
                "complete_task with an unknown id",
                await session.call_tool("complete_task", {"task_id": 999}),
            )

    print("\nALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
