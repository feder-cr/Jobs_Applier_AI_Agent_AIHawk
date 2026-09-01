<p align="center"><sub><b>SPONSOR</b></sub></p>

<p align="center">
  <a href="https://github.com/feder-cr/invisible_playwright"><img src="https://raw.githubusercontent.com/feder-cr/Jobs_Applier_AI_Agent_AIHawk/main/assets/invisible-playwright-banner.png" alt="invisible_playwright - the best undetectable browser" width="880"></a>
</p>

---

<div align="center">

# AIHawk

**Tell an AI what to do on the web. It opens a real Firefox, reads the page, fills the form, clicks the button, and brings back what you asked for.**

One command installs it. Thirteen tools. The Cloudflare and DataDome interstitials that stop ordinary automation rarely appear here, because there is nothing incoherent for them to catch. There is no captcha solver in here; the point is that you rarely need one.

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

## What changed

AIHawk went viral in 2024 as a bot that applied to jobs for you. That is the
version the press above wrote about. It is no longer the interesting half of this
repository.

The forms were never the hard part. Staying on a site long enough to finish
anything was. So the work went down a layer, into a browser built to reach the
end of a task, and once that browser existed a job application turned out to be
one form among all the others.

AIHawk now hands that browser to your AI client. Ask it to apply to positions.
Ask it to price the same route across five dates. Ask it to pull a table off a
page that fights back. Nothing in the setup changes between them.

## What you need first

