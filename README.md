<div align="center">

# AIHawk

**Born as an AI web agent that applied to jobs in bulk. Becoming a general one: an agent you point at the web and tell what to do.**

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

## I want documents

You need **Python 3.12** and **Chrome** installed.

```bash
git clone https://github.com/feder-cr/Jobs_Applier_AI_Agent_AIHawk.git
cd Jobs_Applier_AI_Agent_AIHawk
pip install -r requirements.txt
```

```bash
python main.py
```

That first run creates `data_folder/` from `data_folder_example/`, tells you which files to edit, and stops. Edit these three:

| File | Put in it |
|---|---|
| `data_folder/plain_text_resume.yaml` | Your experience and skills |
| `data_folder/work_preferences.yaml` | What you are looking for |
| `data_folder/secrets.yaml` | Your OpenAI API key |

They are git-ignored, so what you write there stays yours.

Run it again and pick one:

- **Generate Resume**
- **Generate Resume Tailored for Job Description**
- **Generate Tailored Cover Letter for Job Description**

The two tailored options ask for a job posting URL and open it in Chrome. The finished PDF lands in `data_folder/output/`.

**Use an OpenAI key.** This calls `gpt-4o-mini`, and no other provider works: an Anthropic or Ollama key in `secrets.yaml` gets handed to an OpenAI client and fails.

## I want a browser my AI drives

It installs as a package, `invisible-playwright-mcp` on PyPI. None of it is in this repository, so there is nothing to clone here.

You need **Python 3.11 or newer**, **Windows or Linux**, and [uv](https://docs.astral.sh/uv/), which provides the `uvx` command:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh              # macOS, Linux
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"   # Windows
```

If you use [Claude Code](https://claude.com/claude-code), Claude Desktop, Cursor or anything similar, you already have the client half.

```bash
claude mcp add stealth --env STEALTHFOX_PROXY=http://user:pass@host:port -- uvx invisible-playwright-mcp
```

Drop the `--env` flag if you are not using a proxy. In any other client, the same thing as a config entry:

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

Restart the client and list your MCP servers. `stealth` should be there with thirteen tools:

**Pages:** `session_new_page`, `session_list_pages`, `session_select_page`, `session_close_page`
**Reading:** `browser_navigate`, `browser_read_text`, `browser_snapshot`, `browser_take_screenshot`
**Acting:** `browser_click`, `browser_click_at`, `browser_type`, `browser_press_key`, `browser_evaluate`

You never call those yourself, the model does. Ask it for one small thing first, like opening a page and taking a screenshot.

**The first launch downloads a few hundred megabytes** and looks like a hang. It is cached after that. If the server never appears at all, `uvx` is not on the PATH your client sees, which is not always the PATH your shell sees.

### Two things to ask it

The server drives the browser and nothing else: it has no disk access. Reading and writing files is your client's own tooling.

> Go to `<paste the URL>`. Filter to backend roles in Europe posted in the last two weeks. For each result, open the posting and pull out the title, the location, whether it says remote or hybrid, and anything about visa sponsorship. Give me the list as a table, and append a row to shortlist.csv for each one.

> Go to `<paste the URL>`. One way, Milan to Lisbon, economy, one checked bag, one adult. Check every date from the 12th to the 16th of next month, one at a time, and read the cheapest fare for each day. The date field is a calendar widget, so click the days rather than typing them. If a date has no availability say so, do not guess a number. Write the five to flights.md sorted by price, and leave the cheapest open in a tab.

### Settings

| Variable | What it does |
|---|---|
| `STEALTHFOX_PROXY` | `http://user:pass@host:port`, or `socks5://`. Credentials go in the URL. |
| `STEALTHFOX_SEED` | An integer. Same seed, same browser identity, every run. Set one for anything you run more than once. |
| `STEALTHFOX_PROFILE_DIR` | Absolute path. Persistent profile, so logins and cookies survive restarts. Most clients pass env values through verbatim, so a leading `~` becomes a folder literally named `~`. |
| `STEALTHFOX_HEADLESS` | Headless by default. Set `0` to watch the window, worth doing the first few times. |

## Limits

**There is no captcha solver here.** None is built in and none is wired to a third party service.

**Nothing joins the two halves yet.** No code in any of these repositories fills in an application form and submits it end to end. The generated PDF is something you upload yourself, and the browser is something you drive through prompts. There is no timeline attached to that.

## The other repositories

- [invisible_playwright](https://github.com/feder-cr/invisible_playwright) - the Python wrapper and the browser it pins and drives. Use this directly if you would rather script than prompt: the API is Playwright's.
- [invisible-playwright-mcp](https://github.com/feder-cr/invisible-playwright-mcp) - the MCP server installed above.
- [invisible_core](https://github.com/feder-cr/invisible_core) - seed to fingerprint to preferences, proxy and geolocation derivation.
- [lib_resume_builder_AIHawk](https://github.com/feder-cr/lib_resume_builder_AIHawk) - the resume rendering library this repository depends on.

Issues and pull requests are welcome on whichever of those the problem lives in. If you are not sure, open it here. When something fails on a page, say which step, what the page did, what the tool returned and which exit country you were on. "It got blocked" is not something anyone can act on.

## Using it

This automates a browser under your control. Read the terms of the sites you point it at, respect their rate limits, and do not submit anything a human has not read.

## License

See [LICENSE](LICENSE).