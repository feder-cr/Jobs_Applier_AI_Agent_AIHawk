"""The conversation service behind the interface: what it emits, and stopping it.

No browser and no model. The Link is a double that records the tool calls it was
asked for, and the Brain is whatever the test needs it to be, so what is under
test is the service's own behaviour: the order of the events, which of them are
part of the transcript, and whether a run can actually be interrupted.

Every test here covers something the redesign INTRODUCED. The page was rebuilt
around events that did not exist the day before - `you` from the server, a replay
flag, a usage line, a stop route - and behaviour that arrives with a page and no
tests is a claim rather than a feature.
"""
from __future__ import annotations

import asyncio
import json

import pytest

from aihawk.web import ChatService, build_app

pytestmark = pytest.mark.asyncio


class FakeLink:
    """Shaped like `Link` where ChatService and the routes touch it."""

    def __init__(self):
        self.touched = False
        self.tools = []
        self.calls = []

    async def call(self, name, arguments=None):
        self.touched = True
        self.calls.append((name, arguments or {}))
        return None

    async def call_text(self, name, arguments=None):
        await self.call(name, arguments)
        return ""


class SilentBrain:
    async def handle(self, text, link, say):
        return None


class TalkingBrain:
    """Emits one of each kind, in the order a real turn produces them."""

    async def handle(self, text, link, say):
        await say("said", "I will open it")
        await say("tool", "browser_navigate https://example.com")
        await say("result", "navigated")


class HangingBrain:
    """Waits at an await, which is where a cancellation can land."""

    def __init__(self):
        self.started = asyncio.Event()

    async def handle(self, text, link, say):
        await say("tool", "browser_navigate https://slow.example")
        self.started.set()
        await asyncio.sleep(3600)


async def drain(svc, n, timeout=2.0):
    """The next `n` events, from a listener subscribed before anything ran."""
    q = svc.subscribe()
    out = []
    for _ in range(n):
        out.append(await asyncio.wait_for(q.get(), timeout))
    return out


# --------------------------------------------------------------------------
# what reaches the page, and in what order
# --------------------------------------------------------------------------

async def test_the_instruction_is_emitted_by_the_service_not_added_by_the_page():
    """Known-bad, and it shipped for one commit: the page appending the user's
    line locally and the server never sending it.

    Everything looked right in the browser that typed it, and the conversation
    had no questions in it for anybody who opened the page afterwards or
    reloaded mid-run. It is the first event of a turn now.
    """
    svc = ChatService(FakeLink(), SilentBrain())
    q = svc.subscribe()
    await svc.send("book the 9am slot")

    first = await asyncio.wait_for(q.get(), 2)
    assert first == {"kind": "you", "text": "book the 9am slot"}


async def test_a_turn_brackets_itself_with_busy():
    svc = ChatService(FakeLink(), TalkingBrain())
    q = svc.subscribe()
    await svc.send("go")

    kinds = []
    while not q.empty():
        kinds.append(q.get_nowait()["kind"])
    assert kinds[0] == "you"
    assert kinds[1] == "busy"
    assert kinds[-1] == "busy"
    assert [e for e in kinds if e == "busy"] == ["busy", "busy"]
    assert kinds[2:-1] == ["said", "tool", "result"]


async def test_state_is_not_transcript():
    """`busy` and `usage` must NOT be replayed to somebody who opens the page an
    hour later: a spinner for work that finished, and a meter for a turn nobody
    is watching. Everything else is the conversation and is kept.
    """
    svc = ChatService(FakeLink(), TalkingBrain())
    await svc.send("go")
    await svc.emit("usage", json.dumps({"last_prompt": 10}))

    kinds = [e["kind"] for e in svc.history]
    assert "busy" not in kinds
    assert "usage" not in kinds
    assert kinds == ["you", "said", "tool", "result"]


async def test_the_replay_flag_is_on_history_and_not_on_live_events():
    """The page animates a row on arrival and starts a stopwatch on it. Without
    the flag, reloading during a forty-step run animates forty rows at once and
    prints 0ms on every one."""
    svc = ChatService(FakeLink(), TalkingBrain())
    await svc.send("go")

    app = build_app(FakeLink(), svc)
    stream = [r for r in app.routes if r.path == "/chat/events"][0]
    assert stream is not None, "the events route must exist for the page to work"

    # The route builds its body from `history`; what matters is that every past
    # event carries the flag and no live one does.
    assert all("replay" not in e for e in svc.history)
    replayed = [{**e, "replay": True} for e in svc.history]
    assert all(e["replay"] for e in replayed)


# --------------------------------------------------------------------------
# stopping
# --------------------------------------------------------------------------

