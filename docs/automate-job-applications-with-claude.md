---
title: "Automating job applications with Claude"
description: "Claude Code or Claude Desktop plus an MCP browser gives you an agent that works through application forms while you watch - what that setup does well, what it costs, and the pacing that keeps it from hurting you."
parent: "Job Application Automation"
nav_order: 1
---


# Automating job applications with Claude

The current, real answer to "can Claude apply to jobs for me" is: Claude plus an
MCP browser can work through an application form in front of you, reading each
question, drafting an answer from your background, and filling it in while you
watch every step. That is genuinely useful. It is not a fire-and-forget pipeline
that sprays hundreds of applications overnight, and the second half of this page
is about why you do not want it to be.

## The setup, honestly

Claude brings the model; you add a browser it can drive. If you use Claude Code,
the whole setup is one command, run once:

```bash
claude mcp add -s user stealth -- uvx invisible-playwright-mcp
```

Claude Desktop and Cursor take a JSON config block instead of a command; the
block, and which file it goes in, are in the
[server's README](https://github.com/feder-cr/invisible-playwright-mcp). The
server exposes a patched Firefox over MCP - the same engine behind
[AIHawk](https://github.com/feder-cr/AIHawk), which is where this wiki lives.

One thing the first run will not warn you about: the browser is about a quarter
of a gigabyte and is downloaded on the first request that needs a page, so your
first instruction sits silent for a while. Fetch it ahead of time, in a terminal
where you can watch the progress:

```bash
uvx invisible-playwright fetch
```

After that, you talk to Claude the way you already do. Give it your background
first - paste your resume text, or point Claude Code at the file - then open a
listings page or an application form and ask it to work through it. Everything
it does appears as a visible tool call: navigate, read the page, type into a
field, click. You are not trusting a black box; you are supervising an intern
with a very fast reading speed.

## What Claude is actually good at here

**Reading a form nobody wrote a script for.** Application forms differ on every
site: different field names, different steps, questions hidden behind dropdowns,
a resume upload here and a text box asking you to retype the same history there.
A traditional bot needs selectors written for each variant and breaks when the
markup changes. Claude reads the rendered page like a person does, so an
unfamiliar form is just another form.

**Tailoring answers from your background to the question asked.** "Describe a
project where you led a migration" gets a better answer from a model holding
your actual history than from a paragraph you pasted into twenty forms. This is
the honest version of tailoring: choosing which true things to emphasize for
this role. It is not inventing qualifications, and you should say so in your
instructions - tell Claude explicitly that every claim must come from the
background you provided, and that missing information means asking you, not
improvising.

**Noticing what should stop the process.** A good agent run includes moments
where Claude halts and asks: this form wants a salary expectation, this question
is about work authorization, this checkbox is a legal attestation. Those are
yours. A model that answers them for you is not saving you time, it is signing
things in your name.

## What it does badly

**Cost per application.** A multi-step wizard means reading each step, reasoning
about each field, and a tool call per interaction - dozens of model round trips
for one submission, on your plan or API bill. For one thoughtful application
that is fine. As a bulk strategy it is an expensive way to get a worse outcome
than five careful applications would have gotten you.

**Judgment calls it should not make alone.** Compensation, notice periods,
relocation, visa status, disability and veteran self-identification, references.
None of these belong to an agent. The workable pattern is: Claude fills the
factual and narrative fields, then stops and lists everything it left blank and
why, and you finish the pass yourself.

**Anything it was not told.** A model asked a question it has no data for will
sometimes produce a plausible answer anyway. That failure mode is exactly the
one a job application cannot afford. Ground it: full background in, explicit
"ask, never guess" instruction, and your own read of the filled form before
anything is submitted.

## The part the media coverage was about

This project's own history is the clearest available evidence on volume, and it
is worth being straight about. AIHawk started life as a bulk job-application
bot. In October 2024, 404 Media's Jason Koebler
[used it to apply to 17 jobs in one hour](https://www.404media.co/i-applied-to-2-843-roles-the-rise-of-ai-powered-job-application-bots/),
writing up a user who had let it run to 2,843 applications - the bot entered
biographical details, generated resumes, wrote customized cover letters, and
filed the paperwork on its own.
[TechCrunch covered the same story](https://techcrunch.com/2024/10/10/a-reporter-used-ai-to-apply-to-2843-jobs/)
and called the result a bizarre loop: applicants automating applications while,
by the figure TechCrunch cited, 42 percent of companies were already using AI to
screen them, humans increasingly absent from both sides. The Verge's same-day
piece put the criticism in its headline: AI was enabling job seekers to think
like spammers.

The criticism was not wrong, and the applicant is who it lands on. Sprayed
applications carry replicated mistakes at scale, answers that read as generic
because they are, and a volume signature that platforms throttle and recruiters
learn to discount. An account that submits forty applications an hour does not
look like an eager candidate; it looks like what it is.

So the etiquette section of this page is short and unambiguous. Keep a human
pace: a handful of applications in a session, not a stream. Review every filled
form before it is submitted - the AIHawk README's own rule is "do not submit
anything a human has not read," and it applies doubly when Claude did the
writing. Let quality per application be the metric, because it is the only one
that ever paid the applicant.

## Conclusion

Claude Code or Claude Desktop plus `invisible-playwright-mcp` gives you an agent
that can genuinely work an application form: read it, tailor honest answers from
your background, fill it while you watch, and stop where your judgment is
required. Used at human pace with a human review before every submit, that is a
real assist. Used as a spray tool, it recreates the exact behavior this
project's own press coverage documented the costs of. The setup takes one
command; the discipline is the part you bring.

## Short answers to the questions that lead here

**Can Claude actually fill out a job application?** Yes. With an MCP browser
attached, Claude reads the rendered form, types into fields, handles multi-step
wizards, and shows you each action as it happens. You review and submit.

**Does this work with Claude Desktop, or only Claude Code?** Both, and Cursor
too. Claude Code takes the one-line `claude mcp add` command; the others take a
JSON config block documented in the MCP server's README.

**Will Claude write my cover letter and answers?** It will draft them from the
background you give it, tailored to the posting. Keep it grounded: instruct it
that every claim must come from your provided history and that gaps mean asking
you, not inventing.

**How many applications can I do this way?** Technically many; practically you
should not. Each application costs real model usage, and bulk volume is the
pattern that damaged applicants in this project's own history. A few careful,
reviewed applications beat a spray.

**Will the browser get blocked?** The engine is a Firefox patched to look and
behave like a normal desktop browser, which addresses the fingerprint layer.
Pacing, account behavior, and your network exit are still yours - see
[why does my AI agent get blocked?](why-does-my-ai-agent-get-blocked.md).

**Should Claude answer salary, visa, or self-identification questions?** No.
Have it stop and list them for you. Those answers bind you; a model should not
be producing them unsupervised.

## Sources

- The [AIHawk README](https://github.com/feder-cr/AIHawk#readme), retrieved
  2026-09-03, for the `claude mcp add` setup line, the engine download
  behavior, and the "do not submit anything a human has not read" rule.
- [404 Media, "I Applied to 2,843 Roles With an AI-Powered Job Application
  Bot"](https://www.404media.co/i-applied-to-2-843-roles-the-rise-of-ai-powered-job-application-bots/),
  Jason Koebler, retrieved 2026-09-03.
- [TechCrunch, "Someone claims to have used AI to apply to 2,843
  jobs"](https://techcrunch.com/2024/10/10/a-reporter-used-ai-to-apply-to-2843-jobs/),
  Kyle Wiggers, October 10 2024, retrieved 2026-09-03, including the 42 percent
  AI-screening figure it cites.
- The Verge's October 10 2024 piece is linked from the
  [project README](https://github.com/feder-cr/AIHawk#readme); the site blocks
  automated retrieval, so the "think like spammers" phrasing is quoted from its
  headline as linked there.

**See also:** [automating job applications with
ChatGPT](automate-job-applications-with-chatgpt.md) for the other assistant's
side of this, [automating job applications in
Python](automate-job-applications-python.md) for the build-it-yourself route,
[the open-source job application bot, and what it
became](open-source-job-application-bot.md) for the full history this page
compresses, and [getting an AI agent to fill out
forms](ai-agent-fill-out-forms.md) for the form mechanics on their own.

---

*Written by the maintainer of [AIHawk](https://github.com/feder-cr/AIHawk),
which began as the job-application bot in those 2024 headlines and grew into a
general web agent. The browser and the agent are the easy part now; applying
like a person is still the part that works.*
