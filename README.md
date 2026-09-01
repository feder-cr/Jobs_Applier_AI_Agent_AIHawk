<div align="center">

# AIHawk

**Two halves of the same idea: an LLM that writes your application, and a browser that reaches the end of a task you drive it through.**

The first half runs from this repository today. The second ships as installable packages you attach to your AI client.

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

## Where this stands

AIHawk went viral in 2024 as a bot that applied to jobs for you. That is the
version the press above wrote about, and the mass-application engine is no longer
in this repository.

It was removed for a reason worth stating plainly. Firing applications at a job
board is the easy half and the worthless half. It stops working the moment the
site decides you are a machine, and it produces the kind of volume that made
recruiters hate the whole category. The half that was actually hard, and that
survived, is a browser that reaches the end of a task without being stopped.

So AIHawk is two things now, and this README is careful about which is which:

**In this repository, runnable today:** the document half. An LLM reads your
profile and a job posting and writes a resume or a cover letter for that specific
posting. It is a local command line tool, it works, and CI checks it on every
push.

**As separate installable packages:** the browser half. A Firefox patched at the
source, exposed to any AI client over MCP. You install it with one command and
never clone anything.

What joins them into one automated pipeline does not exist yet. That part is
honest roadmap, described at the bottom, not shipped code.

## The document half, in this repository

Generate a resume, a resume rewritten for a specific job posting, or a cover
letter for a specific job posting.

```mermaid
flowchart LR
  PR["Your profile<br/>plain_text_resume.yaml"] --> G["main.py<br/><i>LLM + HTML/CSS templates</i>"]
  JD["A job posting URL<br/><i>opened and scraped in Chrome</i>"] --> G
  G --> CV["PDF in data_folder/output/"]
```

Python 3.12, and Chrome installed. It opens the job posting you point it at,
and it renders the finished HTML to PDF.

```bash
git clone https://github.com/feder-cr/Jobs_Applier_AI_Agent_AIHawk.git
cd Jobs_Applier_AI_Agent_AIHawk
pip install -r requirements.txt
```

```bash
python main.py
```

The first run creates `data_folder/` for you, copied from the worked example, and
stops to say so. Open the three files it made and put your own details in:
`plain_text_resume.yaml` is your experience and skills, `work_preferences.yaml`
is what you are looking for, and `secrets.yaml` takes your OpenAI API key. Those
files are not in git, so what you write there stays yours.

Run it again and it asks which of the three documents you want, then writes the
PDF into `data_folder/output/`.

It calls OpenAI, on `gpt-4o-mini`. Other providers used to be wired up through
LangChain and are not any more: the code that offered the choice was removed with
the mass-application engine, so an Anthropic or Ollama key in `secrets.yaml` gets
handed to an OpenAI client and fails. Put an OpenAI key there, and keep it out of
your commits. There is a test in here that fails the build if a key ever lands in
that file again, because one did.

## The browser half, as packages

This is the part that installs rather than clones, and none of it lives in this
repository.

