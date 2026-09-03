---
title: "Home"
nav_order: 1
---

# AIHawk Wiki

AIHawk is an AI agent with a real browser: you say what you want in plain
language, it goes and does it on the actual web. This wiki is the reading
room around it - what an AI web agent is, how the tools in this space compare,
what to do when an agent gets blocked, and the job-application automation this
project grew out of.

The [README](https://github.com/feder-cr/AIHawk#readme) is the fastest way to
run AIHawk. The pages here are for the questions that come before and after:
which tool fits, why something failed, and what is actually happening
underneath.

## The guides

- **[Alternatives and Comparisons](guides-alternatives-and-comparisons.md)** -
  the AI browser-agent landscape: OpenAI Operator and what replaced it,
  browser-use, computer-use agents, and how the open-source options differ.
- **[When the Agent Gets Blocked](guides-when-the-agent-gets-blocked.md)** -
  challenge pages, rate limits, timing tells, and which of those the browser
  can fix versus which are yours.
- **[Job Application Automation](guides-job-application-automation.md)** -
  where this project started: automating application flows with Claude,
  ChatGPT, or plain Python, and what is realistic today.
- **[Using the Agent](guides-using-the-agent.md)** - task-shaped guides for
  putting an agent to work.

## The layer underneath

AIHawk drives a Firefox patched at the C++ level so the browser itself looks
and behaves like a normal desktop browser. That engine has its own
documentation, maintained with the same care as this wiki: the
[invisible_playwright wiki](https://github.com/feder-cr/invisible_playwright/wiki)
covers browser fingerprinting, bot-detection vendors, network and proxy
mechanics, and the automation layer in depth. Pages here link into it wherever
the mechanism matters.
