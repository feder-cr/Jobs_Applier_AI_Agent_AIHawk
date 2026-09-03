---
title: "Automating job applications in Python"
description: "The build-it-yourself route: browser automation plus an LLM API, the four components a real pipeline needs, why naive scripts break on wizards, validation and anti-bot layers, and the honest case for using what already exists."
parent: "Job Application Automation"
nav_order: 3
---


# Automating job applications in Python

Building a job-application bot in Python is a genuinely instructive project: it
touches browser automation, LLM integration, state, and the parts of the web
that push back. This page lays out what the real components are, shows why the
obvious eighty-line script breaks, and closes with the honest note that this
exact project has already been built in the open, because that is literally how
AIHawk started.

One rule this page keeps, like every page under this parent: no job platform is
named, and the examples run against generic forms or pages you serve yourself.
The mechanics are the same everywhere, which is exactly why the generic version
is worth writing down.

## The naive version, to have something to break

Every attempt starts roughly here: Playwright opens the form, an LLM drafts the
answers, the script fills and submits.

```python
from playwright.sync_api import sync_playwright

BACKGROUND = open("background.md").read()   # your real history, as text

def draft(question: str) -> str:
    # any LLM API; the contract is what matters:
    # answer from BACKGROUND only, say "ASK" when the answer is not in it
    ...

with sync_playwright() as p:
    browser = p.firefox.launch()
    page = browser.new_page()
    page.goto("http://127.0.0.1:8000/application-form")  # a page you serve
    for field in page.locator("form [data-question]").all():
        answer = draft(field.get_attribute("data-question"))
        field.fill(answer)
    page.click("#submit")
```

On a form you wrote yourself, this works on the first try, which is what makes
the approach look one weekend wide. The distance between this and a pipeline
that survives real pages is the rest of this page.

## The four components a real pipeline needs

**Form detection.** Real forms do not label themselves with `data-question`.
Fields associate with their questions through `<label for>`, `aria-label`,
`aria-labelledby`, placeholder text, or nothing but visual proximity; required
markers and error text sit in separate nodes; some forms arrive inside an
embedded iframe with its own document. Mapping "what is this field asking" to
"which element do I fill" is a real subproblem, and it is where an LLM earns its
place: handed the rendered page, a model can read the form the way a person
does, which is the approach described in
[getting an AI agent to fill out forms](ai-agent-fill-out-forms.md).

**Answer generation.** The model needs your background as grounding and a
contract that keeps it honest: every claim from the provided history, an
explicit escape hatch ("ASK") for questions it cannot answer from it, and no
improvisation. Tailoring - picking which true things to emphasize for this role
- is the value. Fabricating qualifications is a bug, and it is one your own
pipeline will happily ship at scale if the prompt does not forbid it.

**Session persistence.** Applying is logged-in work spread over days. That
means a persistent browser profile rather than a fresh context per run, so
cookies and logins survive; it also means the same browser identity each time,
because a login that hops between fingerprints looks stolen. Plan for a profile
directory and for state you can resume after a crash mid-wizard.

**Pacing.** The component most builds skip and the first one to matter in
production. Per-account and per-IP rate limits are real, and a submission every
few seconds is a signature no fingerprint work can hide. Pacing is jitter
between actions, minutes between applications, a daily cap, and backoff on
anything that looks like throttling. It is also the ethical component: the
volume ceiling is where "my bot" stops being distinguishable from spam, a
lesson this project's own history documents in detail on
[the history page](open-source-job-application-bot.md).

## Why naive scripts break

**Multi-step wizards.** Real applications are three to eight steps with state:
conditional fields that appear based on earlier answers, a review step that
re-renders everything, a back button that resets more than it should. A script
that models "the form" as one page loses to the first wizard it meets. You need
a loop over steps - read, fill, advance, re-read - and idempotent resume,
because step four is where the timeout happens.

**Client-side validation.** Fields validate on blur and on keystroke; masked
inputs reformat as you type; selects are custom widgets that only respond to
real interaction. Setting `element.value` from JavaScript skips the events the
page listens for, so the value silently fails validation, or arrives empty at
submit. Fill through real typing and clicking. It is telling that AIHawk's own
agent, per its README, refuses to set form fields from JavaScript even when it
would be faster, because a page can tell the difference.

**File uploads.** The resume field is a file input, often behind a styled
button, sometimes a drag-and-drop zone. Playwright's `set_input_files` covers
the plain case; the styled cases need the real input located first. And a
tailored resume means generating a file per application, which is its own
pipeline stage.

