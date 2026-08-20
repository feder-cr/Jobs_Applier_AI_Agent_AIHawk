"""ZipRecruiter 1-click Apply platform handler using Playwright."""
from __future__ import annotations

import urllib.parse
from typing import Any

from playwright.async_api import Page, TimeoutError as PWTimeout

from src.automation.platforms.base import BasePlatform, JobListing, ApplyResult
from src.logging import logger


class ZipRecruiterPlatform(BasePlatform):
    """ZipRecruiter job search and 1-click apply automation."""

    LOGIN_URL = "https://www.ziprecruiter.com/login"
    JOBS_BASE = "https://www.ziprecruiter.com/jobs-search"

    async def login(self, page: Page, credentials: dict, browser_manager=None) -> bool:
        email = credentials.get("email", "")
        password = credentials.get("password", "")
        if not email or not password:
            logger.warning("ZipRecruiter credentials missing.")
            return False

        await page.goto(self.LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
        await self._human_delay(1, 2)
        try:
            await page.fill("input[name='email']", email)
            await self._human_delay(0.5, 1.0)
            await page.fill("input[name='password']", password)
            await self._human_delay(0.5, 1.0)
            await page.click("button[type='submit']")
            await self._human_delay(3, 5)
        except Exception as exc:
            logger.error("ZipRecruiter login error: {}", exc)
            return False

        return "ziprecruiter.com" in page.url and "login" not in page.url

    async def search_jobs(self, page: Page, preferences: dict[str, Any]) -> list[JobListing]:
        positions = preferences.get("positions", [])
        locations = preferences.get("locations", [])
        if not positions or not locations:
            return []

        jobs: list[JobListing] = []
        blacklisted_companies = {c.lower() for c in preferences.get("company_blacklist", [])}
        blacklisted_titles = {t.lower() for t in preferences.get("title_blacklist", [])}

        for position in positions:
            for location in locations:
                params = {"search": position, "location": location}
                url = self.JOBS_BASE + "?" + urllib.parse.urlencode(params)
                logger.info("ZipRecruiter search: {} in {}", position, location)

                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await self._human_delay(2, 4)

                cards = await page.query_selector_all("article.job_result")
                for card in cards:
                    try:
                        title_el = await card.query_selector("h2.job_title a")
                        company_el = await card.query_selector("a.job_company_name")
                        location_el = await card.query_selector(".location")

                        title = (await title_el.text_content() if title_el else "").strip()
                        company = (await company_el.text_content() if company_el else "").strip()
                        loc = (await location_el.text_content() if location_el else "").strip()
                        href = await title_el.get_attribute("href") if title_el else ""
                        link = f"https://www.ziprecruiter.com{href}" if href and not href.startswith("http") else href

                        if not title or not link:
                            continue
                        if company.lower() in blacklisted_companies:
                            continue
                        if any(w in title.lower() for w in blacklisted_titles):
                            continue

                        jobs.append(JobListing(
                            title=title,
                            company=company,
                            location=loc,
                            url=link,
                            platform="ziprecruiter",
                            apply_method="1_click",
                        ))
                    except Exception as exc:
                        logger.debug("ZipRecruiter card parse error: {}", exc)

        seen: set[str] = set()
        unique = []
        for j in jobs:
            if j.url not in seen:
                seen.add(j.url)
                unique.append(j)
        logger.info("ZipRecruiter: {} unique jobs found.", len(unique))
        return unique

    async def apply_to_job(
        self,
        page: Page,
        job: JobListing | dict,
        resume_path: str = "",
        cover_letter_path: str = "",
    ) -> ApplyResult:
        url = job.get("url", "") if isinstance(job, dict) else job.url
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await self._human_delay(2, 3)

            apply_btn = await page.query_selector(
                "button.apply_button, button:has-text('1-Click Apply'), button:has-text('Apply Now')"
            )
            if not apply_btn:
                return ApplyResult(skipped=True, reason="no apply button")

            await apply_btn.click()
            await self._human_delay(2, 4)

            # 1-click apply may show a confirmation dialog
            confirm = await page.query_selector(
                "button:has-text('Confirm'), button:has-text('Submit')"
            )
            if confirm:
                await confirm.click()
                await self._human_delay(1, 2)
                return ApplyResult(success=True)

            # Multi-step flow
            for _ in range(5):
                await self._human_delay(1, 2)
                submit = await page.query_selector("button:has-text('Submit')")
                if submit:
                    await submit.click()
                    return ApplyResult(success=True)
                cont = await page.query_selector("button:has-text('Continue'), button:has-text('Next')")
                if cont:
                    await cont.click()
                    continue
                break

            return ApplyResult(skipped=True, reason="could not complete flow")
        except PWTimeout:
            return ApplyResult(reason="timeout")
        except Exception as exc:
            logger.error("ZipRecruiter apply error: {}", exc)
            return ApplyResult(reason=str(exc))