MCP is the protocol AI clients use to attach external tools. If you use
[Claude Code](https://claude.com/claude-code), Claude Desktop, Cursor or
anything similar, you already have a client. You need
[uv](https://docs.astral.sh/uv/) for the `uvx` command, Python 3.11 or newer, and
Windows or Linux.

```bash
claude mcp add stealth --env STEALTHFOX_PROXY=http://user:pass@host:port -- uvx invisible-playwright-mcp
```

Without a proxy, drop the `--env` flag. For any other client, the same thing as a
config entry:

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

Use an absolute path for the profile directory. Most clients pass env values
through verbatim, so a leading `~` becomes a folder literally named `~`.

### Check it worked

Restart the client and list your MCP servers. `stealth` should be there with
thirteen tools attached. Then type one small thing before you type a big one:

> Use the stealth browser to open a browser fingerprint check page, take a
> screenshot, and tell me the timezone, locale, languages and public IP it
> reports.

Read those four values against what your own browser reports on the same page. On
a proxied run they should describe the exit country and agree with each other,
not with the machine you are sitting at. That is the whole thesis, checkable in
one prompt, before you trust it with anything that matters.

The first launch downloads the patched Firefox build, a few hundred megabytes, so
it takes a minute and looks like a hang. It is cached afterwards. If the server
does not appear at all, `uvx` is not on the PATH the client sees, which is not
always the PATH your shell sees.

### Two things to ask it

The server drives the browser and only the browser: no disk access, on purpose.
Reading a file or writing a CSV is your client's own file tools.

> Go to this careers page: `<paste the URL>`. Filter to backend roles in Europe
> posted in the last two weeks. For each result, open the posting and pull out the
> title, the location, whether it says remote or hybrid, and anything it says
> about visa sponsorship. Give me the list as a table, and append a row to
> shortlist.csv for each one: company, role, URL, date.

> Go to this flight search site: `<paste the URL>`. One way, Milan to Lisbon,
> economy, one checked bag, one adult. Check every date from the 12th to the 16th
> of next month, one at a time, and read the cheapest fare for each day. The date
> field is a calendar widget, so click the days rather than typing them. If a date
> has no availability say so, do not guess a number. Write the five to flights.md
> sorted by price, and leave the cheapest open in a tab so I can book it myself.

Those two share nothing except the machinery: same server, same browser, same
thirteen tools, nothing reconfigured in between.

## Why fewer challenges appear

An anti-bot rarely catches you on one exotic value. It catches you on a
contradiction. Put a proxy in front of an ordinary browser and you have built one:
the address says one country, the clock and the language say another.

```mermaid
flowchart LR
  A["Proxy says: United States"] --> D{"Anti-bot compares"}
  B["Browser says: Italy"] --> D
  D --> E["Contradiction<br/>→ challenge"]
```

The engine turns that around. Before the browser starts, the exit IP is resolved
through the proxy, and everything the browser will declare is derived from that
exit rather than from the machine the process happens to be running on. Values an
IP cannot imply, like screen metrics and GPU strings, come from
`STEALTHFOX_SEED` and stay put.

```mermaid
flowchart LR
  P["Proxy exit IP"] --> C["invisible_core derives<br/>timezone · locale · languages<br/>geolocation · fonts · WebRTC"]
  C --> B["The browser declares all of it"]
  P --> D{"Anti-bot compares"}
  B --> D
  D --> E["Everything agrees<br/>→ nothing to raise a challenge about"]
```

There is nothing incoherent in that declared layer to find, because it all comes
from one source. That is one input into a risk score among several, and it is the
input this project can do something about. The practical consequence: many of the
interstitials and hard blocks people expect from browser automation never appear,
because nothing raised them.

**There is no captcha solver in this project.** No third party service wired up,
no pass rate to promise. Cloudflare, Turnstile, DataDome, Kasada, Akamai,
reCAPTCHA and hCaptcha all exist and all still work. What changes is how often
you meet one. When an interactive challenge does appear, `browser_click_at` gives
your client a real pointer: viewport coordinates, a pointer that moves rather than
teleports, press and hold, and a screenshot of what happened. That covers sliders
and press-and-hold widgets. It will not identify motorbikes for you, and sometimes
the honest answer to a challenge is to stop.

### Configuration

| Variable | What it does |
|---|---|
| `STEALTHFOX_PROXY` | `http://user:pass@host:port`, or `socks5://`. Timezone, locale, languages, geolocation and egress all derive from it. |
| `STEALTHFOX_SEED` | An integer. Fixes the seeded half of the identity: fonts, screen, GPU strings. Same seed, same values, every run. |
| `STEALTHFOX_PROFILE_DIR` | Absolute path. Persistent profile, so logins and cookies survive restarts. |
| `STEALTHFOX_HEADLESS` | Headless by default. Set `0` to watch it work, worth doing the first few times. |
| `STEALTHFOX_BINARY` | A build of your own. Only for people building the engine themselves, and it needs a matching seal file or the launch is refused on purpose. |

Set a seed for anything you run more than once. An identity that changes shape
between sessions is its own kind of signal.

### The thirteen tools

**Pages:** `session_new_page`, `session_list_pages`, `session_select_page`,
`session_close_page`.
**Reading:** `browser_navigate`, `browser_read_text`, `browser_snapshot`,
`browser_take_screenshot`.
**Acting:** `browser_click`, `browser_click_at`, `browser_type`,
`browser_press_key`, `browser_evaluate`.

You do not call these, the model does. Two are worth explaining.
`browser_snapshot` returns the visible interactive elements rather than the
accessibility tree, because one country dropdown contributes roughly two hundred
option nodes to a full tree and buries the form the model was looking for.
`browser_evaluate` runs arbitrary JavaScript and is the escape hatch, worth being
careful with, since a model that reaches for it too early writes a scraper where
reading the page would have done.

## What is not built yet

Said plainly, because the gap between the two halves above is the whole roadmap
and it would be easy to imply it is already closed.

Filling an application form end to end needs a layer that does not exist in any
of these repositories: reading a page into a list of questions each carrying the
address of the element that answers it, and a set of per-platform adapters for
the handful of applicant tracking systems that behave differently from ordinary
HTML. Until that exists, the generated PDF is something you upload yourself, and
the browser is something you drive through prompts.

Nothing here pretends otherwise, and there is no timeline attached.

## The pieces

- [invisible_playwright](https://github.com/feder-cr/invisible_playwright) - the
  Python wrapper and the patched Firefox it pins and drives. If you would rather
  script than prompt, use this directly: the API is Playwright's.
- [invisible-playwright-mcp](https://github.com/feder-cr/invisible-playwright-mcp) -
  the MCP server installed above.
- [invisible_core](https://github.com/feder-cr/invisible_core) - seed to
  fingerprint to preferences, proxy and geolocation derivation. The part that
  decides what the browser declares.
- [lib_resume_builder_AIHawk](https://github.com/feder-cr/lib_resume_builder_AIHawk) -
  the resume rendering library this repository depends on.

Issues and pull requests are welcome on whichever of those the problem lives in.
If you are not sure, open it here. When something fails on a specific site,
describe the shape of it: which step, what the page did, what the tool returned,
which exit country. "It got blocked" is not something anyone can act on, and a
list of targets in the issue tracker helps nobody.

The 2024 command line applier is still in the git history if you forked it and
want to compare. It is not maintained and it will not work against anything
current. Third-party provider plugins are not in this repository: the core is
open source, the plugins were removed for copyright reasons.

## A note on use

This automates a browser under your control. Read the terms of the sites you
point it at, respect their rate limits, and do not use it to submit things a
human has not read.

## License

See [LICENSE](LICENSE).
