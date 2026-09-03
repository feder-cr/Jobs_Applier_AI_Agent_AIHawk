"""The README offers BOTH ways in, and offers them first.

⛔ THE REQUIREMENT IS ABOUT POSITION, NOT PRESENCE, which is why this file exists
instead of a grep. There are two ways to use this product and only one real
question behind them - where the model comes from:

  1. you already have an MCP client with a model in it (Claude Code, Claude
     Desktop, Cursor), and this browser arrives there as tools;
  2. you have no client, and our interface brings a model with an OpenRouter key.

Both were already documented before this test was written. The MCP server named
the interface at line 140 of 161, under a heading that reads like a footnote, and
the interface named the MCP path at line 114 of 159 under "Already have an MCP
client? Then you may not need this at all". A reader who stopped at the first
screen - which is most readers - saw one option and concluded it was the only one.

So the assertion is that the offer sits in the FIRST section that is not the
title, and that both commands are inside it. A README that mentions both paths
somewhere passes a grep and fails the requirement.
"""
from __future__ import annotations

import pathlib
import re

import pytest

README = pathlib.Path(__file__).resolve().parents[1] / "README.md"

#: The literal command for each path. Literal on purpose: this is what a reader
#: copies, and a paraphrase in the README is not a way in.
MCP_WAY = "uvx invisible-playwright-mcp"
UI_WAY = "uvx aihawk ui"


def _sections():
    """(heading, body) pairs, in order. The lead-in before the first heading is
    returned under an empty heading, because a logo block is not a section."""
    text = README.read_text(encoding="utf-8")
    parts = re.split(r"^(#{1,3} .*)$", text, flags=re.M)
    out = [("", parts[0])]
    for i in range(1, len(parts), 2):
        out.append((parts[i].strip(), parts[i + 1]))
    return out


def test_the_sections_parse():
    """Otherwise everything below passes on an empty list."""
    sections = _sections()
    assert len(sections) > 3, "only %d sections parsed; the regex is wrong" % len(sections)
    assert any(h for h, _ in sections), "no headings found at all"


def test_both_ways_in_are_offered():
    text = README.read_text(encoding="utf-8")
    for way in (MCP_WAY, UI_WAY):
        assert way in text, (
            "the README never shows `%s`, so one of the two ways to use this is "
            "missing entirely" % way)


def test_the_offer_comes_before_anything_else():
    """Both commands in the first real section, not scattered down the page.

    The tolerance is two headings, not one, because a page may open with its own
    title before the choice. Three would let the offer sit behind a features
    section, which is where it was.
    """
    sections = _sections()
    found = {}
    for index, (heading, body) in enumerate(sections):
        for name, way in (("mcp", MCP_WAY), ("ui", UI_WAY)):
            if way in body and name not in found:
                found[name] = (index, heading)

    assert set(found) == {"mcp", "ui"}, "missing: %s" % sorted({"mcp", "ui"} - set(found))

    late = {n: h for n, (i, h) in found.items() if i > 2}
    assert not late, (
        "these ways in are offered too far down to be found: %s. The reader who "
        "stops at the first screen must see both." % late)

    # And in the SAME section, so they read as a choice rather than as two
    # unrelated facts a reader has to notice and compare for themselves.
    assert found["mcp"][0] == found["ui"][0], (
        "the two ways are in different sections (%r and %r), so nothing on the "
        "page says they are alternatives" % (found["mcp"][1], found["ui"][1]))


def test_the_offer_says_what_each_one_costs_the_reader():
    """A choice with no basis for choosing is not a choice.

    What distinguishes the two is where the model comes from: a client you
    already pay for, or an OpenRouter key. If neither is named next to the
    commands, the reader has to try one to find out.
    """
    sections = _sections()
    body = next(b for _, b in sections if MCP_WAY in b)
    low = body.lower()
    assert "openrouter" in low, (
        "the choice does not mention OpenRouter, so nothing says what the second "
        "way needs from the reader")
    assert any(c in low for c in ("claude", "cursor")), (
        "the choice does not name a single MCP client, so nothing says who the "
        "first way is for")


def test_no_tool_name_that_does_not_exist():
    """Any tool the README names has to be real.

    Cheaper than keeping a list in sync and it never goes stale: it constrains
    what may be SAID rather than requiring the page to say everything.
    """
    import asyncio

    try:
        from invisible_playwright_mcp import server
    except ImportError:  # pragma: no cover
        pytest.skip("invisible-playwright-mcp is not installed")

    real = {t.name for t in asyncio.run(server.mcp.list_tools())}
    named = set(re.findall(r"`((?:browser|session)_\w+)`",
                           README.read_text(encoding="utf-8")))
    assert not named - real, (
        "the README names tools that do not exist: %s" % sorted(named - real))


def test_no_hand_written_count_of_tools():
    """"the fourteen tools" was written into six files and a test literal, so
    every new tool was an edit in a place nobody remembers. A count in prose is
    a fact with two homes."""
    text = README.read_text(encoding="utf-8").lower()
    bad = re.findall(r"\b(?:eleven|twelve|thirteen|fourteen|fifteen|sixteen|"
                     r"seventeen|eighteen|nineteen|twenty|\d{1,3})\s+tools\b", text)
    assert not bad, "the README writes a tool count in prose: %s" % bad
