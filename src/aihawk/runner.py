"""How the browser server is started, and what the child is allowed to know.

`child_env` is the security-relevant half and it lives here alone: the OpenRouter
key is removed from the environment the engine is started with, and the browser
options are the only things added. The child drives a browser; it has no use for
a model key, and the cheapest way to keep a secret out of a process is not to
hand it over.

Spawning is `Link`'s. This module used to build its own StdioServerParameters as
well, which meant two places knew the command, the arguments and the environment
of the child - and a change to how the server is launched had to be made twice
or be wrong once.
"""
from __future__ import annotations

from typing import Any, Mapping


def child_env(opts: Mapping[str, Any], base_env: Mapping[str, str]) -> dict:
    """The environment the browser server is started with.

    The pop is the point. Everything else is options travelling under the names
    the engine reads, and an absent option adds no variable at all rather than an
    empty one, because an empty STEALTHFOX_PROXY is not the same as no proxy.
    """
    env = dict(base_env)
    env.pop("OPENROUTER_API_KEY", None)   # the child (browser server) never needs it
    if opts.get("proxy"):
        env["STEALTHFOX_PROXY"] = str(opts["proxy"])
    if opts.get("seed") is not None:
        env["STEALTHFOX_SEED"] = str(opts["seed"])
    if opts.get("headed"):
        env["STEALTHFOX_HEADLESS"] = "0"
    if opts.get("binary"):
        env["STEALTHFOX_BINARY"] = str(opts["binary"])
    if opts.get("profile_dir"):
        env["STEALTHFOX_PROFILE_DIR"] = str(opts["profile_dir"])
    return env


async def drive(task: str, *, opts: Mapping[str, Any], key: str, model: str) -> str:
    """One instruction, one answer, browser closed after. What `aihawk do` runs.

    The same Link the interface holds open for a session, opened and closed
    around a single task. The difference between the two commands is how long the
    connection lives, and nothing else.
    """
    from .agent import Conversation
    from .link import Link
    from .llm import make_client

    link = await Link(opts).open()
    try:
        convo = Conversation(make_client(key), model)
        return await convo.run(task, link.call, link.tools)
    finally:
        await link.close()
