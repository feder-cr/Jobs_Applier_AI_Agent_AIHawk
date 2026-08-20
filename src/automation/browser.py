"""Playwright browser lifecycle manager with cookie persistence."""
from __future__ import annotations

import json
from pathlib import Path

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright

from src.logging import logger

COOKIES_DIR = Path("data_folder/cookies")


class BrowserManager:
    """Manages a single persistent Playwright Chromium browser instance.

    Supports per-platform cookie persistence so users stay logged in
    across bot runs without re-entering credentials each time.
    """

    def __init__(self, headless: bool = True):
        self.headless = headless
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None

    async def launch(self) -> BrowserContext:
        """Start Playwright and launch a Chromium browser context."""
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
            ],
        )
        self._context = await self._browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            java_script_enabled=True,
            locale="en-US",
        )
        # Hide automation fingerprint
        await self._context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        logger.info("Playwright browser launched (headless={})", self.headless)
        return self._context

    async def new_page(self) -> Page:
        """Open a new page in the current context."""
        if self._context is None:
            await self.launch()
        return await self._context.new_page()

    async def save_cookies(self, platform: str) -> None:
        """Persist current browser cookies for a platform."""
        if self._context is None:
            return
        COOKIES_DIR.mkdir(parents=True, exist_ok=True)
        cookies = await self._context.cookies()
        path = COOKIES_DIR / f"{platform}.json"
        path.write_text(json.dumps(cookies, indent=2))
        logger.info("Saved {} cookies for {}", len(cookies), platform)

    async def load_cookies(self, platform: str) -> bool:
        """Restore saved cookies for a platform. Returns True if found."""
        path = COOKIES_DIR / f"{platform}.json"
        if not path.exists():
            return False
        if self._context is None:
            await self.launch()
        try:
            cookies = json.loads(path.read_text())
            await self._context.add_cookies(cookies)
            logger.info("Loaded {} saved cookies for {}", len(cookies), platform)
            return True
        except Exception as exc:
            logger.warning("Could not load cookies for {}: {}", platform, exc)
            return False

    async def clear_cookies(self, platform: str) -> None:
        """Delete saved cookie file for a platform."""
        path = COOKIES_DIR / f"{platform}.json"
        if path.exists():
            path.unlink()

    async def close(self) -> None:
        """Shut down the browser and Playwright."""
        try:
            if self._context:
                await self._context.close()
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()
        except Exception as exc:
            logger.warning("Error closing browser: {}", exc)
        finally:
            self._context = None
            self._browser = None
            self._playwright = None
