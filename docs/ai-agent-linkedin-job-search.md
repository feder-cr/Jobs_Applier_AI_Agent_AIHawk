---
title: "An AI agent for your LinkedIn job search"
description: "What an agent genuinely does for a job search - read postings, match them against your background, draft tailored answers, stop before every submit - and the two things it should never become: a spray cannon or an outreach machine."
parent: "Job Application Automation"
nav_order: 7
---


# An AI agent for your LinkedIn job search

The useful version of "an AI agent for my LinkedIn job search" is an
assistant that reads faster than you and never gets tired of postings, with
you making every decision that matters. The useless version is the same
software with the human removed - and this project has unusual standing to
say so, because it built the useless version first, at scale, and the tech
press documented what happened. This page describes the useful version
concretely, and is plain about the boundaries that keep it useful.

One boundary sits above all the others, so it goes first. LinkedIn's User
Agreement (section 8.2) prohibits using "bots or other unauthorized
automated methods to access the Services," and its help center says accounts
using prohibited automation tools "risk having their accounts restricted or
shut down." Any agent acting on LinkedIn itself operates against that
baseline - the [head page of this cluster](automating-linkedin-job-applications.md)
carries the full quotes and the enforcement record. The workflow below is
built to keep the agent's genuine value while keeping you, not the agent, as
the actor on the platform wherever an action binds you.

## What an agent can genuinely do

**Read postings at volume, so you do not have to.** The most tedious part of
a search is not applying; it is reading forty postings to find the six worth
your time. Reading is exactly what an LLM with a browser does well: open a
posting, extract what the role actually is under the boilerplate, note the
hard requirements, flag the mismatches. Give the agent your background first
and the reading becomes screening: "of these postings, which ones want
something I actually have, and what disqualifies me from the rest."

**Match honestly against your background.** A good prompt here is explicit
in both directions: surface real fits, and name real gaps. An agent that
tells you a posting wants five years of something you have two of is doing
the job; one that rounds you up is manufacturing a bad interview. Instruct
it that every claim must come from the background you provided - the
grounding rules from
[automating job applications with Claude](automate-job-applications-with-claude.md)
apply verbatim.

**Draft tailored answers and letters.** For the postings that survive
screening, the agent drafts: a cover letter emphasizing the true things this
role cares about, answers to written questions from your actual history.
Tailoring, honestly defined, is choosing which true things to lead with -
not inventing. The draft is raw material for your edit, not a finished
artifact.

**Keep a human before every submit.** The project's README states the rule
in one line: do not submit anything a human has not read. Mechanically that
means the agent works through a form in front of you and stops - it does
not click the final button, and it halts on questions that bind you (salary,
visa status, relocation, legal attestations) rather than answering them in
your name.

## What it cannot and should not do

**Mass application is out, and not as etiquette - as the documented failure
mode.** When 404 Media ran this project's old bot, it applied to 17 jobs in
an hour, in a story built around a user who had reached 2,843 applications;
TechCrunch's same-day coverage noted that 42 percent of companies were
already using AI to screen applicants, making the whole exchange a loop of
machines talking to machines; The Verge's headline said job seekers were
being enabled to think like spammers. The costs land on the applicant:
errors replicated thousands of times, generic answers recruiters learn to
discount, interviews you walk into unprepared because you never read the
application that earned them - and platform enforcement on top, since
volume is the most legible signal a logged-in platform reads (see
[how LinkedIn detects bots](linkedin-bot-detection.md)). An agent run at
spray volume is the old bot with better prose and a bigger bill.

**Unattended runs on the platform are out.** The value of the agent is
judgment applied per posting; unattended, that judgment is unreviewed, which
on a job application means unreviewed claims made in your name. If a task
needs no judgment, an agent is the wrong tool for it anyway; if it needs
judgment, the judgment needs checking.

**And the adjacent thing this project does not do:** there is a whole
industry of LinkedIn outreach automation - connection-request campaigns,
message sequences, engagement pods, growth-hacking tooling for sales and
recruiting. It is a real market and this is not it. That category is
squarely inside the User Agreement's ban on automated methods to "add or
download contacts, send or redirect messages ... or otherwise drive
inauthentic engagement," and its output is the noise every LinkedIn user
already wades through. AIHawk is not an outreach tool, ships nothing for
campaigns or sequences, and this wiki will not become a manual for them.
That is the whole paragraph, on purpose.

## Where AIHawk fits, concretely

AIHawk is a general web agent on a hardened Firefox: you say what you want
in plain language, it drives a real browser - pointer moving, keys pressed,
no JavaScript shortcuts a page could detect. Two ways in, per the README: if
you already use Claude Code, Claude Desktop or Cursor, one command adds the
browser to your assistant (`claude mcp add -s user stealth -- uvx
invisible-playwright-mcp`); otherwise `uvx aihawk ui` gives you chat beside
a live browser view with an OpenRouter key, and `uvx aihawk do "..."` runs a
single instruction headlessly.

