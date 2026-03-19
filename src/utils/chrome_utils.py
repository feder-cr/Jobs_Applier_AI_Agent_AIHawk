import urllib
from playwright.sync_api import sync_playwright
from src.logging import logger

_playwright = None
_browser = None


def _get_browser():
    """Get or create a shared Playwright browser instance."""
    global _playwright, _browser
    if _browser is None or not _browser.is_connected():
        logger.debug("Launching Playwright Chromium browser")
        _playwright = sync_playwright().start()
        _browser = _playwright.chromium.launch(headless=True)
    return _browser


def init_browser():
    """Initialize and return a new Playwright browser page."""
    try:
        browser = _get_browser()
        page = browser.new_page(viewport={"width": 1200, "height": 800})
        logger.debug("Playwright browser page initialized successfully.")
        return page
    except Exception as e:
        logger.error(f"Failed to initialize browser: {str(e)}")
        raise RuntimeError(f"Failed to initialize browser: {str(e)}")


def HTML_to_PDF(html_content, page):
    """
    Convert an HTML string to PDF and return it as a base64 string.

    :param html_content: HTML string to convert.
    :param page: Playwright page instance.
    :return: Base64 string of the generated PDF.
    """
    import base64

    if not isinstance(html_content, str) or not html_content.strip():
        raise ValueError("HTML content must be a non-empty string.")

    encoded_html = urllib.parse.quote(html_content)
    data_url = f"data:text/html;charset=utf-8,{encoded_html}"

    try:
        page.goto(data_url, wait_until="networkidle")

        pdf_bytes = page.pdf(
            print_background=True,
            landscape=False,
            width="8.27in",
            height="11.69in",
            margin={
                "top": "0.8in",
                "bottom": "0.8in",
                "left": "0.5in",
                "right": "0.5in",
            },
            prefer_css_page_size=True,
        )
        return base64.b64encode(pdf_bytes).decode("utf-8")
    except Exception as e:
        logger.error(f"Playwright PDF generation error: {e}")
        raise RuntimeError(f"Playwright PDF generation error: {e}")
