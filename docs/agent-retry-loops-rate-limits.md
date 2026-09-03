---
title: "Agent retry loops trip rate limits, not fingerprints"
description: "An AI agent's retry and re-plan loop multiplies one task into a burst of requests. Rate limits count that burst; no browser fixes volume. Where the throttle lives."
parent: "When the Agent Gets Blocked"
nav_order: 3
---


# Agent retry loops trip rate limits, not fingerprints

An agent whose browser looks like a real person's will still get blocked if it asks
for the same page thirty times in ten seconds. That block has nothing to do with the
fingerprint. It is a counter.

This page is about the failure mode a perfect disguise does not touch. When a step
fails, an AI agent does not give up: the error goes back to the model, the model
re-plans, and it tries again - a different selector, a reload, a fresh read of the
page. Every one of those attempts is more requests, and a stack of attempts per
minute is a volume signal that trips rate limits and quotas long before any
fingerprint check runs. The fix does not live in the browser. It lives in how the
loop is bounded and how you use it.

## Why an agent makes more traffic than a person

A person who knows what they want loads a page once. An agent observes, decides,
acts, and when the action fails it recovers - and recovery is a request multiplier.
Three things stack:

- **Retries.** A slow load, a selector that missed, a transient error, and the agent
  tries the step again. One logical action becomes three or five page loads.
- **Re-planning.** In AIHawk's loop, a failed tool call is not the end of the task:
  the error text is fed back to the model as the result, and the model decides what
  to do next. That is what makes it an agent rather than a script, and what it
  usually decides is to look again - re-read the page, reload it, navigate back to
  re-orient. Each of those is a fresh visit to a URL a person loaded once.
- **Exploration.** An agent that does not know a site's layout probes it: opens a
  page to see what is there, backs out, opens another.

The result is that one instruction - "find the price for each of five dates" - can
produce ten or twenty page loads, most of them to the same few URLs, in a burst
measured in seconds. That pattern is trivial to count, and counting is exactly what
a rate limiter does.

## A rate limit counts; it does not look

A fingerprint check and a rate limit answer different questions. The first reads
properties of the client - the GPU string, the canvas hash, the network handshake -
and asks "is this a real browser". The engine under AIHawk is built to make that
answer yes. The second never opens the browser at all: it counts how many requests
arrived from this address, this account, or this session, in this window, and
compares the count to a threshold. The most convincing browser ever built increments
that counter by exactly one per request.

| Signal | What it reads | Does a real-looking browser help |
|---|---|---|
| Fingerprint / driver / network handshake | Properties of the client | Yes - this is what the engine is for |
| Rate limit / quota | Count of requests over time | No - N requests is N requests |
| Per-account quota | Actions tied to one identity | No - the account is the unit, not the browser |
| Behaviour / velocity | Timing and shape of the traffic | No - the loop decides the timing |