The job-search shape that fits inside the boundaries above puts the agent's
volume where no platform terms are implicated, and the human at every
binding action:

1. **Ground it.** Paste or point it at your real background once per
   session. Add the standing instruction: claims only from this background;
   gaps mean asking, not improvising.
2. **Let it read and screen.** Collect postings you are interested in and
   have the agent read each one against your background - fits, gaps, and
   what a strong application would emphasize. This is reading, at a pace
   you set, with you present.
3. **Have it draft off-platform.** Cover letters and question answers are
   drafted from the posting text and your background - work that does not
   touch your account at all.
4. **You act.** You edit the drafts, you fill or approve the form, you
   click submit, at whatever pace a person applies at - a handful per
   session. Where the agent works a form in front of you, it stops before
   the submit and lists everything it left for your judgment.

Steps 2 and 3 are where the agent saves you hours, and they are also -
not coincidentally - the steps where nothing is acting on your account. If
your model tooling is the open question,
[which model to use with AIHawk](which-model-to-use-with-aihawk.md) covers
the trade-offs, and
[using AIHawk without an API key](using-aihawk-without-an-api-key.md)
covers the assistant-hosted route.

## Short answers to the questions that lead here

**Can an AI agent do my LinkedIn job search for me?** It can do the reading,
screening and drafting - most of the hours - with you doing the judging and
submitting. Removing the human entirely recreates the spray bot, with the
documented costs and the account risk that came with it.

**Is using an AI agent on LinkedIn against the terms?** Automated access is
prohibited by the User Agreement, and the account risk of automation on the
platform is yours. The workflow above concentrates the agent's work
off-platform and keeps a human as the actor for anything that binds you.
Read [the head page](automating-linkedin-job-applications.md) before
deciding anything.

**How many applications should the agent help with per day?** A number a
person could genuinely produce and review - single digits in a session,
each one read before submit. Volume is what broke this approach in 2024,
and it is entirely your choice.

**Will it write my cover letters?** It will draft them, tailored to the
posting from your real background. You edit and own the result; instruct it
explicitly that missing information means asking you.

**Can it also do my LinkedIn networking and outreach?** No, deliberately.
Automated connection requests and message sequences are inauthentic
engagement under LinkedIn's own terms, and this project does not build for
them.

**What does AIHawk actually run on?** A patched Firefox driven over MCP -
either by your existing assistant (Claude Code, Claude Desktop, Cursor) or
by the project's own `uvx aihawk ui` / `uvx aihawk do` with an OpenRouter
key.

## Sources

All retrieved 2026-09-03.

- [LinkedIn User Agreement](https://www.linkedin.com/legal/user-agreement),
  section 8.2, for the automated-access and inauthentic-engagement
  prohibitions quoted.
- [LinkedIn Help: Prohibited software and extensions](https://www.linkedin.com/help/linkedin/answer/a1341387),
  for the "restricted or shut down" consequence.
- [404 Media, "I Applied to 2,843 Roles: The Rise of AI-Powered Job
  Application Bots"](https://www.404media.co/i-applied-to-2-843-roles-the-rise-of-ai-powered-job-application-bots/),
  Jason Koebler, October 10 2024, for the 17-in-an-hour and 2,843 figures.
- [TechCrunch, "Someone claims to have used AI to apply to 2,843
  jobs"](https://techcrunch.com/2024/10/10/a-reporter-used-ai-to-apply-to-2843-jobs/),
  Kyle Wiggers, October 10 2024, for the 42 percent AI-screening figure.
- The Verge's October 10 2024 piece is linked from the
  [project README](https://github.com/feder-cr/AIHawk#readme); the site
  blocks automated retrieval, so its framing is cited from the headline as
  linked there.
- The [AIHawk README](https://github.com/feder-cr/AIHawk#readme), for the
  two ways to run the agent, the input-event behavior, and the human-review
  rule.

**See also:** [automating LinkedIn job applications: what exists and what
it costs you](automating-linkedin-job-applications.md) for the landscape
and the terms reality, [automating job applications with
Claude](automate-job-applications-with-claude.md) for the assistant-driven
setup this page's workflow runs on, [LinkedIn Easy Apply
bots](linkedin-easy-apply-bots.md) for the volume-first class this page is
the alternative to, and [getting an AI agent to fill out
forms](ai-agent-fill-out-forms.md) for the form mechanics.

---

*Written by the maintainer of [AIHawk](https://github.com/feder-cr/AIHawk).
The agent got better than the 2024 bot in every way that matters, and the
most important improvement is the one that looks like a limitation: it
waits for you.*
