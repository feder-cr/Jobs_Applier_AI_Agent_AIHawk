"""What turns a typed sentence into browser actions, and narrates while it does.

The shell was built with this slot deliberately empty and a stub in it, so that
the seam a model plugs into would be exercised rather than imagined. This module
fills the slot. There are two implementations and both are real:

`LiteralBrain` understands a handful of literal commands and no language at all.
It is
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

from typing import Awaitable, Callable

from . import actions_help
from .agent import Conversation
from .link import Link

Say = Callable[[str, str], Awaitable[None]]


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
            "`type <selector> <text>`, `tab`, `shot`. "
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
        elif verb == "tab":
            # Here so the placeholder can reach the whole surface, which is what
            # it is for: without it the tab strip could only be exercised with a
            # key and a model willing to open one.
            await say("tool", "session_new_page")
            await say("result", await link.call_text("session_new_page"))
        elif verb == "shot":
            await say("tool", "browser_take_screenshot")
            await say("result", "taken; the view on the right is live anyway")
            await link.call("browser_take_screenshot")
        else:
            await say("said", self.HELP)


class OpenRouterBrain(Brain):
    """The product: the shared loop, narrating each step as it takes it.

    The loop itself is `agent.Conversation`. This
    class supplies the two things that differ: a transcript that survives an
    instruction, so the follow-up box means something, and a narrator, so the
    work is visible while it happens rather than only when it ends.

    Briefly there were two loops. That is how a README sentence promising "same
    machinery" goes false with nobody editing it, and why this one is four lines.
    """

    def __init__(self, client, model: str, *, max_turns: int = 25) -> None:
        self._convo = Conversation(client, model, max_turns=max_turns)

    @property
    def usage(self) -> dict:
        return self._convo.usage

    @property
    def messages(self) -> list:
        return self._convo.messages

    async def handle(self, text: str, link: Link, say: Say) -> None:
        try:
            await self._convo.run(text, link.call, link.tools,
                                  say=say, describe=actions_help.summarise)
        except RuntimeError as exc:
            # The turn ceiling. It is the one failure a person can act on - by
            # narrowing the task - so it is said plainly rather than raised into
            # the generic handler that prefixes an exception class.
            await say("err", str(exc))
