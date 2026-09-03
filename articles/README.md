# Articles

Guides on using AIHawk, with worked examples and recordings. Empty for now.

One article per folder, so the piece and the things it references travel
together:

```
src/article/
  extracting-a-listing-to-csv/
    README.md
    demo.mp4
    screenshots/
```

## What makes one worth publishing

**A prompt somebody can paste, and the result it actually produced.** Not a
paraphrase of what it would do. If the run took four tries to get right, the
article is more useful with the four tries in it than with a clean one that
never happened.

**A recording of the run, not a diagram of it.** The thing worth showing is the
browser doing the work while the transcript narrates.

**The version it was recorded against.** These pieces go stale: the tool names
and the shape of the responses change between releases, and a reader who cannot
tell which version they are looking at cannot tell whether the difference is
theirs or ours.

## Two rules that are not style

**Site names are for subjects, not examples.** A mainstream platform may be
the declared subject of a guide - a piece about automating a specific site,
written in the open, honest about what that site's terms say and what the
reader risks. What stays out is the other thing: naming sites incidentally as
the targets your demo happens to run against, which turns a guide into a
target list. For demos and recordings, `books.toscrape.com` exists for exactly
this and is fair game; otherwise use a page you serve yourself. A guide about
a named site never includes instructions aimed at defeating that specific
site's protections.

**No proxy providers, and no credentials.** Not in a config block, not in a URL
in a screenshot, not in a terminal recording. A recording is the easiest place
to leak one, because nobody re-reads a video before publishing.

And read a screenshot before it ships. A grep cannot clear a PNG, and a
fingerprint or detector page paints the real IP, timezone and locale straight
into the pixels.
