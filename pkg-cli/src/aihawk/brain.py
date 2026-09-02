"""What turns a typed sentence into browser actions, and narrates while it does.

The shell was built with this slot deliberately empty and a stub in it, so that
the seam a model plugs into would be exercised rather than imagined. This module
fills the slot. There are two implementations and both are real:

`LiteralBrain` understands five literal commands and no language at all. It is
not a fallback for a missing key and it is not a demo prop: it is how the whole
surface can be driven, and tested, with no model, no key and no spending. When
something looks wrong in the UI, being able to issue exactly one action and see
exactly what came back is the difference between a bug report and a guess.

`OpenRouterBrain` is the product. It is the same loop the `do` command runs,
with one difference that matters: it says what it is doing while it does it. A
loop that returns an answer after ninety seconds of silence is a batch job; the
same loop narrating each step is something a person can watch, interrupt and
trust. The narration is not logging bolted on, it is the feature.
"""
from __future__ import annotations

import json
from typing import Any, Awaitable, Callable, List

from . import actions_help
from .agent import mcp_tools_to_openai
from .link import Link, text_of

Say = Callable[[str, str], Awaitable[None]]

SYSTEM_PROMPT = (
    "You are a browser automation agent. You control a real, stealth Firefox "
    "browser ONLY through the provided tools. Inspect pages with "
    "browser_read_text / browser_snapshot / browser_read_html before acting on "
    "them. A person is watching the browser while you work, so prefer one clear "
    "action at a time over long chains. When the task is done, reply with the "
    "answer in plain text and do NOT call any more tools. Report only what the "
    "page actually shows."
)


class Brain:
    """One method, on purpose.

    Whatever fills this slot - a model, a script, a recorded trace - receives
    what the user said, a way to act, and a way to narrate. Nothing above it
    needs to know which of those it is.
    """

    async def handle(self, text: str, link: Link, say: Say) -> None:
        raise NotImplementedError


class LiteralBrain(Brain):
    """Understands literal commands and nothing else. Explicitly a placeholder."""

    HELP = ("I am a placeholder, not a model. I understand: "
            "`go <url>`, `read [selector]`, `click <selector>`, "
            "`type <selector> <text>`, `shot`. "
            "Start the interface with an OpenRouter key to get a real one.")

    async def handle(self, text: str, link: Link, say: Say) -> None:
        parts = text.strip().split(None, 1)
        verb = parts[0].lower() if parts else ""
        rest = parts[1] if len(parts) > 1 else ""

        if verb in ("go", "open", "navigate") and rest:
            await say("tool", f"browser_navigate {rest}")
            await say("result", await link.call_text("browser_navigate", {"url": rest}))
        elif verb == "read":
            sel = rest or "body"
            await say("tool", f"browser_read_text {sel}")
            await say("result", await link.call_text("browser_read_text", {"selector": sel}))
        elif verb == "click" and rest:
            await say("tool", f"browser_click {rest}")
            await say("result", await link.call_text("browser_click", {"selector": rest}))
        elif verb == "type" and " " in rest:
            selector, value = rest.split(None, 1)
            await say("tool", f"browser_type {selector}")
            await say("result", await link.call_text(
                "browser_type", {"selector": selector, "text": value}))
        elif verb == "shot":
            await say("tool", "browser_take_screenshot")
            await say("result", "taken; the view on the right is live anyway")
            await link.call("browser_take_screenshot")
        else:
            await say("said", self.HELP)


class OpenRouterBrain(Brain):
    """The agent loop, narrating each step as it takes it.

    Conversation is kept ACROSS instructions, which is what makes the follow-up
    box on the left useful: "and now sort them by price" only means anything if
    the model still knows what "them" was. The transcript is trimmed nowhere yet,
    and that is a known limit rather than an oversight - see `turns` below.
    """

    def __init__(self, client, model: str, *, max_turns: int = 25) -> None:
        self._client = client
        self._model = model
        self._max_turns = max_turns
        self._messages: List[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
        self._tool_defs = None

    @property
    def messages(self) -> List[dict]:
        return self._messages

    async def handle(self, text: str, link: Link, say: Say) -> None:
        if self._tool_defs is None:
            self._tool_defs = mcp_tools_to_openai(link.tools)

        self._messages.append({"role": "user", "content": text})

        for turn in range(self._max_turns):
            resp = self._client.chat.completions.create(
                model=self._model, messages=self._messages,
                tools=self._tool_defs, tool_choice="auto", temperature=0,
            )
            msg = resp.choices[0].message
            self._messages.append(msg.model_dump())

            if getattr(msg, "content", None):
                # The model's own words. Shown even when it also calls a tool,
                # because "I will check the basket first" is the sentence that
                # makes the next five tool lines readable.
                await say("said", msg.content)

            if not msg.tool_calls:
                return

            for call in msg.tool_calls:
                name = call.function.name
                try:
                    args = json.loads(call.function.arguments or "{}")
                except json.JSONDecodeError as exc:
                    # A model can emit malformed arguments. Telling it so is
                    # recoverable; raising here would end the whole task.
                    await say("err", f"{name}: unreadable arguments ({exc})")
                    self._messages.append({
                        "role": "tool", "tool_call_id": call.id,
                        "content": f"arguments were not valid JSON: {exc}",
                    })
                    continue

                await say("tool", f"{name} {actions_help.summarise(name, args)}".strip())
                try:
                    result = text_of(await link.call(name, args))
                except Exception as exc:
                    result = f"{type(exc).__name__}: {exc}"
                    await say("err", result)
                else:
                    await say("result", result[:1200])
                self._messages.append({
                    "role": "tool", "tool_call_id": call.id, "content": result[:8000],
                })

        await say("err", f"stopped after {self._max_turns} turns without an answer")
