import os
import pytest
from click.testing import CliRunner
import aihawk.cli as climod

pytestmark = pytest.mark.skipif(
    not (os.environ.get("STEALTHFOX_BINARY") and os.environ.get("OPENROUTER_API_KEY")),
    reason="needs STEALTHFOX_BINARY + OPENROUTER_API_KEY (real browser + LLM)",
)


def test_do_reads_a_data_url_heading():
    r = CliRunner().invoke(climod.main, [
        "do",
        "Open data:text/html,<h1>hello-cli</h1> and tell me the exact text of the h1.",
        "--binary", os.environ["STEALTHFOX_BINARY"],
    ])
    assert r.exit_code == 0, r.output
    assert "hello-cli" in r.output.lower()
