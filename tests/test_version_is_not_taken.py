"""The version a change proposes must not already be on the index.

⛔ MEASURED 2026-09-04, AND NOTHING SAW IT. `aihawk 0.4.0` was published at
23:47. Over the following hours main gained two more changes - verbs for the
session tools, and a `.env` plus a raised dependency floor - while `pyproject`
still said `0.4.0`. So main carried content that was not the content of the
0.4.0 on the index, and no test, gate or workflow had an opinion about it.

The way that goes wrong is quiet, which is why it deserves a gate rather than a
habit. `publish.yml` asks the index first and treats an already-present version
as a deliberate no-op:

    200) present=yes
         "aihawk $VERSION is already on the index. No-op, not a failure."

That is correct for a re-pushed or backfilled tag, and it cannot tell that case
apart from somebody forgetting to bump. So the release would have reported
success and shipped nothing, and the next person to look would find the feature
missing from a version that was tagged, released and green.

PULL REQUESTS ONLY, and that is the whole design. A pull request proposes new
content; if its version is already published, that content can never reach
anybody. On main straight after a release the version IS the published one until
somebody bumps, which is a normal resting state and not a defect, so a check
that ran there would be red for a reason nobody can act on - and a gate that is
red at rest is a gate people learn to skip.

The trade this makes, stated rather than discovered: the first pull request
after a release has to carry a version bump. That matches how this repository
already works, since the change that earns a release is the change that bumps.

Enabled by AIHAWK_CHECK_VERSION, which the `version` CI job sets itself, so it
cannot silently skip the way it does in a local run.
"""
from __future__ import annotations

import os
import urllib.error
import urllib.request

import pytest

PACKAGE = "aihawk"

pytestmark = pytest.mark.skipif(
    not os.environ.get("AIHAWK_CHECK_VERSION"),
    reason="set AIHAWK_CHECK_VERSION=1 to ask the index (one network call)",
)


def _declared_version() -> str:
    import pathlib
    import tomllib

    root = pathlib.Path(__file__).resolve().parents[1]
    data = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    return data["project"]["version"]


def _on_the_index(version: str):
    """`True`, `False`, or None when the index would not say.

    ⛔ Three outcomes, not two. A network error is neither present nor absent,
    and scoring it as absent turns an unreachable index into a green gate -
    which is the failure this file exists to prevent, wearing a different hat.
    """
    url = "https://pypi.org/pypi/%s/%s/json" % (PACKAGE, version)
    try:
        with urllib.request.urlopen(url, timeout=20) as answer:
            return answer.status == 200
    except urllib.error.HTTPError as failed:
        if failed.code == 404:
            return False
        return None
    except Exception:
        return None


def test_the_declared_version_is_not_already_published():
    version = _declared_version()
    present = _on_the_index(version)

    if present is None:
        pytest.skip("the index did not answer; neither present nor absent")

    assert not present, (
        "pyproject declares %s and the index already serves it, so a release "
        "from here publishes nothing: publish.yml sees the version, reports "
        "'already on the index. No-op, not a failure', and everything below it "
        "is skipped. Bump the version." % version)


def test_the_check_can_tell_a_taken_version_from_a_free_one():
    """⛔ The known-bad input, run against the live index rather than a mock.

    A check that has only ever said "free" is not a check. `0.1.0` was published
    on 2026-09-02 and is not coming back, so it is a stable stand-in for the
    thing this gate must catch, and a version far past anything real stands in
    for the state it must allow.
    """
    taken = _on_the_index("0.1.0")
    free = _on_the_index("99.99.99")

    if taken is None or free is None:
        pytest.skip("the index did not answer; neither present nor absent")

    assert taken is True, "the check cannot see a version that IS published"
    assert free is False, "the check calls an unpublished version taken"
