<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/aihawk-logo-dark.png">
  <img alt="AIHawk" src="assets/aihawk-logo-light.png" width="380">
</picture>

**An AI agent with a real browser. You say what you want in plain language, it goes and does it on the actual web.**

<sub>FEATURED IN</sub><br>
[**Business Insider**](https://www.businessinsider.com/aihawk-applies-jobs-for-you-linkedin-risks-inaccuracies-mistakes-2024-11) ·
[**TechCrunch**](https://techcrunch.com/2024/10/10/a-reporter-used-ai-to-apply-to-2843-jobs/) ·
[**Semafor**](https://www.semafor.com/article/09/12/2024/linkedins-have-nots-and-have-bots) ·
[**Wired**](https://www.wired.it/article/aihawk-come-automatizzare-ricerca-lavoro/) ·
[**The Verge**](https://www.theverge.com/2024/10/10/24266898/ai-is-enabling-job-seekers-to-think-like-spammers) ·
[**Vanity Fair**](https://www.vanityfair.it/article/intelligenza-artificiale-candidature-di-lavoro) ·
[**404 Media**](https://www.404media.co/i-applied-to-2-843-roles-the-rise-of-ai-powered-job-application-bots/)

</div>

---

# Pick one

There are two ways to use this, and the only real question is **where the model comes from**.

<table>
<tr>
<th width="50%">1. Your AI client already has a model</th>
<th width="50%">2. You want an interface, model included</th>
</tr>
<tr>
<td valign="top">

Claude Code, Claude Desktop, Cursor, or anything else that speaks MCP.
The browser shows up as tools it can use.

```bash
claude mcp add stealth -- uvx invisible-playwright-mcp
```

Then just talk to your client:

> Go to news.ycombinator.com and give me the top five titles.

</td>
<td valign="top">

No client needed. Bring an [OpenRouter](https://openrouter.ai) key, get a page
with the chat on the left and the live browser on the right.

```bash
uvx aihawk ui --openrouter-key sk-or-...
```

Then open **http://127.0.0.1:8765** and type the same thing.

</td>
</tr>
</table>

Same patched Firefox either way, and the second one is a client of the first: AIHawk
talks to that MCP server over MCP, with no private path to the browser.

**Not sure?** If you already pay for Claude or Cursor, take column 1 - you are
already paying for the model. Otherwise take column 2.

## Before you start

**Python 3.11 or newer**, on **Windows (x86_64) or Linux (x86_64, arm64)**.
macOS is not supported: no Mac engine has been published since firefox-21. Plus
[uv](https://docs.astral.sh/uv/), which is what gives you `uvx`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh              # Linux
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"   # Windows
```

The first run downloads the browser, about 700 MB. It looks like a hang and it is
cached afterwards.

That is the whole setup. No proxy, no account, no config file.

## Without a page, for scripts and cron

Same machinery, no interface, the answer on stdout.

```bash
uvx aihawk do "Go to example.com and tell me the top headline" --openrouter-key sk-or-...
```

## Without a key

`uvx aihawk ui` starts without one. What answers is a placeholder that understands
six literal commands - `go <url>`, `read [selector]`, `click <selector>`,
`type <selector> <text>`, `tab`, `shot` - which is enough to see the interface work and to
tell a browser problem from a model problem before spending anything.

## What it is good at

Anything that needs a browser rather than an API, and needs a person's judgement
about what is on the page.

> Go to `<paste the URL>`. One way, Milan to Lisbon, economy, one checked bag, one
> adult. Check every date from the 12th to the 16th of next month, one at a time,
> and read the cheapest fare for each day. The date field is a calendar widget, so
> click the days rather than typing them. If a date has no availability, say so.
> Do not guess a number.

It drives the page the way a person would: the pointer moves, keys are pressed, and
it will refuse to set a form field from JavaScript even when that would be quicker,
because a page can tell the difference.

## Options

Both `ui` and `do` take the same ones.

| Option | What it does |
|---|---|
| `--openrouter-key` | Your key, or the `OPENROUTER_API_KEY` variable. Required for `do`, optional for `ui`. |
| `--model` | An OpenRouter model id, or `AIHAWK_MODEL`. Defaults to `z-ai/glm-4.6`. |
| `--proxy` | `http://user:pass@proxy.example.com:8080`, or `socks5://`. Optional. With one set, the timezone, locale and egress follow it. |
| `--binary` | Path to an engine binary you already have, instead of the downloaded one. |
| `--seed` | An integer. Same seed, same browser identity, every run. Set one for anything you run twice. |
| `--profile-dir` | Absolute path. Logins and cookies survive restarts. |
| `--headed` | Show the browser window. The interface shows you the page anyway. |
| `--host`, `--port` | `ui` only. Loopback and 8765 by default. Leave the host alone unless you mean it. |

The key does not reach the browser process. It is removed from the environment the
engine starts with, by name and by value, so a copy kept under a second name -
`OPENAI_API_KEY` is the usual one - goes too. `tests/test_key_isolation.py` fails
if that stops being true.

## The rest of the family

| Project | What it is |
|---|---|
| [invisible-playwright-mcp](https://github.com/feder-cr/invisible-playwright-mcp) | The MCP server from column 1. Tools only, no interface. |
| [invisible_playwright](https://github.com/feder-cr/invisible_playwright) | The engine, as a Python library. Use it if you would rather write code than prompts: the API is Playwright's. |
| [invisible_core](https://github.com/feder-cr/invisible_core) | Seed to fingerprint to preferences, proxy and geolocation. |

## Contributing

Issues and pull requests welcome on whichever of those the problem lives in. If you
are not sure, open it here. See [CONTRIBUTING](.github/CONTRIBUTING.md).

When something fails on a page, say which step, what the page did, what the tool
returned and which exit country you were on. "It got blocked" is not something
anyone can act on.


## Using it responsibly

This automates a browser under your control. Read the terms of the sites you point
it at, respect their rate limits, and do not submit anything a human has not read.

## License

[MIT](LICENSE). Everything distributed before 2 September 2026 was released under
AGPL-3.0 and stays under it.
