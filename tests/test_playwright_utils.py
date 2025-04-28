import base64
import types
import sys
import importlib
from types import SimpleNamespace

import pytest


# ------------------------------------------------------------------
# Fake Playwright stack (no real browser download / spawn)
# ------------------------------------------------------------------
_PDF_BYTES = b"%PDF-1.4 fake pdf bytes %EOF"
_HTML_STR  = "<html><body>Hello</body></html>"


class _DummyPage:
    def __init__(self):
        self._html = _HTML_STR

    # fetch_page_html
    def goto(self, *_a, **_kw):
        return None

    def content(self):
        return self._html

    # HTML_to_PDF
    def set_content(self, html, **_kw):
        self._html = html

    def pdf(self, **_kw):
        return _PDF_BYTES


class _DummyBrowser:
    def __init__(self):
        self.page = _DummyPage()

    def new_page(self):
        return self.page

    def close(self):
        return None


class _DummyChromium:
    def launch(self, **_kw):
        return _DummyBrowser()


class _PlaywrightCtxMgr:
    def __enter__(self):
        return SimpleNamespace(chromium=_DummyChromium())

    def __exit__(self, exc_type, exc, tb):
        return False  # propagate errors


@pytest.fixture(autouse=True)
def _patch_playwright(monkeypatch):
    """Replace playwright.sync_api.sync_playwright with a dummy impl."""
    dummy_module = types.ModuleType("playwright.sync_api")
    dummy_module.sync_playwright = lambda: _PlaywrightCtxMgr()
    monkeypatch.setitem(sys.modules, "playwright.sync_api", dummy_module)
    yield


def _reload_utils():
    if "src.utils.chrome_utils" in sys.modules:
        del sys.modules["src.utils.chrome_utils"]
    return importlib.import_module("src.utils.chrome_utils")


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------
def test_fetch_page_html_and_html_to_pdf(monkeypatch):
    utils = _reload_utils()

    # fetch_page_html
    html = utils.fetch_page_html("https://example.com")
    assert html == _HTML_STR

    # HTML_to_PDF returns base-64 of _PDF_BYTES
    b64 = utils.HTML_to_PDF("<h1>Hi</h1>")
    assert base64.b64decode(b64) == _PDF_BYTES


def test_html_to_pdf_empty_string(monkeypatch):
    utils = _reload_utils()
    with pytest.raises(ValueError):
        utils.HTML_to_PDF("   ")
