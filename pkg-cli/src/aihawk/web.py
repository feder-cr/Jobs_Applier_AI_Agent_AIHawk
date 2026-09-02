"""The two-pane interface: conversation on the left, the live browser on the right.

This used to live inside the MCP server and reach the browser through a Python
object in the same process. It lives here now, and it reaches the browser the way
everybody else does: over MCP, calling the same fourteen tools any agent gets.
The server went back to being only a server.

That is not a tidier arrangement of the same code, it changes what is true about
each side. The MCP package now has no opinion about being looked at, so nothing
in it has to be kept working for the sake of a page. And this interface has no
privileged access, so anything it can do, somebody else's client can also do -
which is the strongest guarantee available that the tools are sufficient.

Three consequences, each handled rather than hidden:

  The live view cannot ask "is a browser running" without starting one, because
  `session_list_pages` calls `ensure`. `Link` remembers whether an instruction
  has been issued and the view stays quiet until then.

  Screenshots and actions now share one pipe. They are serialised in `Link`, and
  they would have been serialised by the browser anyway.

  The page URL is no longer free. It is fetched on its own slower timer rather
  than with every frame, so watching costs one cheap call every two seconds.
"""
from __future__ import annotations

import asyncio
import json
from typing import AsyncIterator, Dict, List, Optional

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response, StreamingResponse
from starlette.routing import Route

from .brain import Brain, LiteralBrain
from .link import Link, image_of

