<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/aihawk-logo-dark.png">
  <img alt="AIHawk" src="assets/aihawk-logo-light.png" width="380">
</picture>

**Born as an AI web agent that applied to jobs in bulk. Becoming a general one: an agent you point at the web and tell what to do.**

<sub>FEATURED IN</sub><br>
[**Business Insider**](https://www.businessinsider.com/aihawk-applies-jobs-for-you-linkedin-risks-inaccuracies-mistakes-2024-11) ·
[**TechCrunch**](https://techcrunch.com/2024/10/10/a-reporter-used-ai-to-apply-to-2843-jobs/) ·
[**Semafor**](https://www.semafor.com/article/09/12/2024/linkedins-have-nots-and-have-bots) ·
[**Dev.by**](https://devby.io/news/ya-razoslal-rezume-na-2843-vakansii-po-17-v-chas-kak-ii-boty-vytesnyaut-ludei-iz-protsessa-naima.amp) ·
[**Wired**](https://www.wired.it/article/aihawk-come-automatizzare-ricerca-lavoro/) ·
[**The Verge**](https://www.theverge.com/2024/10/10/24266898/ai-is-enabling-job-seekers-to-think-like-spammers) ·
[**Vanity Fair**](https://www.vanityfair.it/article/intelligenza-artificiale-candidature-di-lavoro) ·
[**404 Media**](https://www.404media.co/i-applied-to-2-843-roles-the-rise-of-ai-powered-job-application-bots/)

</div>

---

## Overview

AIHawk gives a model a real browser and a page to work in. You type what you
want in plain language, and you watch it happen: the conversation on the left,
the browser on the right, live.

One command, and the only thing it needs from you is an
[OpenRouter](https://openrouter.ai) key. No client to install, no configuration
to paste into another program, nothing else to run.

```bash
uvx aihawk ui --openrouter-key sk-or-...
```

Then open `http://127.0.0.1:8765`.

The browser is a patched Firefox that looks like an ordinary one, and it is the
same engine whether you drive it from here, from a script, or from your own
agent.

## Requirements

**Python 3.11 or newer**, **Windows or Linux**, and
[uv](https://docs.astral.sh/uv/), which provides the `uvx` command.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh              # macOS, Linux
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"   # Windows
```

The first launch downloads the browser, about 700 MB, and looks like a hang. It
is cached after that.

## Two ways to run it

**The interface.** Everything happens on one page and you can see it.

```bash
uvx aihawk ui --openrouter-key sk-or-... --proxy http://user:pass@host:port
```

**One shot.** Same machinery, no page, an answer on stdout. For scripts and cron.

```bash
uvx aihawk do "Open <url> and tell me the price of the first result" \
  --openrouter-key sk-or-...
```

Without a key, `aihawk ui` still starts. What answers is a placeholder that
understands five literal commands - `go <url>`, `read [selector]`,
`click <selector>`, `type <selector> <text>`, `shot` - which is enough to see
the interface work, and to tell a browser problem from a model problem without
spending anything.

## What to ask it

> Go to `<paste the URL>`. Filter to backend roles in Europe posted in the last
> two weeks. For each result, open the posting and pull out the title, the
> location, whether it says remote or hybrid, and anything about visa
> sponsorship. Give me the list as a table.

> Go to `<paste the URL>`. One way, Milan to Lisbon, economy, one checked bag,
> one adult. Check every date from the 12th to the 16th of next month, one at a
> time, and read the cheapest fare for each day. The date field is a calendar
> widget, so click the days rather than typing them. If a date has no
> availability say so, do not guess a number.

Those two share nothing but the machinery.

## Options

Both commands take the same browser options.

| Option | What it does |
|---|---|
| `--openrouter-key` | Your key, or the `OPENROUTER_API_KEY` environment variable. Required for `do`, optional for `ui`. |
| `--model` | An OpenRouter model id, or `AIHAWK_MODEL`. Defaults to a current one. |
| `--proxy` | `http://user:pass@host:port`, or `socks5://`. Credentials go in the URL. |
| `--seed` | An integer. Same seed, same browser identity, every run. Set one for anything you run more than once. |
| `--profile-dir` | Absolute path. Persistent profile, so logins and cookies survive restarts. |
| `--headed` | Show the browser window. The interface shows you the page anyway. |
| `--host`, `--port` | `ui` only. Loopback and 8765 by default. Leave the host alone unless you mean it. |

The key never reaches the browser process: it is stripped from the environment
the engine is started with, and there is a test that fails if that stops being
true.

## Already have an MCP client?

Then you may not need this at all. The browser is exposed as an MCP server, and
Claude Code, Claude Desktop, Cursor and anything similar can drive it directly:

```bash
claude mcp add stealth --env STEALTHFOX_PROXY=http://user:pass@host:port -- uvx invisible-playwright-mcp
```

Your client brings the model, and gets the same fourteen tools this interface
uses. Nothing here has a private path to the browser - AIHawk is a client of
that server like any other, which is the reason to trust that the tools are
enough.

## The tools

You never call these yourself. The model does, from what you ask it.

| Group | Tools |
|---|---|
| Pages | `session_new_page`, `session_list_pages`, `session_select_page`, `session_close_page` |
| Reading | `browser_navigate`, `browser_read_text`, `browser_snapshot`, `browser_read_html`, `browser_take_screenshot` |
| Acting | `browser_click`, `browser_click_at`, `browser_type`, `browser_press_key`, `browser_evaluate` |

## Related projects

| Project | What it is |
|---|---|
| [invisible-playwright-mcp](https://github.com/feder-cr/invisible-playwright-mcp) | The MCP server this drives. Tools only, no interface. |
| [invisible_playwright](https://github.com/feder-cr/invisible_playwright) | The Python wrapper and the browser it pins and drives. Use it directly if you would rather script than prompt: the API is Playwright's. |
| [invisible_core](https://github.com/feder-cr/invisible_core) | Seed to fingerprint to preferences, proxy and geolocation derivation. |

## Contributing

Issues and pull requests are welcome on whichever of those the problem lives in.
If you are not sure, open it here. See [CONTRIBUTING](.github/CONTRIBUTING.md).

When something fails on a page, say which step, what the page did, what the tool
returned and which exit country you were on. "It got blocked" is not something
anyone can act on.

This automates a browser under your control. Read the terms of the sites you
point it at, respect their rate limits, and do not submit anything a human has
not read.

## License

[MIT](LICENSE). Everything distributed before 2 September 2026 was
released under AGPL-3.0 and stays under it.
