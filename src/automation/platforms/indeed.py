"""Indeed Quick Apply platform handler using Playwright."""
from __future__ import annotations

import urllib.parse
from typing import Any

from playwright.async_api import Page, TimeoutError as PWTimeout

from src.automation.platforms.base import BasePlatform, JobListing, ApplyResult
from src.logging import logger


class IndeedPlatform(BasePlatform):
    """Indeed job search and Quick Apply automation."""

    LOGIN_URL = "https://secure.indeed.com/account/login"
    JOBS_BASE = "https://www.indeed.com/jobs"

    async def login(self, page: Page, credentials: dict, browser_manager=None) -> bool:
        email = credentials.get("email", "")
        password = credentials.get("password", "")
        if not email or not password:
            logger.warning("Indeed credentials missing.")
            return False

        await page.goto(self.LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
        await self._human_delay(1, 2)
        try:
            await page.fill("input[type='email']", email)
            await self._human_delay(0.5, 1.0)
            # Indeed uses a multi-step login
            continue_btn = await page.query_selector("button[type='submit']")
            if continue_btn:
                await continue_btn.click()
            await self._human_delay(1, 2)
            pw_input = await page.query_selector("input[type='password']")
            if pw_input:
                await pw_input.fill(password)
                await self._human_delay(0.5, 1.0)
                submit = await page.query_selector("button[type='submit']")
                if submit:
                    await submit.click()
            await self._human_delay(3, 5)
        except Exception as exc:
            logger.error("Indeed login error: {}", exc)
            return False

        # Verify login by checking URL or profile element
        return "dashboard" in page.url or "indeed.com/myjobs" in page.url or \
               await page.query_selector(".gnav-LoggedInAccountLink") is not None

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
                params = {"q": position, "l": location}
                url = self.JOBS_BASE + "?" + urllib.parse.urlencode(params)
                logger.info("Indeed search: {} in {}", position, location)

                for page_num in range(3):
                    page_url = url + f"&start={page_num * 10}"
                    await page.goto(page_url, wait_until="domcontentloaded", timeout=30000)
                    await self._human_delay(2, 4)

                    cards = await page.query_selector_all(".job_seen_beacon")
                    if not cards:
                        break

                    for card in cards:
                        try:
                            title_el = await card.query_selector("h2.jobTitle a")
                            company_el = await card.query_selector("[data-testid='company-name']")
                            location_el = await card.query_selector("[data-testid='text-location']")

                            title = (await title_el.text_content() if title_el else "").strip()
                            company = (await company_el.text_content() if company_el else "").strip()
                            location_text = (await location_el.text_content() if location_el else "").strip()
                            href = await title_el.get_attribute("href") if title_el else ""
                            link = f"https://www.indeed.com{href}" if href and href.startswith("/") else href

                            if not title or not link:
                                continue
                            if company.lower() in blacklisted_companies:
                                continue
                            if any(w in title.lower() for w in blacklisted_titles):
                                continue

                            jobs.append(JobListing(
                                title=title,
                                company=company,
                                location=location_text,
                                url=link,
                                platform="indeed",
                                apply_method="quick_apply",
                            ))
                        except Exception as exc:
                            logger.debug("Error parsing Indeed job card: {}", exc)
                            continue

        # De-duplicate
        seen: set[str] = set()
        unique: list[JobListing] = []
        for j in jobs:
            if j.url not in seen:
                seen.add(j.url)
                unique.append(j)
        logger.info("Indeed: {} unique jobs found.", len(unique))
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

            # Look for "Apply Now" or "Easily Apply" button
            apply_btn = await page.query_selector(
                "button[id*='indeedApplyButton'], a[id*='indeedApplyButton'], "
                "button:has-text('Apply now'), button:has-text('Easily apply')"
            )
            if not apply_btn:
                return ApplyResult(skipped=True, reason="no apply button found")

            await apply_btn.click()
            await self._human_delay(2, 4)

            # Indeed often opens an iframe for quick apply
            frame = None
            for f in page.frames:
                if "indeed" in f.url and "apply" in f.url:
                    frame = f
                    break

            target = frame or page

            # Upload resume
            if resume_path:
                try:
                    file_input = await target.query_selector("input[type='file']")
                    if file_input:
                        await file_input.set_input_files(resume_path)
                        await self._human_delay(1, 2)
                except Exception as exc:
                    logger.debug("Indeed resume upload error: {}", exc)

            # Click through steps
            for _ in range(8):
                await self._human_delay(1, 2)
                # Submit button
                submit = await target.query_selector(
                    "button[type='submit']:has-text('Submit'), "
                    "button:has-text('Submit your application')"
                )
                if submit:
                    await submit.click()
                    await self._human_delay(2, 3)
                    return ApplyResult(success=True)

                # Continue button
                cont = await target.query_selector(
                    "button[type='submit']:has-text('Continue'), "
                    "button:has-text('Next')"
                )
                if cont:
                    await cont.click()
                    continue

                break

            return ApplyResult(skipped=True, reason="could not complete application flow")

        except PWTimeout:
            return ApplyResult(reason="timeout")
        except Exception as exc:
            logger.error("Indeed apply error: {}", exc)
            return ApplyResult(reason=str(exc))