PAGE = """<!doctype html>
<meta charset="utf-8"><title>AIHawk</title>
<style>
  :root { color-scheme: dark; }
  * { box-sizing: border-box; }
  body { margin:0; height:100vh; display:flex; background:#101317; color:#e7eaec;
         font:14px/1.55 -apple-system,Segoe UI,sans-serif; }
  #left { width:44%; min-width:360px; display:flex; flex-direction:column;
          border-right:1px solid #2a3037; }
  #head { padding:10px 14px; border-bottom:1px solid #2a3037; display:flex;
          align-items:center; gap:10px; }
  #head b { font-size:13px; letter-spacing:.02em; }
  .badge { margin-left:auto; font:11px ui-monospace,Consolas,monospace;
           color:#a2abb3; background:#1f242a; border:1px solid #2a3037;
           padding:3px 8px; border-radius:999px; }
  #log { flex:1; overflow:auto; padding:16px; }
  .msg { margin-bottom:12px; }
  .you { color:#e7eaec; background:#1f242a; padding:8px 12px; border-radius:10px;
         display:inline-block; max-width:90%; }
  .step { display:flex; gap:8px; align-items:baseline; }
  .n { color:#4c555d; font:11px ui-monospace,Consolas,monospace; min-width:1.6em;
       text-align:right; flex:none; }
  .tool { color:#e2a06a; font:12px/1.5 ui-monospace,Consolas,monospace; }
  .result { color:#7c868e; white-space:pre-wrap; font:12px/1.5 ui-monospace,Consolas,monospace;
            border-left:2px solid #2a3037; padding-left:10px; margin:3px 0 0 2.3em; }
  .said { color:#c9d1d6; }
  .err { color:#e8836b; font:12px/1.5 ui-monospace,Consolas,monospace; }
  #busy { color:#7c868e; font-style:italic; padding:0 16px 10px; display:none; }
  form { display:flex; gap:8px; padding:12px; border-top:1px solid #2a3037; }
  input { flex:1; background:#1f242a; border:1px solid #2a3037; color:#e7eaec;
          padding:10px 12px; border-radius:8px; font:inherit; }
  input:disabled { opacity:.5; }
  button { background:#e38a5d; border:0; color:#101317; font-weight:600;
           padding:0 16px; border-radius:8px; cursor:pointer; }
  #right { flex:1; display:flex; flex-direction:column; min-width:0; }
  #bar { padding:8px 12px; border-bottom:1px solid #2a3037; color:#7c868e;
         font:12px ui-monospace,Consolas,monospace; display:flex; gap:10px; }
  #url { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  #state { margin-left:auto; flex:none; }
  main { flex:1; display:flex; align-items:flex-start; justify-content:center;
         overflow:auto; padding:12px; background:#0b0d10; }
  /* display:none here, and whoever shows it must write 'block': assigning the
     empty string removes the inline style and falls back on THIS rule, which
     leaves the image hidden with the pixels already inside it. That defect
     shipped once and a green test could not see it. */
  img { max-width:100%; border:1px solid #2a3037; border-radius:6px; display:none; }
  #empty { color:#4c555d; margin:auto; }
</style>
<div id="left">
  <div id="head"><b>AIHawk</b><span class="badge" id="model">no model</span></div>
  <div id="log"></div>
  <div id="busy">working...</div>
  <form id="f"><input id="i" placeholder="tell it what to do" autocomplete="off"><button>send</button></form>
</div>
<div id="right">
  <div id="bar"><b>browser</b><span id="url"></span><span id="state">idle</span></div>
  <main><img id="frame" alt="live browser view"><div id="empty">nothing running yet</div></main>
</div>
<script>
const log = document.getElementById('log'), busy = document.getElementById('busy');
let step = 0;
function add(kind, text) {
  const wrap = document.createElement('div');
  wrap.className = 'msg';
  if (kind === 'tool') {
    step += 1;
    wrap.innerHTML = '<div class="step"><span class="n"></span><span class="tool"></span></div>';
    wrap.querySelector('.n').textContent = step;
    wrap.querySelector('.tool').textContent = text;
  } else {
    const s = document.createElement('div');
    s.className = kind === 'you' ? 'you' : kind;
    s.textContent = text;
    wrap.appendChild(s);
  }
  log.appendChild(wrap); log.scrollTop = log.scrollHeight;
}
const es = new EventSource('/chat/events');
es.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.kind === 'busy') { busy.style.display = m.text === '1' ? 'block' : 'none'; return; }
  if (m.kind === 'model') { document.getElementById('model').textContent = m.text; return; }
  add(m.kind, m.text);
};
document.getElementById('f').onsubmit = async (e) => {
  e.preventDefault();
  const i = document.getElementById('i');
  const text = i.value.trim(); if (!text) return;
  i.value = ''; add('you', text);
  await fetch('/chat/send', {method:'POST', headers:{'Content-Type':'application/json'},
                            body: JSON.stringify({text})});
};

const img = document.getElementById('frame'), empty = document.getElementById('empty');
const state = document.getElementById('state'), urlEl = document.getElementById('url');
async function tick() {
  try {
    const r = await fetch('/live/frame?t=' + Date.now(), {cache: 'no-store'});
    if (r.status === 204) {
      img.style.display = 'none'; empty.style.display = ''; state.textContent = 'idle';
    } else if (r.ok) {
      const blob = await r.blob();
      const old = img.src;
      img.src = URL.createObjectURL(blob);
      if (old.startsWith('blob:')) URL.revokeObjectURL(old);
      img.style.display = 'block'; empty.style.display = 'none';
      state.textContent = 'live';
    } else if (r.status === 503) {
      // Busy, not broken: a screenshot cannot be taken mid-navigation, and at
      // this rate an ordinary navigation produces several in a row. The last
      // frame stays on screen, because a stale picture of where the browser was
      // beats a red word about where it is going.
      state.textContent = 'busy';
    } else { state.textContent = 'error ' + r.status; }
  } catch (e) { state.textContent = 'offline'; }
  // Ask for the next frame only once this one has landed, or a browser slower
  // than the interval accumulates requests it can never serve.
  setTimeout(tick, 500);
}
async function where() {
  try {
    const r = await fetch('/live/where', {cache: 'no-store'});
    if (r.ok) { const j = await r.json(); urlEl.textContent = j.url || ''; }
  } catch (e) {}
  setTimeout(where, 2000);
}
tick(); where();
</script>
"""


