---
title: "Using AIHawk without an API key"
description: "What uvx aihawk ui does with no key: the full interface and the real browser on a literal-command placeholder - what each command does, what the mode is for, and the one-line upgrade."
parent: "Using the Agent"
nav_order: 5
---


# Using AIHawk without an API key

`uvx aihawk ui` with no key is not an error state and not a crippled demo. It
starts the full interface and the real stealth browser; the only thing missing
is the model. In its place sits a placeholder that understands a fixed set of
literal commands and no natural language at all, and the startup line says so
plainly: `model    none: literal commands only.` Everything else is the
product - the same browser engine, the same tools, the same live view - which
is exactly what makes the mode useful rather than decorative.

The interface runs keyless because most of what it shows you does not need a
model. Producing answers is the model's half of the product - and if you want
that half without buying a key, the assistant path covers it: since aihawk
0.3.0 the browser attaches to Claude Code, Codex or Gemini CLI over MCP, and
the assistant brings its own model.

## What actually runs

With no key, your typed text goes to the placeholder instead of to a model.
The placeholder does no interpretation: it splits your line into a command and
an argument, makes exactly one browser tool call, and shows you what came
back. The commands, as the source defines them:

- `go <url>` - navigate the page there. The words `open` and `navigate` work
  as synonyms for `go`.
- `read [selector]` - extract the text of the matching element; with no
  selector it reads the whole `body`.
- `click <selector>` - click the matching element.
- `type <selector> <text>` - type the text into the matching element, through
  real key events like everything this browser does.
- `tab` - open a new browser tab.
- `shot` - take a screenshot; the reply points out, correctly, that the view
  on the right is live anyway.

Anything else - including a plain English sentence - gets the help line back:
"I am a placeholder, not a model." That is the entire language. Each command is
one real tool call on the real engine, so what you see the browser do is
exactly what the agent's tools do when a model calls them.

The live pane behaves as it always does: the page view refreshes continuously
while you work, and the address bar and tab strip track the browser. All the
browser options work in this mode too - `--proxy`, `--seed`, `--headed`,
`--binary`, `--profile-dir` - because they configure the engine, not the
model.

## What it is for

**Seeing the interface before deciding anything.** Chat on the left, live
browser on the right, at http://127.0.0.1:8765. Whether this is a tool you
want is answerable in two minutes, for free.

**Testing the browser side on its own.** The engine, your network, a proxy
you are considering, a page you care about: `go` there and `read` what comes
back, with no model behavior mixed into the result. This is the diagnostic
instrument that [browser problem or model problem?](browser-problem-or-model-problem.md)
is built around - a failure that reproduces under literal commands is
guaranteed not to be a model failure, because no model was present.

**Learning the loop's shape cheaply.** A real agent run is the same
observe-act-observe rhythm you are performing by hand: read the page, pick one
action, look at what changed. Driving it manually for ten minutes builds the
right instincts for writing instructions later - including why one clear step
at a time beats a paragraph of ambitions. [The explainer](ai-web-agent-explained.md)
gives the same loop in theory; this is it in your hands.

**Reproducing a bug precisely.** One command, one tool call, one result makes
a report someone can act on. "click #submit returned this error on this page"
beats "the agent got confused" in every way that matters.

## What it deliberately cannot do

The boundary is the model, and everything on the model's side of it is absent:

- **No language.** "Go to the docs and find the install command" is not a
  command, so it gets the help line. The placeholder maps words to tool calls;
  it never decides anything.
- **No multi-step work.** One line is one action. It will not chain, retry,
  or notice that a click failed - noticing is a model behavior.
- **No answers.** It shows you raw page text; it will not extract, summarize,
  compare, or conclude. Producing an answer is the paid half of the product.
- **No one-shot runs.** Since 0.3.0 aihawk has no headless subcommand at all;
  the scripted path runs through an assistant CLI with the browser attached
  over MCP, and there the key question moves to the assistant, not to aihawk.

One cost survives keylessness: the engine itself. The browser, roughly a
quarter of a gigabyte, downloads on the first command that needs a page, even
in placeholder mode. `uvx invisible-playwright fetch` in a terminal gets it
done up front where you can watch it - money is not involved either way, only
bandwidth and patience.

## The one-line upgrade

When you want the real thing, the placeholder is replaced by a model by
supplying an [OpenRouter](https://openrouter.ai) key:

```bash
uvx aihawk ui --openrouter-key sk-or-...
```

or, better, set `OPENROUTER_API_KEY` in the environment - better because a key
on the command line lands in your shell history, and on Linux in the process
list. Nothing else changes: same interface, same browser, same live view, and
your typed sentences now go to a model, `z-ai/glm-4.6` unless you choose
another with `--model`. [Which model to use](which-model-to-use-with-aihawk.md)
covers that choice and what tasks actually cost. The key stays with the model
client: it is stripped from the environment the browser engine starts with, by
name and by value, and the repository carries a test that fails if that stops
being true.

## Short answers to the questions that lead here

**Can I try AIHawk without paying anything?** Yes: `uvx aihawk ui` with no
key runs the full interface and the real browser on a literal-command
placeholder. The only cost is the one-time engine download.

**What commands does the keyless mode understand?** `go` (also `open` or
`navigate`), `read`, `click`, `type`, `tab`, and `shot` - each a single real
browser action. Anything else returns the help line.

**Why does it not understand my sentence?** Because there is no model to
understand it. The placeholder is a command mapper, not a small language
model; language arrives only with a key.

**Is the keyless browser the same one the paid mode uses?** Identical: same
engine, same tools, same options. The key changes what drives the browser,
never the browser.

**Does keyless mode still download the browser?** Yes, on the first command
that needs a page. Run `uvx invisible-playwright fetch` first if you want to
see the download rather than wait through it.

**Why would I use the placeholder after I have a key?** As a diagnostic: a
failure reproduced under literal commands is browser-side with certainty. The
[browser-or-model page](browser-problem-or-model-problem.md) turns that into a
procedure.

## Sources

All retrieved 2026-09-03.

- [feder-cr/AIHawk](https://github.com/feder-cr/AIHawk), this repository's
  source: `src/aihawk/brain.py` (the placeholder, its command set, aliases and
  help line), `src/aihawk/cli.py` (the keyless path, the startup message, the
  browser options applying either way), `src/aihawk/llm.py` (the key
  requirement for `do` and the default model), and the README (the engine
  download, the prefetch command, and the shell-history note).

**See also:** [browser problem or model problem?](browser-problem-or-model-problem.md),
[which model to use with AIHawk](which-model-to-use-with-aihawk.md),
[what is an AI web agent?](ai-web-agent-explained.md), and the rest of
[Using the Agent](guides-using-the-agent.md).

---

*From the [AIHawk](https://github.com/feder-cr/AIHawk) wiki. The placeholder
was built so the interface could be developed and tested without spending on a
model; it ships because that turned out to be worth having every day.*
