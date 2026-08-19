"""aihawk CLI: drive a stealth browser with an LLM from one command."""
from __future__ import annotations

import asyncio
import os

import click

from .llm import resolve_key, resolve_model
from .runner import drive


@click.group()
def main() -> None:
    """Drive a stealth browser with an LLM."""


@main.command()
@click.argument("task")
@click.option("--openrouter-key", default=None, help="OpenRouter API key (or env OPENROUTER_API_KEY).")
@click.option("--model", default=None, help="Model id (or env AIHAWK_MODEL).")
@click.option("--proxy", default=None, help="Proxy URL for the stealth browser.")
@click.option("--seed", type=int, default=None, help="Deterministic fingerprint seed.")
@click.option("--headed", is_flag=True, help="Run the browser headed.")
@click.option("--binary", default=None, help="Path to a specific engine binary.")
def do(task, openrouter_key, model, proxy, seed, headed, binary):
    """Run TASK in a stealth browser and print the result."""
    try:
        key = resolve_key(openrouter_key, os.environ)
    except RuntimeError as e:
        raise click.ClickException(str(e))
    mdl = resolve_model(model, os.environ)
    opts = {"proxy": proxy, "seed": seed, "headed": headed, "binary": binary}
    result = asyncio.run(drive(task, opts=opts, key=key, model=mdl))
    click.echo(result)


if __name__ == "__main__":
    main()