class ChatService:
    """One conversation, its listeners, and the link it drives."""

    def __init__(self, link: Link, brain: Optional[Brain] = None,
                 model_label: str = "no model") -> None:
        self._link = link
        self._brain = brain or LiteralBrain()
        self._listeners: List[asyncio.Queue] = []
        self.history: List[Dict[str, str]] = []
        self.model_label = model_label
        self._busy = asyncio.Lock()

    def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self._listeners.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        if q in self._listeners:
            self._listeners.remove(q)

    async def emit(self, kind: str, text: str) -> None:
        event = {"kind": kind, "text": text}
        # `busy` is a state flag, not a line of the conversation: replaying it
        # to somebody who opens the page later would show a spinner for work
        # that finished an hour ago.
        if kind != "busy":
            self.history.append(event)
        for q in list(self._listeners):
            q.put_nowait(event)

    async def send(self, text: str) -> None:
        async with self._busy:
            await self.emit("busy", "1")
            try:
                await self._brain.handle(text, self._link, self.emit)
            except Exception as exc:
                await self.emit("err", f"{type(exc).__name__}: {exc}")
            finally:
                await self.emit("busy", "0")


def build_app(link: Link, service: ChatService) -> Starlette:
    async def root(_request: Request) -> HTMLResponse:
        return HTMLResponse(PAGE)

    async def send(request: Request) -> JSONResponse:
        body = await request.json()
        text = (body or {}).get("text", "")
        if not text:
            return JSONResponse({"error": "empty"}, status_code=400)
        # Detached: an instruction takes seconds to minutes and the caller must
        # not sit on an open request while the narration streams over SSE.
        asyncio.create_task(service.send(text))
        return JSONResponse({"accepted": True})

    async def events(_request: Request) -> StreamingResponse:
        q = service.subscribe()

        async def stream() -> AsyncIterator[bytes]:
            try:
                yield b"data: " + json.dumps(
                    {"kind": "model", "text": service.model_label}).encode() + b"\n\n"
                for past in list(service.history):
                    yield b"data: " + json.dumps(past).encode() + b"\n\n"
                while True:
                    event = await q.get()
                    yield b"data: " + json.dumps(event).encode() + b"\n\n"
            finally:
                service.unsubscribe(q)

        return StreamingResponse(stream(), media_type="text/event-stream",
                                 headers={"Cache-Control": "no-store"})

    async def frame(_request: Request) -> Response:
        if not link.touched:
            # 204, not an error: nothing is wrong, there is simply nothing to
            # look at. Asking the server would START a browser, which is exactly
            # what a view is not allowed to cause.
            return Response(status_code=204)
        try:
            got = image_of(await link.call("browser_take_screenshot"))
        except Exception as exc:
            return JSONResponse({"error": str(exc)[:200]}, status_code=503)
        if got is None:
            return Response(status_code=204)
        png, mime = got
        return Response(png, media_type=mime, headers={"Cache-Control": "no-store"})

    async def where(_request: Request) -> JSONResponse:
        """The address the browser is on.

        Asked with `browser_evaluate` and NOT with `session_list_pages`, whose
        description says "id, title, url, and which one is active" and which
        returns `["tab-1"]`: ids only, measured on 0.8.1. That description is
        what a model reads as documentation, so the mismatch is filed against
        the server rather than worked around silently - this comment is the
        pointer to it. When the tool returns what it promises, this should use
        it, because one round trip beats evaluating script in the page.
        """
        if not link.touched:
            return JSONResponse({"url": ""})
        try:
            raw = await link.call_text("browser_evaluate", {"expression": "location.href"})
        except Exception:
            return JSONResponse({"url": ""})
        url = (raw or "").strip().strip('"')
        return JSONResponse({"url": url if url.startswith("http") else ""})

    return Starlette(routes=[
        Route("/", root),
        Route("/chat/send", send, methods=["POST"]),
        Route("/chat/events", events),
        Route("/live/frame", frame),
        Route("/live/where", where),
    ])