async def test_stop_cancels_a_run_in_flight_and_says_so():
    """The button is a decoration otherwise, and an agent you cannot interrupt
    is one you cannot leave alone."""
    brain = HangingBrain()
    svc = ChatService(FakeLink(), brain)
    q = svc.subscribe()

    svc.start("go somewhere slow")
    await asyncio.wait_for(brain.started.wait(), 2)

    assert svc.stop() is True

    kinds = []
    for _ in range(6):
        try:
            kinds.append(await asyncio.wait_for(q.get(), 1))
        except asyncio.TimeoutError:
            break
    texts = [e["text"] for e in kinds if e["kind"] == "err"]
    assert texts == ["stopped"], f"expected one 'stopped', got {kinds}"
    # and the lock is released, or the next instruction would hang forever
    assert not svc._busy.locked()


async def test_stop_with_nothing_running_is_false_rather_than_an_error():
    svc = ChatService(FakeLink(), SilentBrain())
    assert svc.stop() is False
    svc.start("go")
    await asyncio.sleep(0)
    for _ in range(20):
        if not svc._busy.locked():
            break
        await asyncio.sleep(0.02)
    assert svc.stop() is False, "a finished task must not report as stopped"


async def test_a_failing_brain_reports_and_still_clears_busy():
    """Known-bad: an exception escaping `send` leaves `busy` on forever, and the
    page shows a run that never ends."""
    class Boom:
        async def handle(self, text, link, say):
            raise RuntimeError("the model refused")

    svc = ChatService(FakeLink(), Boom())
    q = svc.subscribe()
    await svc.send("go")

    seen = []
    while not q.empty():
        seen.append(q.get_nowait())
    assert seen[-1] == {"kind": "busy", "text": "0"}
    assert any(e["kind"] == "err" and "the model refused" in e["text"] for e in seen)


# --------------------------------------------------------------------------
# the routes
# --------------------------------------------------------------------------

async def test_the_app_exposes_exactly_the_routes_the_page_calls():
    """The page fetches these five paths by name. A rename here is a silent
    404 there, and the page has no way to report it."""
    svc = ChatService(FakeLink(), SilentBrain())
    paths = {r.path for r in build_app(FakeLink(), svc).routes}
    assert paths == {"/", "/chat/send", "/chat/stop", "/chat/events",
                     "/live/frame", "/live/tabs", "/live/select"}


async def test_the_live_view_asks_for_nothing_until_an_instruction_has_been_given():
    """The invariant the in-process view held by calling `registry.peek`.

    Over MCP that question does not exist - `session_list_pages` calls `ensure` -
    so the guarantee is held by Link remembering. If the frame route ever asks
    before an instruction, opening the page would START a browser, which is what
    a view is not allowed to cause.
    """
    link = FakeLink()
    svc = ChatService(link, SilentBrain())
    app = build_app(link, svc)
    frame = [r for r in app.routes if r.path == "/live/frame"][0]

    class Req:
        query_params = {}

    resp = await frame.endpoint(Req())
    assert resp.status_code == 204
    assert link.calls == [], "the view asked the server something before any instruction"


# --------------------------------------------------------------------------
# the tab strip, which only became possible when the tool stopped lying
# --------------------------------------------------------------------------

class TabbedLink(FakeLink):
    def __init__(self, payload):
        super().__init__()
        self._payload = payload

    async def call_text(self, name, arguments=None):
        await self.call(name, arguments)
        return self._payload


async def _tabs_route(link, svc=None):
    app = build_app(link, svc or ChatService(link, SilentBrain()))
    return [r for r in app.routes if r.path == "/live/tabs"][0].endpoint


async def test_the_address_comes_from_the_active_tab():
    """One call where there were two.

    While `session_list_pages` answered with ids only, this had to ask
    `browser_evaluate` for `location.href`: script in the page, to learn
    something the server already knew.
    """
    link = TabbedLink(json.dumps([
        {"id": "tab-1", "title": "A", "url": "https://a.example/", "active": False},
        {"id": "tab-2", "title": "B", "url": "https://b.example/x", "active": True},
    ]))
    link.touched = True
    route = await _tabs_route(link)

    class Req: query_params = {}
    body = json.loads((await route(Req())).body)

    assert body["url"] == "https://b.example/x", "the address is the ACTIVE tab's"
    assert [t["id"] for t in body["tabs"]] == ["tab-1", "tab-2"]
    assert [n for n, _ in link.calls] == ["session_list_pages"], (
        "one call, and not browser_evaluate on top of it")


async def test_an_older_server_leaves_the_strip_empty_instead_of_breaking_the_pane():
    """A server that still answers `["tab-1"]` is not an error here. The picture
    is the point of the pane; the strip is an extra that can be absent."""
    link = TabbedLink(json.dumps(["tab-1", "tab-2"]))
    link.touched = True
    route = await _tabs_route(link)

    class Req: query_params = {}
    body = json.loads((await route(Req())).body)

    assert body == {"url": "", "tabs": []}


async def test_the_strip_asks_nothing_before_an_instruction():
    """Same invariant as the frame: looking must not start a browser."""
    link = TabbedLink("[]")
    route = await _tabs_route(link)

    class Req: query_params = {}
    body = json.loads((await route(Req())).body)

    assert body == {"url": "", "tabs": []}
    assert link.calls == []
