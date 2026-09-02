"""aihawk CLI: drive a stealth browser with an LLM, from one command or from a page."""
from __future__ import annotations

import asyncio
import os

import click

from .llm import BASE_URL, resolve_key, resolve_model
from .runner import drive

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

    The model comes from OpenRouter and nowhere else, so `do` needs a key:
    pass --openrouter-key or set OPENROUTER_API_KEY. `ui` runs without one on
    a literal-command placeholder, which is enough to see the interface work.

    Said here rather than only in the subcommands because this is the first
    page anybody reads, and a key requirement discovered from an error message
    is a key requirement discovered too late.
    """


@main.command()
@click.argument("task")
@click.option("--openrouter-key", default=None,
              help="OpenRouter API key (or env OPENROUTER_API_KEY).")
@click.option("--model", default=None, help="Model id (or env AIHAWK_MODEL).")
@browser_options
def do(task, openrouter_key, model, proxy, seed, headed, binary, profile_dir):
    """Run TASK in a stealth browser and print the result."""
    try:
        key = resolve_key(openrouter_key, os.environ)
    except RuntimeError as e:
        raise click.ClickException(str(e))
    mdl = resolve_model(model, os.environ)
    opts = {"proxy": proxy, "seed": seed, "headed": headed,
            "binary": binary, "profile_dir": profile_dir}
    result = asyncio.run(drive(task, opts=opts, key=key, model=mdl))
    click.echo(result)


@main.command()
@click.option("--openrouter-key", default=None,
              help="OpenRouter API key (or env OPENROUTER_API_KEY). Without one "
                   "the interface runs on the literal-command placeholder.")
@click.option("--model", default=None, help="Model id (or env AIHAWK_MODEL).")
@click.option("--host", default="127.0.0.1", show_default=True,
              help="Interface bind address. Leave it on loopback unless you mean it.")
@click.option("--port", type=int, default=8765, show_default=True)
@browser_options
def ui(openrouter_key, model, host, port, proxy, seed, headed, binary, profile_dir):
    """Serve the two-pane interface: conversation left, live browser right.

    The key is optional HERE and required for `do`, and the asymmetry is
    deliberate. Without a key this runs the literal-command placeholder, which is
    how the whole surface can be exercised - and its defects found - with no
    model, no key and nothing spent. With a key it is the product.
    """
    from .brain import LiteralBrain, OpenRouterBrain
    from .link import Link
    from .llm import make_client
    from .web import ChatService, build_app

    key = openrouter_key or os.environ.get("OPENROUTER_API_KEY")
    if key:
        mdl = resolve_model(model, os.environ)
        brain = OpenRouterBrain(make_client(key), mdl)
        label = mdl
        click.echo("model    %s via %s" % (mdl, BASE_URL))
    else:
        brain = LiteralBrain()
        label = "placeholder (no key)"
        click.echo("model    none: literal commands only. Pass --openrouter-key "
                   "for a real one.")

    opts = {"proxy": proxy, "seed": seed, "headed": headed,
            "binary": binary, "profile_dir": profile_dir}

    async def serve() -> None:
        import uvicorn

        link = await Link(opts).open()
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