**An MCP client.** MCP is the protocol AI clients use to attach external tools.
If you use [Claude Code](https://claude.com/claude-code), Claude Desktop, Cursor
or anything similar, you already have one. This server plugs into it and shows
up as thirteen new tools your model can call.

**[uv](https://docs.astral.sh/uv/)**, which provides the `uvx` command used
below:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh              # macOS, Linux
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"   # Windows
```

**Python 3.11 or newer**, and **Windows or Linux**. The engine is built for
those two.

**A proxy, if you want to appear somewhere else.** Without one the browser runs
on your own connection: the identity still holds together, it just holds together
around you. Any HTTP or SOCKS5 endpoint with credentials in the URL works, and
you want a stable exit IP in the country you intend to appear from. Bring your
own; this project ships none.

## Setup

```bash
claude mcp add stealth --env STEALTHFOX_PROXY=http://user:pass@host:port -- uvx invisible-playwright-mcp
```

Without a proxy, drop the `--env` flag:

```bash
claude mcp add stealth -- uvx invisible-playwright-mcp
```

For any other client, the same thing as a config entry:

```json
{
  "mcpServers": {
    "stealth": {
      "command": "uvx",
      "args": ["invisible-playwright-mcp"],
      "env": {
        "STEALTHFOX_PROXY": "http://user:pass@host:port",
        "STEALTHFOX_SEED": "pick-something-stable",
        "STEALTHFOX_PROFILE_DIR": "/absolute/path/to/profile"
      }
    }
  }
}
```

Use an absolute path for the profile directory. Most clients pass env values
through verbatim, so a leading `~` becomes a folder literally named `~`.

### Check it worked

Restart the client and list your MCP servers. `stealth` should be there,
connected, with thirteen tools attached. Then type one small thing before you
type a big one:

> Use the stealth browser to open a browser fingerprint check page, take a
> screenshot, and tell me the timezone, locale, languages and public IP it
> reports.

Read those four values back against what your own browser reports on the same
page. On a proxied run they should describe the exit country and agree with each
other, not with the machine you are sitting at. That is the entire product thesis,
checkable in one prompt, before you trust it with anything that matters.

The first launch downloads the patched Firefox build, a few hundred megabytes,
so that first run takes a minute and looks like a hang. It is cached afterwards
and every later run starts in seconds. If the server does not appear at all,
`uvx` is not on the PATH the client sees, which is not always the PATH your
shell sees.

There is nothing to clone here. The server installs from PyPI; this repository
is documentation and examples.

## Two things to try

This server drives the browser and only the browser: no disk access, on purpose.
Reading a CV and writing a CSV are your client's own file tools, which the usual
clients all have. If yours does not, ask for the results in chat and save them
yourself.

### Applying to jobs

> Open this careers page: `<paste the URL>`. Filter to backend roles in Europe
> posted in the last two weeks. For each result, open the posting and pull out
> the title, the location, whether it says remote or hybrid, and anything it says
> about visa sponsorship. Skip anything that asks for a security clearance. Read
> my CV at ./cv.pdf and give me the list as a table sorted by how well each one
> matches it. Then take the top three and start the application form for each,
> filling the fields from the CV. Where there is a free text question, write the
> answer yourself from the posting and my CV, keep it under 150 words, and do not
> invent employers or dates. Stop before the final submit button so I can read
> what you wrote before it goes out, and append a row to applications.csv for
> each one: company, role, URL, date.

If a form has a file upload for the CV, whether the model can fill it depends on
your client, not on this server. Ask it to stop at that field and attach the file
yourself. That is one click, once per form.

### Finding a flight

> Go to this flight search site: `<paste the URL>`. One way, Milan to Lisbon,
> economy, one checked bag, one adult. Check every date from the 12th to the 16th
> of next month, one at a time, and read the cheapest fare shown for each day. The
> date field is a calendar widget, so click the days rather than typing them. If a
> date has no availability say so, do not guess a number. When you have all five,
> write them to flights.md sorted by price with the airline and departure time,
> and leave the cheapest one open in a tab so I can book it myself.

The second task shares nothing with the first except the machinery: same server,
same browser, same thirteen tools, nothing reconfigured in between. A browser
that only worked on job boards would be a job board tool.

## How it is put together

```mermaid
flowchart LR
  U["You"] -->|"a prompt, in plain language"| C["AI client<br/>Claude Code · Claude Desktop<br/>any MCP client"]
  C <-->|"MCP · 13 browser tools"| M["invisible-playwright-mcp"]
  M --> B["Patched Firefox<br/>invisible_playwright"]
  B --> P["Your proxy"]
  P --> S["The site"]
```

Three pieces, each usable on its own. The model decides what to do. The MCP
server exposes the browser as tools it can call. The browser is a Firefox patched
at the source so that what it reports about itself holds together.

## Filling a form

Nothing gets clicked until the page has been read, and that is why this survives
forms it has never seen. A form is not a page you script: same role, same
candidate, and the markup still differs by applicant tracking system, by how the
employer configured it, and by which questions a recruiter added that morning.

```mermaid
flowchart TB
  H["Page HTML<br/><i>iframes flattened in first</i>"] --> C1["Containers<br/>[1] Personal info · [2] Address · [3] Custom questions<br/><i>each with its locator</i>"]
  C1 --> F["Fields<br/>question · locator · type · required · options"]
  F --> L["The model answers the questions<br/>Name → Luca · Country → USA · Licence → Yes"]
  L --> A["The connector acts<br/>fill_textbox · select_radio · upload_file"]
```

The first two steps produce a description of the form that owes nothing to the
site's markup: a list of questions, each carrying the address of the element that
answers it. That separation is the design. The model answers questions and never
touches the page. It sees *Country, dropdown, one of USA / India / Italy* and
returns *USA*. How USA gets into that particular dropdown is code, and stays
code.

Which is where the platforms differ. Applications do not run on a thousand
systems, they run on a handful, and each has its habits: a dropdown that is a
real `<select>` on one is a div listening for keystrokes on another.

```mermaid
flowchart TB
  BASE["Base connector<br/>fill_textbox() · select_radio() · upload_file()"]
  BASE --> W["Workday"]
  BASE --> I["iCIMS"]
  BASE --> O["Oracle"]
  BASE --> E["..."]
```

The base connector defines the ordinary behaviour once. Each platform overrides
only what genuinely behaves differently, and most of them override very little.

## The resume

One CV rarely fits two postings. The resume builder takes your profile and the
posting you are applying to and writes a document aimed at that posting, which
then goes into the form.

```mermaid
flowchart LR
  PR["Your profile<br/>experience · skills"] --> G["Resume builder"]
  JD["The job posting"] --> G
  G --> CV["Tailored PDF"]
  CV --> UP["the application's file upload"]
```

Source: [lib_resume_builder_AIHawk](https://github.com/feder-cr/lib_resume_builder_AIHawk)
and [resume_render_from_job_description](https://github.com/feder-cr/resume_render_from_job_description).

## Why fewer challenges appear

This is not headless Chrome with patches sprayed on from JavaScript at runtime.
It is a Firefox patched at the source level and built from that source.

The property that earns the result is coherence. An anti-bot rarely catches you
on one exotic value. It catches you on a contradiction: an American exit address
with a European clock, a Windows user agent with Linux font metrics, a language
that disagrees with the geolocation. Put a proxy in front of an ordinary browser
and you have manufactured exactly that.

```mermaid
flowchart LR
  A["Proxy says: United States"] --> D{"Anti-bot compares"}
  B["Browser says: Italy"] --> D
  D --> E["Contradiction<br/>→ challenge"]
```

The engine turns it around. Before the browser starts, the exit IP is resolved
through the proxy, and everything the browser will declare is derived from that
exit rather than from the machine the process happens to be running on. The
values an IP cannot imply, like screen metrics and GPU strings, are generated
once from `STEALTHFOX_SEED` and held steady.

```mermaid
flowchart LR
  P["Proxy exit IP"] --> C["invisible_core derives<br/>timezone · locale · languages<br/>geolocation · fonts · WebRTC"]
  C --> B["The browser declares all of it"]
  P --> D{"Anti-bot compares"}
  B --> D
  D --> E["Everything agrees<br/>→ nothing to raise a challenge about"]
```

One source, one story, and nothing contradictory left in the declared layer to
find. The smoke test above shows you that layer directly: run it and read the
four values back. What you notice afterwards is an absence. The interstitials,
the checking-your-browser pages and the hard blocks people expect from browser
automation mostly do not appear, because nothing raised them.

Coherence is one input into a site's risk score. It is the input this project
controls, and the one that ordinary automation gets wrong first.

### About challenges

The best captcha is the one nobody asks you to take, and that is the strategy
here: fewer challenges raised means fewer challenges to pass. **There is no
captcha solver in this project** - no third party service wired up, no pass rate
to promise. Cloudflare, Turnstile, DataDome, Kasada, Akamai, reCAPTCHA and
hCaptcha all exist and all still work. What changes is how often you meet one.

When an interactive challenge does appear, `browser_click_at` gives your client a
real pointer: it takes viewport coordinates, moves to them rather than
teleporting, can press and hold, and returns a screenshot of what happened. That
is the tool for sliders and press-and-hold widgets. It will not identify
motorbikes for you, and sometimes the right answer to a challenge is to stop.

If a run stalls, ask for a screenshot. You will see exactly what the browser
sees. Or set `STEALTHFOX_HEADLESS=0` and take the mouse yourself.

## Configuration

Everything is an environment variable on the MCP server entry.

| Variable | What it does |
|---|---|
| `STEALTHFOX_PROXY` | `http://user:pass@host:port`, or `socks5://`. Timezone, locale, languages, geolocation and egress all derive from it. |
| `STEALTHFOX_SEED` | Fixes the seeded half of the identity: fonts, screen, GPU strings. Same seed, same values, every run. |
| `STEALTHFOX_PROFILE_DIR` | Absolute path. Persistent profile, so logins and cookies survive restarts. |
| `STEALTHFOX_HEADLESS` | Headless by default. Set `0` to watch it work in a visible window, worth doing the first few times. |
| `STEALTHFOX_BINARY` | Path to a Firefox build of your own. For people building the engine themselves; it needs a matching seal file or the launch is refused on purpose. |

Set a `STEALTHFOX_SEED` for anything you run more than once. An identity that
changes shape between sessions is its own kind of signal. Pair it with a profile
directory and a stable exit, or you will look like the same account arriving as a
different person every morning.

## The tools

Thirteen, and the count is the ceiling rather than a target: every tool a model
can call is a tool it can call at the wrong moment, so the set stops at what a
browser actually needs.

**Pages:** `session_new_page`, `session_list_pages`, `session_select_page`,
`session_close_page`. Several tabs at once, which is what multi-step work
actually looks like: open a listing in a second page, read it, close it, and go
back to the results without losing your place.

**Reading:** `browser_navigate`, `browser_read_text`, `browser_snapshot`,
`browser_take_screenshot`.

**Acting:** `browser_click`, `browser_click_at`, `browser_type`,
`browser_press_key`, `browser_evaluate`.

You do not call these yourself, the model does. Three are worth explaining
anyway.

`browser_snapshot` returns the interactive elements that are visible, not the
accessibility tree, and that is what keeps long forms working. A single country
dropdown contributes something like two hundred option nodes to a full tree,
which pushes the actual form out of the model's attention and gets the wrong
thing clicked. The visible-elements view fits and stays readable.

`browser_click` takes an element from the snapshot. `browser_click_at` takes
viewport coordinates instead, which is what you want for the things a snapshot
cannot name: calendar grids that redraw every month, drag handles, sliders.

`browser_evaluate` runs arbitrary JavaScript in the page. It is the escape hatch,
and the one tool worth being careful with, since a model that reaches for it too
early will write a scraper where reading the page would have done.

## The pieces

- [invisible_playwright](https://github.com/feder-cr/invisible_playwright) - the
  Python wrapper and the patched Firefox it pins and drives. If you would rather
  script it yourself than ask an AI, use this directly: the API is Playwright's,
  so what you already know applies.
- [invisible-playwright-mcp](https://github.com/feder-cr/invisible-playwright-mcp) -
  the MCP server this README installs.
- [invisible_core](https://github.com/feder-cr/invisible_core) - seed to
  fingerprint to preferences, proxy and geolocation derivation, binary
  resolution. The part that decides what the browser declares.

Issues and pull requests are welcome on whichever of those the problem actually
lives in. If you are not sure, open it here. When something fails on a specific
site, describe the shape of it: which step, what the page did, what the tool
returned, which exit country, whether you were on a persistent profile. "It got
blocked" is not something anyone can act on, and a list of targets in the issue
tracker helps nobody.

The 2024 command line applier is still in the git history if you forked it and
want to compare. It is not maintained, and it will not work against anything
current. Third-party provider plugins are not in this repository: the core is
open source, the plugins were removed for copyright reasons.

## A note on use

This automates a browser under your control. Read the terms of the sites you
point it at, respect their rate limits, and do not use it to create accounts in
bulk or to submit things a human has not read. The examples above stop before the
submit button on purpose.

## License

See [LICENSE](LICENSE).