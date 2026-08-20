"""Glassdoor Easy Apply platform handler using Playwright."""
from __future__ import annotations

import urllib.parse
from typing import Any

from playwright.async_api import Page, TimeoutError as PWTimeout

from src.automation.platforms.base import BasePlatform, JobListing, ApplyResult
from src.logging import logger


class GlassdoorPlatform(BasePlatform):
    """Glassdoor job search and Easy Apply automation."""

    LOGIN_URL = "https://www.glassdoor.com/profile/login_input.htm"
    JOBS_BASE = "https://www.glassdoor.com/Job/jobs.htm"

    async def login(self, page: Page, credentials: dict, browser_manager=None) -> bool:
        email = credentials.get("email", "")
        password = credentials.get("password", "")
        if not email or not password:
            logger.warning("Glassdoor credentials missing.")
            return False

        await page.goto(self.LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
        await self._human_delay(1, 2)
        try:
            await page.fill("input[name='username']", email)
            await self._human_delay(0.5, 1.0)
            await page.fill("input[name='password']", password)
            await self._human_delay(0.5, 1.0)
            await page.click("button[type='submit']")
            await self._human_delay(3, 5)
        except Exception as exc:
            logger.error("Glassdoor login error: {}", exc)
            return False

        return "glassdoor.com" in page.url and "login" not in page.url

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
                params = {"sc.keyword": position, "locT": "C", "locId": "1", "jobType": ""}
                url = self.JOBS_BASE + "?" + urllib.parse.urlencode(params)
                logger.info("Glassdoor search: {} in {}", position, location)

                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await self._human_delay(2, 4)

                cards = await page.query_selector_all("li.react-job-listing")
                for card in cards:
                    try:
                        title_el = await card.query_selector("[data-test='job-title']")
                        company_el = await card.query_selector("[data-test='employer-short-name']")
                        location_el = await card.query_selector("[data-test='emp-location']")
                        link_el = await card.query_selector("a[data-test='job-link']")

                        title = (await title_el.text_content() if title_el else "").strip()
                        company = (await company_el.text_content() if company_el else "").strip()
                        loc = (await location_el.text_content() if location_el else "").strip()
                        href = await link_el.get_attribute("href") if link_el else ""
                        link = f"https://www.glassdoor.com{href}" if href and not href.startswith("http") else href

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
                            platform="glassdoor",
                            apply_method="easy_apply",
                        ))
                    except Exception as exc:
                        logger.debug("Glassdoor card parse error: {}", exc)

        # De-duplicate
        seen: set[str] = set()
        unique = []
        for j in jobs:
            if j.url not in seen:
                seen.add(j.url)
                unique.append(j)
        logger.info("Glassdoor: {} unique jobs found.", len(unique))
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
                "button[data-test='apply-btn'], button:has-text('Easy Apply'), button:has-text('Apply Now')"
            )
            if not apply_btn:
                return ApplyResult(skipped=True, reason="no apply button")

            await apply_btn.click()
            await self._human_delay(2, 3)

            # Upload resume if we have one
            if resume_path:
                try:
                    file_input = await page.query_selector("input[type='file']")
                    if file_input:
                        await file_input.set_input_files(resume_path)
                        await self._human_delay(1, 2)
                except Exception:
                    pass

            # Click through up to 8 steps
            for _ in range(8):
                await self._human_delay(1, 2)
                submit = await page.query_selector(
                    "button:has-text('Submit Application'), button:has-text('Submit')"
                )
                if submit:
                    await submit.click()
                    await self._human_delay(2, 3)
                    return ApplyResult(success=True)

                cont = await page.query_selector(
                    "button:has-text('Continue'), button:has-text('Next')"
                )
                if cont:
                    await cont.click()
                    continue
                break

            return ApplyResult(skipped=True, reason="could not complete flow")
        except PWTimeout:
            return ApplyResult(reason="timeout")
        except Exception as exc:
            logger.error("Glassdoor apply error: {}", exc)
            return ApplyResult(reason=str(exc))
