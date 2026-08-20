"""Universal AI-driven job application handler.

Applies to any career page URL using LLM-guided form filling.
Inspired by ApplyPilot's universal form filling approach.
"""
from __future__ import annotations

import re
from typing import Any

from playwright.async_api import Page, TimeoutError as PWTimeout

from src.automation.platforms.base import BasePlatform, JobListing, ApplyResult
from src.logging import logger


class UniversalPlatform(BasePlatform):
    """Apply to any job page via AI-driven form detection and filling.

    This platform doesn't do its own job search — it processes a list of
    job URLs provided directly in preferences["universal_urls"].
    """

    async def login(self, page: Page, credentials: dict, browser_manager=None) -> bool:
        # Universal platform handles no platform-wide login
        return True

    async def search_jobs(self, page: Page, preferences: dict[str, Any]) -> list[JobListing]:
        """Return jobs from manually-specified URLs in preferences."""
        urls = preferences.get("universal_urls", [])
        jobs: list[JobListing] = []
        for url in urls:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await self._human_delay(1, 2)
            title = await page.title()
            jobs.append(JobListing(
                title=title,
                company="",
                location="",
                url=url,
                platform="universal",
                apply_method="ai_form_fill",
            ))
        return jobs

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

            # Find and click an "Apply" button
            apply_btn = await page.query_selector(
                "button:has-text('Apply'), a:has-text('Apply Now'), "
                "button:has-text('Apply Now'), a:has-text('Apply')"
            )
            if apply_btn:
                await apply_btn.click()
                await self._human_delay(2, 3)

            # Generic form filling loop
            for step in range(10):
                await self._human_delay(1, 2)
                filled = await self._fill_all_inputs(page, resume_path, cover_letter_path)

                # Try to submit
                submit = await page.query_selector(
                    "button[type='submit']:has-text('Submit'), "
                    "button:has-text('Submit Application'), "
                    "input[type='submit']"
                )
                if submit:
                    await submit.click()
                    await self._human_delay(2, 4)
                    return ApplyResult(success=True)

                # Try to advance
                next_btn = await page.query_selector(
                    "button:has-text('Next'), button:has-text('Continue'), "
                    "button[type='submit']:not(:has-text('Submit'))"
                )
                if next_btn:
                    await next_btn.click()
                    continue

                if not filled:
                    break

            return ApplyResult(skipped=True, reason="could not determine form flow")
        except PWTimeout:
            return ApplyResult(reason="timeout")
        except Exception as exc:
            logger.error("Universal apply error for {}: {}", url, exc)
            return ApplyResult(reason=str(exc))

    async def _fill_all_inputs(
        self, page: Page, resume_path: str, cover_letter_path: str
    ) -> bool:
        """Fill all visible, unfilled inputs. Returns True if anything was filled."""
        filled_any = False

        # File inputs
        if resume_path:
            try:
                for fi in await page.query_selector_all("input[type='file']"):
                    label = (await fi.get_attribute("aria-label") or "").lower()
                    if not label or "resume" in label or "cv" in label:
                        await fi.set_input_files(resume_path)
                        await self._human_delay(0.5, 1.0)
                        filled_any = True
                        break
            except Exception:
                pass

        # Text inputs
        try:
            for inp in await page.query_selector_all(
                "input[type='text']:visible, input[type='email']:visible, "
                "input[type='tel']:visible, input[type='number']:visible, textarea:visible"
            ):
                value = (await inp.input_value()).strip()
                if value:
                    continue
                label_text = await self._get_label_text(page, inp)
                answer = await self._answer_with_llm(label_text or "Fill this field")
                await inp.fill(answer[:300])
                await self._human_delay(0.2, 0.5)
                filled_any = True
        except Exception as exc:
            logger.debug("Universal text fill error: {}", exc)

        # Select dropdowns
        try:
            for sel in await page.query_selector_all("select:visible"):
                value = await sel.input_value()
                if value:
                    continue
                options = [
                    (await o.text_content() or "").strip()
                    for o in await sel.query_selector_all("option")
                ]
                label_text = await self._get_label_text(page, sel)
                best = await self._answer_with_llm(label_text or "Select", [o for o in options if o])
                try:
                    await sel.select_option(label=best)
                    filled_any = True
                except Exception:
                    pass
        except Exception as exc:
            logger.debug("Universal select fill error: {}", exc)

        return filled_any

    @staticmethod
    async def _get_label_text(page: Page, element) -> str:
        """Try to find the label text for an input element."""
        try:
            el_id = await element.get_attribute("id")
            if el_id:
                label = await page.query_selector(f"label[for='{el_id}']")
                if label:
                    return (await label.text_content() or "").strip()
        except Exception:
            pass
        try:
            aria = await element.get_attribute("aria-label")
            if aria:
                return aria.strip()
        except Exception:
            pass
        try:
            placeholder = await element.get_attribute("placeholder")
            if placeholder:
                return placeholder.strip()
        except Exception:
            pass
        return ""
