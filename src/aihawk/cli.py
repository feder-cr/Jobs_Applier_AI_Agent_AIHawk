"""aihawk CLI: serve the page that drives a stealth browser with an LLM."""
from __future__ import annotations

import asyncio
import os

import click

from .llm import BASE_URL, resolve_key, resolve_model

BROWSER_OPTIONS = [
    click.option("--proxy", default=None, help="Proxy URL for the stealth browser."),
    click.option("--seed", type=int, default=None, help="Deterministic fingerprint seed."),
    click.option("--headed", is_flag=True, help="Run the browser headed."),
    click.option("--binary", default=None, help="Path to a specific engine binary."),
    click.option("--profile-dir", default=None,
                 help="Persistent profile dir; logins survive across runs."),
]


def browser_options(fn):
    for opt in reversed(BROWSER_OPTIONS):
        fn = opt(fn)
    return fn


@click.group()
def main() -> None:
    """Drive a stealth browser with an LLM.

    The model comes from OpenRouter and nowhere else: pass --openrouter-key or
    set OPENROUTER_API_KEY. Without one the interface refuses to start - an
    agent is a model with a browser, and there is no half of it to serve. To
    drive the browser by hand without a model, use the invisible_playwright
    library directly: same engine, Playwright's whole API.

    Said here rather than only in the subcommand because this is the first page
    anybody reads, and a key requirement discovered from an error message is a
    key requirement discovered too late.
    """


@main.command()
@click.option("--openrouter-key", default=None,
              help="OpenRouter API key (or env OPENROUTER_API_KEY). Required: "
                   "the interface does not start without a model.")
@click.option("--model", default=None, help="Model id (or env AIHAWK_MODEL).")
@click.option("--host", default="127.0.0.1", show_default=True,
              help="Interface bind address. Leave it on loopback unless you mean it.")
@click.option("--port", type=int, default=8765, show_default=True)
@browser_options
def ui(openrouter_key, model, host, port, proxy, seed, headed, binary, profile_dir):
    """Serve the two-pane interface: conversation left, live browser right.

    Requires an OpenRouter key: an agent is a model with a browser, and
    without the model there is nothing honest to serve. Driving the browser
    by hand, no model and nothing spent, is the invisible_playwright
    library's job - same engine, Playwright's whole API.
    """
    from .brain import OpenRouterBrain
    from .link import Link
    from .llm import make_client
    from .web import ChatService, build_app

    key = openrouter_key or os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise click.ClickException(
            "no OpenRouter key. Pass --openrouter-key or set "
            "OPENROUTER_API_KEY. To drive the browser without a model, use "
            "the invisible_playwright library directly: same engine, "
            "Playwright's whole API.")
    mdl = resolve_model(model, os.environ)
    brain = OpenRouterBrain(make_client(key), mdl)
    label = mdl
    click.echo("model    %s via %s" % (mdl, BASE_URL))

    opts = {"proxy": proxy, "seed": seed, "headed": headed,
            "binary": binary, "profile_dir": profile_dir}

    async def serve() -> None:
        import uvicorn

        link = await Link(opts, key=key).open()
        click.echo("browser  ready, %d tools" % len(link.tools))
        click.echo("open     http://%s:%d" % (host, port))
        service = ChatService(link, brain, model_label=label)
        app = build_app(link, service)
        server = uvicorn.Server(uvicorn.Config(app, host=host, port=port,
                                               log_level="warning"))
        try:
            await server.serve()
        finally:
            await link.close()

    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
