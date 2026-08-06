"""LLM-based job fit scorer.

Rates how well a candidate's resume matches a job description on a 1-10
scale. Reuses the existing AIModel abstraction from llm_manager.py.
"""
from __future__ import annotations

import json
import re

from src.logging import logger

SCORE_PROMPT = """You are a job fit evaluator. Given a candidate resume and a job description, score the fit.

SCORING SCALE:
9-10: Perfect match — candidate has direct experience in nearly all required skills.
7-8:  Strong match — candidate has most required skills, minor gaps.
5-6:  Moderate match — some relevant skills but missing key requirements.
3-4:  Weak match — significant skill gaps.
1-2:  Poor match — completely different field or experience level.

IMPORTANT FACTORS:
- Weight technical skills heavily (languages, frameworks, tools)
- Consider transferable experience
- Factor in years of experience vs job requirements
- Consider location/remote preferences

Respond ONLY with valid JSON (no markdown, no extra text):
{"score": <1-10 int>, "keywords": "<comma-separated ATS keywords>", "reason": "<2-3 sentences>"}"""


class JobRanker:
    """Score job listings against the candidate's resume using an LLM."""

    def __init__(self, llm_model, resume_text: str):
        """
        Args:
            llm_model: An instantiated AIModel from src/libs/llm_manager.py
            resume_text: Full text of the candidate's resume
        """
        self._llm = llm_model
        self._resume = resume_text[:8000]  # cap to avoid token overflow

    def score(self, title: str, company: str, description: str) -> dict:
        """Score a job. Returns {"score": int, "keywords": str, "reason": str}."""
        job_text = (
            f"TITLE: {title}\n"
            f"COMPANY: {company}\n\n"
            f"DESCRIPTION:\n{description[:5000]}"
        )
        prompt = (
            f"{SCORE_PROMPT}\n\n"
            f"RESUME:\n{self._resume}\n\n"
            f"---\n\nJOB POSTING:\n{job_text}"
        )
        try:
            response = self._llm.invoke(prompt)
            return self._parse(response)
        except Exception as exc:
            logger.warning("LLM scoring failed for '{}': {}", title, exc)
            return {"score": 0, "keywords": "", "reason": f"Error: {exc}"}

    @staticmethod
    def _parse(response: str) -> dict:
        # Try JSON first
        try:
            # Strip markdown fences if present
            clean = re.sub(r"```(?:json)?|```", "", response).strip()
            data = json.loads(clean)
            score = max(1, min(10, int(data.get("score", 0))))
            return {
                "score": score,
                "keywords": str(data.get("keywords", "")),
                "reason": str(data.get("reason", "")),
            }
        except (json.JSONDecodeError, ValueError, TypeError):
            pass

        # Fallback: regex
        score = 0
        keywords = ""
        reason = response
        for line in response.splitlines():
            line = line.strip()
            if m := re.search(r'"?score"?\s*[:\-]\s*(\d+)', line, re.I):
                try:
                    score = max(1, min(10, int(m.group(1))))
                except ValueError:
                    pass
            if m := re.search(r'"?keywords"?\s*[:\-]\s*(.+)', line, re.I):
                keywords = m.group(1).strip().strip('"')
            if m := re.search(r'"?reason"?\s*[:\-]\s*(.+)', line, re.I):
                reason = m.group(1).strip().strip('"')
        return {"score": score, "keywords": keywords, "reason": reason}
