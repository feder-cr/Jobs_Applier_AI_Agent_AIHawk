"""LLM loop: bridge MCP browser_* tools into OpenRouter tool-calls, stop when
the model returns a final answer (no tool call)."""
from __future__ import annotations

import json
from typing import Any, List

SYSTEM_PROMPT = (
    "You are a browser automation agent. You control a real, stealth Firefox "
    "browser ONLY through the provided tools. Inspect pages with "
    "browser_read_text / browser_snapshot. When the task is done, reply with "
    "the answer in plain text and do NOT call any more tools. Report only what "
    "the page actually shows."
)


def mcp_tools_to_openai(tools) -> List[dict]:
    out = []
    for t in tools:
        out.append({
            "type": "function",
            "function": {
                "name": t.name,
                "description": (getattr(t, "description", "") or "")[:1024],
                "parameters": getattr(t, "inputSchema", None) or {"type": "object", "properties": {}},
            },
        })
    return out


def _result_text(result) -> str:
    if not getattr(result, "content", None):
        return ""
    first = result.content[0]
    return getattr(first, "text", None) or "[non-text result]"


async def run_task(mcp, task: str, *, client, model: str, max_turns: int = 25) -> str:
    tool_defs = mcp_tools_to_openai((await mcp.list_tools()).tools)
    messages: List[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": task},
    ]
    for _turn in range(max_turns):
        resp = client.chat.completions.create(
            model=model, messages=messages, tools=tool_defs,
            tool_choice="auto", temperature=0,
        )
        msg = resp.choices[0].message
        messages.append(msg.model_dump())
        if not msg.tool_calls:
            return msg.content or ""
        for call in msg.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments or "{}")
            result = await mcp.call_tool(name, args)
            messages.append({
                "role": "tool", "tool_call_id": call.id,
                "content": _result_text(result)[:8000],
            })
    raise RuntimeError(f"task did not finish within max_turns={max_turns}")
