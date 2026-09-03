---
title: "The open-source job application bot, and what it became"
description: "AIHawk's own history, told straight: the 2024 bulk-application bot, the 30,000 stars and the media wave, the spammers criticism and the fair answer to it, and why the project became a general web agent."
parent: "Job Application Automation"
nav_order: 4
---


# The open-source job application bot, and what it became

If you searched for an open-source job application bot, this repository is
probably one of the results, and it earned that placement the loud way: in 2024
it was the bot in the headlines. This page is the project telling its own
story, including the part where the criticism was substantially right - because
what the project became only makes sense once you see what the original hit,
and what it hit first was its own ceiling.

## What the original bot was

The project began as a Python bot that automated job applications end to end.
Point it at listings, give it your history, and it did the rest: entered
biographical details into forms, generated resumes, wrote customized cover
letters per posting, checked the required boxes, and submitted - unattended, in
volume. That description is not marketing memory; it is how
[404 Media](https://www.404media.co/i-applied-to-2-843-roles-the-rise-of-ai-powered-job-application-bots/)
described what it watched the bot do.

It spread fast because it sat on a real nerve. Application forms had grown long
and repetitive, applicants were being screened by software, and here was
software that screened back. The repository climbed to about 30,000 stars, and
in October 2024 the press arrived.

## The media wave, and what it actually said

404 Media's Jason Koebler ran the bot himself and
[applied to 17 jobs in one hour](https://www.404media.co/i-applied-to-2-843-roles-the-rise-of-ai-powered-job-application-bots/),
building the piece around a user who had let it run to 2,843 applications.
[TechCrunch picked the story up the same day](https://techcrunch.com/2024/10/10/a-reporter-used-ai-to-apply-to-2843-jobs/)
and named the uncomfortable context: by the figure it cited, 42 percent of
companies were already using AI to screen applicants, so automated applications
meeting automated screening formed what it called a bizarre loop, with humans
increasingly absent from both ends of hiring. The Verge published its take the
same day with the criticism in the headline: AI was enabling job seekers to
think like spammers. The
[project README's featured strip](https://github.com/feder-cr/AIHawk#readme)
carries the full set - Business Insider, Semafor, Wired's Italian edition, and
Vanity Fair Italy alongside those three.

Thirty thousand stars and international coverage is the part a project brags
about. The next section is the part that matters more.

## The criticism deserved a straight answer

The spammers framing was not a cheap shot. A bot whose value proposition is
volume converges on spam mechanics no matter how it is built: the same answers
fanned out everywhere, any error in your data replicated 2,843 times, cover
letters that read generic because they are generated at a rate no one reviews.
And the damage lands on the applicant first. Recruiters learn to discount what
looks mass-produced; platforms throttle and flag accounts with machine-like
volume; an interview earned by an application you never read is an interview
you walk into unprepared. The loop TechCrunch described makes it worse at the
system level - every escalation in application volume buys more automated
screening, which everyone then has to out-volume.

There was a second, quieter problem: the original bot was welded to the markup
of the pages it automated. Selectors written for a specific flow break when the
page changes, and pages change constantly - some of that is ordinary
redesign, some of it is aimed. A tool built as a collection of site-specific
scripts is in a maintenance race it cannot win, which is why this wiki's pages
name no job platforms at all: the durable knowledge is the mechanics that are
the same everywhere, not any one site's layout.

So the project's answer to the criticism is not a defense of spray. It is
agreement, followed by a change of direction: the metric that pays the
applicant is quality per application, and the honest way to build for that is
an agent that does one application well, with a human reviewing it, rather
than a cannon that does thousands unread. The project's own README now states
the rule in one line: do not submit anything a human has not read.

## What it became, and why

Strip the volume out of the original bot and ask what was actually valuable in
it, and two parts survive. First, a model that can read any form: the LLM never
cared that the form was a job application, and reading an unfamiliar page is
precisely what site-specific scripts could not do. Second, a browser that holds
up under inspection, because the anti-bot layer meets automation everywhere,
not just on application flows.

Those two parts are simply a general web agent, and that is what AIHawk is
now: you say what you want in plain language, and it does it in a real browser
- the pointer moves, keys are pressed, and it declines shortcuts a page could
detect, like setting form fields from JavaScript. The browser is the part that
went deepest: a Firefox patched at the C++ level so the browser itself, not a
wrapper of overrides, looks and behaves like a normal desktop Firefox. That
engine and its documentation live at
[invisible_playwright](https://github.com/feder-cr/invisible_playwright), and
what an agent in this category is at all is covered in
[what is an AI web agent?](ai-web-agent-explained.md).

There are two ways in, both current. If you already use an assistant that runs
tools - Claude Code, Claude Desktop, Cursor - you add the browser to it as an
MCP server, and your assistant brings the model. Otherwise `uvx aihawk ui`
runs the project's own interface, chat beside a live browser view, with the
model coming from an OpenRouter key you supply. The code is MIT-licensed as of
September 2026; everything distributed earlier was and remains AGPL-3.0.

Job applications did not disappear from the picture - this page's siblings
cover doing them [with Claude](automate-job-applications-with-claude.md),
[with ChatGPT](automate-job-applications-with-chatgpt.md), and
[in Python](automate-job-applications-python.md). What disappeared is the
unattended volume. The agent works through an application in front of you,
drafts from your real history, and stops where your judgment is required.

## Conclusion

The open-source job application bot was real, enormous, and covered by half
the tech press in a week, and the sharpest criticism it drew was right:
volume-first automation hurts the people it claims to help, applicants
included. What survived the criticism was not the bulk pipeline but the two
hard parts inside it - a model that reads any form, and a browser built to
withstand inspection - and those two parts, generalized, are AIHawk today: an
open-source web agent that treats a job application as one task done well
rather than thousands done blind.

## Short answers to the questions that lead here

**What was the original AIHawk?** A 2024 open-source Python bot that applied
to jobs automatically: form filling, generated resumes, customized cover
letters, unattended submission. It reached about 30,000 stars and was covered
by 404 Media, TechCrunch, The Verge, Business Insider, Semafor, Wired's
Italian edition, and Vanity Fair Italy.

**Is the bulk-application bot still what this repository is?** No. The project
is now a general web agent on a hardened browser. The job-application use case
remains supported as supervised, one-at-a-time work, not unattended volume.

**Was the "spammers" criticism fair?** Substantially, yes. Spray-and-pray
replicates errors at scale, reads as generic, and triggers the throttling and
discounting that hurt the applicant first. The project's answer is quality per
application, not more spray.

**Why did it stop being job-board-specific?** Site-specific scripts lose the
maintenance race against changing pages, and a general agent that reads any
form does not need them. That is also why no page on this wiki names a job
platform.

**Can I still use it to apply to jobs?** Yes - through an assistant you
already have via MCP, or through its own interface. See
[automating job applications with Claude](automate-job-applications-with-claude.md)
for the concrete setup and the pacing rules that keep it useful.

**What license is it under?** MIT for everything distributed from
September 2, 2026; earlier distributions were AGPL-3.0 and stay under it.

## Sources

- [404 Media, "I Applied to 2,843 Roles With an AI-Powered Job Application
  Bot"](https://www.404media.co/i-applied-to-2-843-roles-the-rise-of-ai-powered-job-application-bots/),
  Jason Koebler, retrieved 2026-09-03, for the first-hand account of the
  original bot's behavior and volume.
- [TechCrunch, "Someone claims to have used AI to apply to 2,843
  jobs"](https://techcrunch.com/2024/10/10/a-reporter-used-ai-to-apply-to-2843-jobs/),
  Kyle Wiggers, October 10 2024, retrieved 2026-09-03, for the 42 percent
  AI-screening figure and the automation-loop framing.
- The [AIHawk README](https://github.com/feder-cr/AIHawk#readme), retrieved
  2026-09-03, for the featured-coverage list, the current two ways to run the
  agent, the human-review rule, and the licensing dates.
- The Verge's October 10 2024 piece is linked from that README; the site
  blocks automated retrieval, so its framing is cited from the headline as
  linked there.

**See also:** the
[job application automation hub](guides-job-application-automation.md) for the
practical guides this history sits behind,
[automating job applications in Python](automate-job-applications-python.md)
for the road the original bot walked,
[what is an AI web agent?](ai-web-agent-explained.md) for the category it
moved into, and
[why does my AI agent get blocked?](why-does-my-ai-agent-get-blocked.md) for
the layer that made the browser the hard part.

---

*Written by the maintainer of [AIHawk](https://github.com/feder-cr/AIHawk).
The 2,843 applications in those headlines were sent by the old bot; the point
of the new agent is that nobody should ever send that many again.*
