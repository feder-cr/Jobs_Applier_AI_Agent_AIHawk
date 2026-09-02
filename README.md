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

AIHawk gives your AI client a real browser and lets you drive it in plain
language. Open pages, read them, click, type, come back with the answer.

It installs as a package, `invisible-playwright-mcp`, and connects over MCP, the
protocol AI clients use to attach external tools. Your client gets fourteen
tools; you never call them yourself.

## Requirements

**Python 3.11 or newer**, **Windows or Linux**, and
[uv](https://docs.astral.sh/uv/), which provides the `uvx` command.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh              # macOS, Linux
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"   # Windows
```

If you use [Claude Code](https://claude.com/claude-code), Claude Desktop, Cursor
or anything similar, you already have the client half.

## Installation

```bash
claude mcp add stealth --env STEALTHFOX_PROXY=http://user:pass@host:port -- uvx invisible-playwright-mcp
```

Drop the `--env` flag if you are not using a proxy. In any other client, the same
thing as a config entry:

```json
{
  "mcpServers": {
    "stealth": {
      "command": "uvx",
      "args": ["invisible-playwright-mcp"],
      "env": {
        "STEALTHFOX_PROXY": "http://user:pass@host:port",
        "STEALTHFOX_SEED": "12345",
        "STEALTHFOX_PROFILE_DIR": "/absolute/path/to/profile"
      }
    }
  }
}
```

## Usage

Restart the client and list your MCP servers. `stealth` should be there with
fourteen tools attached. Ask for one small thing first, like opening a page and
taking a screenshot.

The first launch downloads the browser, about 700 MB, and looks like a hang. It is
cached after that. If the server never appears at all, `uvx` is not on the PATH
your client sees, which is not always the PATH your shell sees.

The server drives the browser and nothing else: it has no disk access. Reading
and writing files is your client's own tooling.

Two things worth asking it:

> Go to `<paste the URL>`. Filter to backend roles in Europe posted in the last
> two weeks. For each result, open the posting and pull out the title, the
> location, whether it says remote or hybrid, and anything about visa
> sponsorship. Give me the list as a table, and append a row to shortlist.csv for
> each one.

> Go to `<paste the URL>`. One way, Milan to Lisbon, economy, one checked bag,
> one adult. Check every date from the 12th to the 16th of next month, one at a
> time, and read the cheapest fare for each day. The date field is a calendar
> widget, so click the days rather than typing them. If a date has no
> availability say so, do not guess a number. Write the five to flights.md sorted
> by price, and leave the cheapest open in a tab.

Those two share nothing but the machinery.

## Configuration

Environment variables on the MCP server entry.

| Variable | What it does |
|---|---|
| `STEALTHFOX_PROXY` | `http://user:pass@host:port`, or `socks5://`. Credentials go in the URL. |
| `STEALTHFOX_SEED` | An integer. Same seed, same browser identity, every run. Set one for anything you run more than once. |
| `STEALTHFOX_PROFILE_DIR` | Absolute path. Persistent profile, so logins and cookies survive restarts. Most clients pass env values through verbatim, so a leading `~` becomes a folder literally named `~`. |
| `STEALTHFOX_HEADLESS` | Headless by default. Set `0` to watch the window, worth doing the first few times. |

## Available tools

You never call these yourself. Your model does, from what you ask it.

| Group | Tools |
|---|---|
| Pages | `session_new_page`, `session_list_pages`, `session_select_page`, `session_close_page` |
| Reading | `browser_navigate`, `browser_read_text`, `browser_snapshot`, `browser_read_html`, `browser_take_screenshot` |
| Acting | `browser_click`, `browser_click_at`, `browser_type`, `browser_press_key`, `browser_evaluate` |

## Related projects

| Project | What it is |
|---|---|
| [invisible-playwright-mcp](https://github.com/feder-cr/invisible-playwright-mcp) | The MCP server installed above. |
| [invisible_playwright](https://github.com/feder-cr/invisible_playwright) | The Python wrapper and the browser it pins and drives. Use it directly if you would rather script than prompt: the API is Playwright's. |
| [invisible_core](https://github.com/feder-cr/invisible_core) | Seed to fingerprint to preferences, proxy and geolocation derivation. |

## Contributing

Issues and pull requests are welcome on whichever of those the problem lives in.
If you are not sure, open it here.

When something fails on a page, say which step, what the page did, what the tool
returned and which exit country you were on. "It got blocked" is not something
anyone can act on.

This automates a browser under your control. Read the terms of the sites you
point it at, respect their rate limits, and do not submit anything a human has
not read.

## License

[AGPL-3.0](LICENSE).
