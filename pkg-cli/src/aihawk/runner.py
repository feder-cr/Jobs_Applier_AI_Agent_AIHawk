"""Spawn the invisible-playwright-mcp server as a stdio child, drive it."""
from __future__ import annotations

import sys
from typing import Any, Mapping

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from .agent import run_task
from .llm import make_client


def child_env(opts: Mapping[str, Any], base_env: Mapping[str, str]) -> dict:
    env = dict(base_env)
    if opts.get("proxy"):
        env["STEALTHFOX_PROXY"] = str(opts["proxy"])
    if opts.get("seed") is not None:
        env["STEALTHFOX_SEED"] = str(opts["seed"])
    if opts.get("headed"):
        env["STEALTHFOX_HEADLESS"] = "0"
    if opts.get("binary"):
        env["STEALTHFOX_BINARY"] = str(opts["binary"])
    return env


async def drive(task: str, *, opts: Mapping[str, Any], key: str, model: str) -> str:
    import os
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "invisible_playwright_mcp"],
        env=child_env(opts, os.environ),
    )
    client = make_client(key)
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as mcp:
            await mcp.initialize()
            return await run_task(mcp, task, client=client, model=model)