The bottom three rows are not fixable from any browser, because the browser only
controls what one request looks like, not how many are sent or how fast. When a
clean fingerprint still gets blocked, volume and address are the usual reasons -
[the engine wiki has a page on exactly that](https://github.com/feder-cr/invisible_playwright/wiki/why-blocked-with-a-clean-fingerprint).

## What bounds the loop in AIHawk

AIHawk's loop carries two bounds worth knowing about, because they shape what a
runaway task can and cannot do:

- **A turn ceiling.** One instruction runs for at most 25 model turns by default,
  and when the ceiling is hit the task stops with a plain message instead of
  looping on. The message tells you the remedy too: narrow the task.
- **One thing at a time.** Instructions are serialised - one instruction at a time
  on one browser - and the system prompt tells the model to prefer one clear action
  per turn over long chains.

Be honest about what a ceiling is, though: it is a stop, not a throttle. It caps how
big a burst one instruction can become; it does not pace the requests inside the
burst, and it does not stop *you* from immediately issuing the same instruction
again. The half that no product can supply is how often you run it.

## The throttle lives in how you drive it

- **Do not re-run a failed task immediately.** The worst response to a block or a
  failure is the identical request again, faster. Wait, and wait longer each time.
- **Narrow the task instead of repeating it.** If an instruction hits the turn
  ceiling, splitting it into smaller instructions with pauses between them produces
  less traffic than re-running the big one until it fits.
- **Mind the exit, not the browser count.** The unit a counter sees is requests per
  address and per account. Several agents behind one exit IP, each politely pacing
  itself, are one very busy client to the site.
- **If you script it, budget it.** A scheduled check on the engine (the
  script pattern on
  [the monitoring page](how-to-monitor-a-page-with-an-ai-agent.md))
  makes it easy to put a browser run in cron, which makes it easy to build an
  accidental refresh storm. Give
  the script a budget and backoff, because that is the layer that owns the schedule:

```python
import subprocess, time

def run_with_backoff(check_cmd, *, max_attempts=3):
    for attempt in range(max_attempts):
        r = subprocess.run(check_cmd,
                           capture_output=True, text=True)
        if r.returncode == 0:
            return r.stdout
        time.sleep(60 * 2 ** attempt)   # 1 min, 2 min, 4 min - never instantly
    raise RuntimeError("giving up instead of hammering")
```

The engine makes each visit look right; the script decides how many visits happen
and when. They are separate jobs, and the second one cannot be delegated downward.

## What the browser fixes, and what it does not

The honest split, because overclaiming here is a way to get someone blocked while
they trust a promise that was never true.

**What the engine handles.** The fingerprint, driver and network layers read as a
genuine Firefox, so the class of check that asks "is this a real browser" mostly
answers yes. Same seed, same identity, every run, so a failure is reproducible.

**What you supply.** The engine does not change your address's reputation, does not
create per-account quota out of nothing, and does not decide how often you run
tasks. A real-looking browser on a
[datacenter address is still on a datacenter address](https://github.com/feder-cr/invisible_playwright/wiki/can-websites-detect-a-datacenter-proxy-ip),
and a counter on the address does not care how good the browser is.

Put plainly: the engine makes each request look like it came from a real person. It
does not make thirty requests look like one. That second job belongs to whoever
decides how often the agent runs, which is you.

## Conclusion

Retrying and re-planning are what make an agent an agent, and they are also what
turn one instruction into a burst of requests. Bursts are counted, and a counter is
a different defence from a fingerprint check. AIHawk bounds the burst - a turn
ceiling, serialised instructions - but pacing between runs, backoff after failures
and a sane request budget live in how you drive it, and a clean exit lives under it.
The browser's job is to make each request real; keeping the requests few and
well-spaced is yours.

## Short answers to the questions that lead here

**Will a stealth browser stop my agent from being rate limited?** No. Rate limits
count requests; they never inspect the browser. A real-looking fingerprint helps
with detection, not with volume.

**Why does my agent get blocked when doing the same thing by hand works?** Almost
always because the agent sent many more requests, much faster, than you did.
Retries, re-reads and reloads multiply traffic a person never generates.

**Does AIHawk retry forever?** No. One instruction is capped at 25 model turns by
default and then stops with a plain message. But the cap is a stop, not a throttle:
re-issuing the same instruction immediately is still a retry loop, just with you in
it.

**Where should backoff live?** In whatever decides when tasks run: your habits at
the prompt, or the script wrapping the one-shot run. No browser setting paces a loop
that was told to try until it succeeds.

**Is a per-account quota a fingerprint problem?** No. A quota is counted against the
account, not the browser, so a better fingerprint does nothing for it. Budget the
actions instead.

**How many requests per minute is safe?** There is no universal number; it depends
on the site. The safe habit is a budget per task, backoff on failure, and never an
immediate identical re-run.

## Sources

- AIHawk's own source, read 2026-09-03: `src/aihawk/agent.py` (the 25-turn default
  ceiling and its stop message, tool errors fed back to the model as results, the
  one-action-at-a-time system prompt) and `src/aihawk/link.py` (one instruction at a
  time on one browser).
- The engine wiki's
  [rate limiting mechanics](https://github.com/feder-cr/invisible_playwright/wiki/how-to-rate-limit-your-scraper-playwright)
  and its notes on
  [handling 403 and 429 with backoff](https://github.com/feder-cr/invisible_playwright/wiki/how-to-handle-403-429-backoff-mid-scrape-playwright),
  which document the same volume signal at the scraping layer.

**See also:** [the timing signal AI agents give off](ai-agent-timing-signal.md) for
the shape of the traffic rather than its amount,
[why does my AI agent get blocked?](why-does-my-ai-agent-get-blocked.md) for the
layer-by-layer sort, and
[browser-use getting blocked](browser-use-getting-blocked.md) for the same split in
another agent framework.

---

*Written while maintaining [AIHawk](https://github.com/feder-cr/AIHawk), an AI agent
on a Firefox patched at the C++ level. The first velocity flag I ever chased was
raised by our own test harness hammering one endpoint from one address - the browser
was innocent, the loop was not.*
