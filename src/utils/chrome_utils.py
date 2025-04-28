import base64
from playwright.sync_api import sync_playwright
from src.logging import logger

def fetch_page_html(url: str) -> str:
    """Return full HTML of the page using Playwright headless Chromium."""
    logger.debug("Fetching job page with Playwright: %s", url)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="load")
        html = page.content()
        browser.close()
    return html


def HTML_to_PDF(html_content: str) -> str:
    """
    Render HTML to PDF (A4) with Playwright and return a base-64 string.
    """
    if not isinstance(html_content, str) or not html_content.strip():
        raise ValueError("HTML content must be a non-empty string")

    logger.debug("Rendering HTML to PDF with Playwright (no external Chrome)")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content(html_content, wait_until="load")
        pdf_bytes = page.pdf(
            format="A4",
            margin={"top": "20mm", "bottom": "20mm", "left": "12mm", "right": "12mm"},
            print_background=True,
        )
        browser.close()

    return base64.b64encode(pdf_bytes).decode()
