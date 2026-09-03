<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/feder-cr/AIHawk/main/assets/aihawk-logo-dark.png">
  <img alt="AIHawk" src="https://raw.githubusercontent.com/feder-cr/AIHawk/main/assets/aihawk-logo-light.png" width="380">
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

## First, one prerequisite for both ways

**Python 3.11 or newer**, on **Windows (x86_64) or Linux (x86_64, arm64)** - macOS
is not supported, the last engine build for it was `firefox-20`. Then
[uv](https://docs.astral.sh/uv/), because both commands below start with `uvx`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh              # Linux
```
```powershell
irm https://astral.sh/uv/install.ps1 | iex                   # Windows
```

## Now pick one

**Do you already use an AI assistant that can run tools - Claude Code, Claude
Desktop, Cursor?** If yes, it brings the model and you add this browser to it. If
no, or if you would rather watch the work happen, run our interface instead.

<table>
<tr>
<th width="50%">1. Add it to the assistant you have</th>
<th width="50%">2. Run our interface</th>
</tr>
<tr>
<td valign="top">

Your assistant brings the model. Nothing to pay us, nothing to sign up for.

**Claude Code**, once for every project:

```bash
claude mcp add -s user stealth -- uvx invisible-playwright-mcp
```

**Claude Desktop, Cursor, and the rest** take a config file instead. The block to
paste, and which file it goes in, are in the
[server's README](https://github.com/feder-cr/invisible-playwright-mcp).

Then talk to your assistant as usual:

> Go to news.ycombinator.com and give me the top five titles.

</td>
<td valign="top">

We bring the interface, you bring an [OpenRouter](https://openrouter.ai) account
and its key. Chat on the left, the live browser on the right.

```bash
uvx aihawk ui --openrouter-key sk-or-...
```

Open **http://127.0.0.1:8765** and type the same thing.

Curious first? `uvx aihawk ui` runs with no key at all on a placeholder that
takes literal commands, which is enough to see the interface work and to tell a
browser problem from a model problem before spending anything.

</td>
</tr>
</table>

Same patched Firefox behind both. AIHawk reaches it through that MCP server, over
MCP, exactly as your assistant would - so anything the interface can do, your
assistant can do too.

## The download nobody warns you about

The browser is about a quarter of a gigabyte and it is **not** fetched when you
install either side. It arrives on the **first request that needs a page**, which
means your first instruction sits there doing nothing for a while, and on a slow
connection the assistant may report a timeout that says nothing about a download.

Get it over with first, in a terminal where you can watch it:

```bash
uvx invisible-playwright fetch
```

Cached afterwards, and shared by both ways in. Per-platform sizes are in the
[engine's README](https://github.com/feder-cr/invisible_playwright).

## Without a page, for scripts and cron

Same machinery, no interface, the answer on stdout.

```bash
uvx aihawk do "Go to example.com and tell me the top headline" --openrouter-key sk-or-...
```

The keyless placeholder from column 2 takes exactly these: `go <url>`,
`read [selector]`, `click <selector>`, `type <selector> <text>`, `tab` (opens a new
browser tab), `shot`.

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

`ui` and `do` share all of these except the last row, which is `ui` only.

| Option | What it does |
|---|---|
| `--openrouter-key` | Your key, or the `OPENROUTER_API_KEY` variable. Required for `do`, optional for `ui`. |
| `--model` | An OpenRouter model id, or `AIHAWK_MODEL`. Defaults to `z-ai/glm-4.6`. |
| `--proxy` | Optional. `http://user:pass@proxy.example.com:8080`, or `socks5://proxy.example.com:1080`. Host and port are both required; a bare scheme is rejected. With one set, the timezone, locale and egress follow it. |
| `--binary` | Path to an engine binary you already have. It must be the exact build the packaged seal pins, or startup refuses: this skips the download, not the version check. |
| `--seed` | An integer. Same seed, same browser identity, every run. Set one for anything you run twice. |
| `--profile-dir` | A directory to keep the profile in, so logins and cookies survive restarts. A relative path works and resolves from where you ran the command, which is rarely what you want. |
| `--headed` | Show the browser window. The interface shows you the page anyway. |
| `--host`, `--port` | `ui` only. `127.0.0.1` and `8765`. Changing the host exposes the interface, and it has no authentication, so anyone who can reach the port can drive your browser. |

Passing `--openrouter-key` puts the key in your shell history, and on Linux in the
process list for every user on the machine. `OPENROUTER_API_KEY` in the environment
avoids both.

Either way it does not reach the browser process. It is removed from the environment the
engine starts with, by name and by value, so a copy kept under a second name -
`OPENAI_API_KEY` is the usual one - goes too. [`tests/test_key_isolation.py`](https://github.com/feder-cr/AIHawk/blob/main/tests/test_key_isolation.py)
fails if that stops being true.

## The rest of the family

| Project | What it is |
|---|---|
| [invisible-playwright-mcp](https://github.com/feder-cr/invisible-playwright-mcp) | The MCP server from column 1. Tools only, no interface. |
| [invisible_playwright](https://github.com/feder-cr/invisible_playwright) | The engine, as a Python library. Use it if you would rather write code than prompts: the API is Playwright's. |
| [invisible_core](https://github.com/feder-cr/invisible_core) | Seed to fingerprint to preferences, proxy and geolocation. |

## Contributing

Issues and pull requests welcome on whichever of those the problem lives in. If you
are not sure, open it here. See [CONTRIBUTING](https://github.com/feder-cr/AIHawk/blob/main/.github/CONTRIBUTING.md).

When something fails on a page, say which step, what the page did, what the tool
returned and which exit country you were on. "It got blocked" is not something
anyone can act on.


## Using it responsibly

This automates a browser under your control. Read the terms of the sites you point
it at, respect their rate limits, and do not submit anything a human has not read.

## License

[MIT](https://github.com/feder-cr/AIHawk/blob/main/LICENSE). Everything distributed before 2 September 2026 was released under
AGPL-3.0 and stays under it.