**The anti-bot layer.** This is the wall that surprises builders most, because
it has nothing to do with your code being correct. Stock automation is
detectable below your script: driver artifacts, headless tells, a fingerprint
inconsistent with the claimed platform, a TLS handshake that does not match the
user agent. No amount of selector work fixes a page that has already decided
what you are. The mechanism layer - fingerprinting surfaces, detection vendors,
network tells - is documented in depth on the
[invisible_playwright wiki](https://github.com/feder-cr/invisible_playwright/wiki),
and the agent-level symptoms in
[why does my AI agent get blocked?](why-does-my-ai-agent-get-blocked.md). If
you stay on the build-it-yourself road, that engine is usable as a library:
[invisible_playwright](https://github.com/feder-cr/invisible_playwright) is a
Firefox patched at the C++ level, driven through the standard Playwright API,
so the code above ports by changing the launch.

## Or use what exists

Here is the honest close. The pipeline this page describes - form reading,
grounded answer generation, persistent sessions, pacing, on a browser built to
look like a real one - is an open-source project you can read instead of
rediscover. [AIHawk](https://github.com/feder-cr/AIHawk) began in 2024 as
exactly this Python bot, reached about 30,000 stars and a wave of press
coverage, and grew into a general web agent on that same hardened engine. It is
MIT-licensed; run it as an interface with `uvx aihawk ui`, script it headless
with `uvx aihawk do "..."`, or take just the browser layer as a library and
keep your own agent logic on top.

Building your own is still a fine choice when the point is learning or when
your flow is unusual. But go in knowing which parts are the actual work: not
the form filling, which a weekend gets you, but the wizard state, the
validation-safe input, the stable identity, and the restraint.

## Conclusion

A real job-application pipeline in Python is four components - form detection,
grounded answer generation, session persistence, pacing - sitting on a browser
that can survive being looked at. The naive script fails on multi-step wizards,
event-driven validation, uploads, and an anti-bot layer that inspects the
browser underneath your code. All four components, on a hardened engine, exist
in the open already; whether you build or adopt, the volume ceiling and the
review-before-submit rule are the parts that keep the pipeline worth running.

## Short answers to the questions that lead here

**Can I automate job applications with Python and Playwright?** Yes, and the
form-filling part is genuinely easy. The real work is wizard state,
validation-safe typing, persistent sessions, pacing, and a browser that does
not advertise itself as automation.

**Which LLM do I need?** Any API model works for answer generation. The prompt
contract matters more than the model: answers only from your provided
background, with an explicit "ask the human" escape for anything else.

**Why does my script's input disappear at submit?** You are probably setting
values from JavaScript, which skips the input events client-side validation
listens for. Type and click like a user; the value then exists the way the page
expects.

**Why does my bot get blocked even though the code works?** Detection operates
below your script: driver artifacts, headless tells, fingerprint and TLS
inconsistencies. See the
[invisible_playwright wiki](https://github.com/feder-cr/invisible_playwright/wiki)
for the mechanism layer; correctness of your Python is not the question being
asked.

**How fast can I safely go?** Slower than the code allows. Jitter inside a
form, minutes between applications, a daily cap you would defend out loud.
Past that ceiling you are building a spam tool with extra steps, and the
account it burns is yours.

**Is there an open-source version already?** Yes -
[AIHawk](https://github.com/feder-cr/AIHawk), which started as exactly this
bot and is now a general web agent on a hardened Firefox. Reading its layout is
a shortcut even if you then build your own.

## Sources

- The [AIHawk README](https://github.com/feder-cr/AIHawk#readme), retrieved
  2026-09-03, for the interface and headless commands, the library and MCP
  layers, the license, and the agent's refusal to set form fields from
  JavaScript.
- [404 Media's October 2024
  report](https://www.404media.co/i-applied-to-2-843-roles-the-rise-of-ai-powered-job-application-bots/),
  retrieved 2026-09-03, for what the original bot generation actually did in
  the field: biographical fill, generated resumes, customized cover letters,
  unattended volume.
- This project's own engine documentation, linked throughout, for the
  fingerprinting and detection mechanics summarized in the anti-bot section.

**See also:** [getting an AI agent to fill out
forms](ai-agent-fill-out-forms.md) for the form-reading approach in isolation,
[automating job applications with
Claude](automate-job-applications-with-claude.md) for the no-code version of
this pipeline, [the open-source job application bot, and what it
became](open-source-job-application-bot.md) for where the build-it-yourself
road led once, and the
[job application automation hub](guides-job-application-automation.md).

---

*Written by the maintainer of [AIHawk](https://github.com/feder-cr/AIHawk),
which exists because someone built this exact Python project and then spent two
years on the parts this page says are the actual work.*
