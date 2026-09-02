"""The loop: model, tools, browser, repeat until it answers.

ONE loop, used by both commands. `aihawk do` and `aihawk ui` differ in what they
do with the narration and in whether the conversation survives the instruction,
and in nothing else. They were briefly two loops, which is how a README sentence
saying "same machinery" becomes false without anybody editing it: the second copy
gets a fix, the first does not, and the two answers diverge for a task that
looks identical from outside.

The narration is a parameter rather than a mode. `do` passes a sink that drops
everything, `ui` passes the thing that pushes events to the page, and neither
appears in here. A loop that knows whether it is being watched is a loop with two
behaviours to test.
"""
from __future__ import annotations

import json
from typing import Any, Awaitable, Callable, List, Optional

SYSTEM_PROMPT = (
    "You are a browser automation agent. You control a real, stealth Firefox "
    "browser ONLY through the provided tools. Inspect pages with "
    "browser_read_text / browser_snapshot / browser_read_html before acting on "
    "them. A person may be watching the browser while you work, so prefer one "
    "clear action at a time over long chains. When the task is done, reply with "
    "the answer in plain text and do NOT call any more tools. Report only what "
    "the page actually shows."
)

Say = Callable[[str, str], Awaitable[None]]


async def _silent(_kind: str, _text: str) -> None:
    """The default narrator: says nothing, so `do` prints only its answer."""


def mcp_tools_to_openai(tools) -> List[dict]:
    """MCP tool descriptions as OpenAI function definitions.

    Two details are load-bearing and both come from the API rejecting the
    alternative: `parameters` must be an object and never None, and the
    description is truncated because a long one is rejected rather than trimmed.
    """
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


class Conversation:
    """One transcript, and the loop that grows it.

    Kept as an object because the interface needs the transcript to survive an
    instruction: "and now sort them by price" only means something if the model
    still knows what "them" was. `do` throws the object away after one call and
    gets the old one-shot behaviour for free.
    """

    def __init__(self, client, model: str, *, max_turns: int = 25) -> None:
        self.client = client
        self.model = model
        self.max_turns = max_turns
        self.messages: List[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.tool_defs: Optional[List[dict]] = None
        self.usage = {"prompt": 0, "completion": 0, "calls": 0, "last_prompt": 0}

    def _note_usage(self, resp) -> None:
        u = getattr(resp, "usage", None)
        if u is None:
            return
        last = getattr(u, "prompt_tokens", 0) or 0
        self.usage["prompt"] += last
        self.usage["completion"] += getattr(u, "completion_tokens", 0) or 0
        self.usage["calls"] += 1
        # The LAST turn's prompt, kept beside the running totals and not folded
        # into them. Each turn is sent the whole transcript, so the newest prompt
        # size IS the current occupancy of the context window; adding them up
        # counts every earlier turn again and races past any limit within a few
        # messages, which would make a meter built on it worse than none.
        self.usage["last_prompt"] = last

    async def run(self, task: str, call_tool, tools, *, say: Say = _silent,
                  describe=None) -> str:
        """Run one instruction to an answer.

        `call_tool(name, args)` performs a tool call and returns the MCP result;
        `tools` is the server's tool list. Both are passed rather than a session,
        so this has no opinion about how the browser is reached - which is what
        lets the interface serialise its calls against the screenshot pump.
        """
        if self.tool_defs is None:
            self.tool_defs = mcp_tools_to_openai(tools)
        self.messages.append({"role": "user", "content": task})

        for _turn in range(self.max_turns):
            resp = self.client.chat.completions.create(
                model=self.model, messages=self.messages,
                tools=self.tool_defs, tool_choice="auto", temperature=0,
            )
            self._note_usage(resp)
            await say("usage", json.dumps(self.usage))
            msg = resp.choices[0].message
            self.messages.append(msg.model_dump())

            if getattr(msg, "content", None):
                await say("said", msg.content)
            if not msg.tool_calls:
                return msg.content or ""

            for call in msg.tool_calls:
                name = call.function.name
                try:
                    args = json.loads(call.function.arguments or "{}")
                except json.JSONDecodeError as exc:
                    # Recoverable: telling the model its arguments were unreadable
                    # lets it try again. Raising would end the whole task over one
                    # malformed message.
                    await say("err", f"{name}: unreadable arguments ({exc})")
                    self.messages.append({"role": "tool", "tool_call_id": call.id,
                                          "content": f"arguments were not valid JSON: {exc}"})
                    continue

                await say("tool", f"{name} {describe(name, args)}".strip()
                          if describe else name)
                try:
                    text = _result_text(await call_tool(name, args))
                except Exception as exc:
                    text = f"{type(exc).__name__}: {exc}"
                    await say("err", text)
                else:
                    await say("result", text[:1200])
                self.messages.append({"role": "tool", "tool_call_id": call.id,
                                      "content": text[:8000]})

        raise RuntimeError(f"task did not finish within max_turns={self.max_turns}")


async def run_task(mcp, task: str, *, client, model: str, max_turns: int = 25) -> str:
    """One instruction, one answer, no narration. What `aihawk do` runs."""
    tools = (await mcp.list_tools()).tools
    convo = Conversation(client, model, max_turns=max_turns)
    return await convo.run(task, mcp.call_tool, tools)
