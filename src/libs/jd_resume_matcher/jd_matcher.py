"""
JD Resume Matcher — picks the best-matching resume for a given JD,
tailors it using Claude, and outputs HTML + PDF.

Configuration is read from data_folder/jd_matcher_config.yaml.
Copy data_folder_example/jd_matcher_config.yaml as a starting point.

Exposes two entry points:
  - run_jd_match(api_key)              → interactive CLI flow
  - tailor_resume_for_jd(...)          → programmatic, no prompts (used by the auto-apply bot)
"""
import subprocess
from pathlib import Path
from typing import Optional
from anthropic import Anthropic
from src.logging import logger
from src.utils.resume_reviewer import review_resume_pdf

_CONFIG_PATH = Path("data_folder/jd_matcher_config.yaml")
_config_cache: dict = {}

RESUME_DESCRIPTIONS = {
    "AIDataEngineer": "Best for roles emphasising LLM pipelines, GenAI, AI infrastructure, MLOps with AI focus",
    "DataandMLEngineer": "Best for roles requiring both ML lifecycle (training, evaluation, productionization) and data engineering",
    "LeadDataEngineer": "Best for roles requiring technical ownership, cross-functional leadership, architecture authority, staff/lead level",
    "SeniorDataEngineer": "Best for roles focused on Spark, pipelines, data platforms, cloud migration, streaming",
}


def _load_config() -> dict:
    """Load jd_matcher_config.yaml once and cache it."""
    global _config_cache
    if not _config_cache:
        import yaml
        if not _CONFIG_PATH.exists():
            raise FileNotFoundError(
                f"JD Matcher config not found at {_CONFIG_PATH}. "
                f"Copy data_folder_example/jd_matcher_config.yaml to {_CONFIG_PATH} and fill in your paths."
            )
        with open(_CONFIG_PATH, "r") as f:
            _config_cache = yaml.safe_load(f) or {}
    return _config_cache


def _get_resumes_dir() -> Path:
    return Path(_load_config()["resumes_dir"])


def _get_output_base_dir() -> Path:
    return Path(_load_config()["output_base_dir"])


def _get_chrome_bin() -> str:
    return _load_config().get("chrome_bin", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")


def _get_candidate_name() -> str:
    return _load_config().get("candidate_name", "Candidate")


def _get_resume_files() -> dict:
    cfg = _load_config()
    resumes_dir = Path(cfg["resumes_dir"])
    return {key: resumes_dir / filename for key, filename in cfg["resume_files"].items()}


def _output_stem() -> str:
    """Filename-safe candidate name for output files, e.g. 'Jane_Smith'."""
    return _get_candidate_name().replace(" ", "_")


def _strip_html(html: str) -> str:
    """Strip HTML tags and collapse whitespace — turns ~8k token HTML into ~1.5k token text."""
    import re
    text = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


_RESUME_CACHE: dict = {}  # loaded once per process, reused for every job


def _load_all_resumes() -> dict:
    """Load all resumes from disk — cached after the first call."""
    global _RESUME_CACHE
    if not _RESUME_CACHE:
        for key, path in _get_resume_files().items():
            with open(path, "r", encoding="utf-8") as f:
                _RESUME_CACHE[key] = f.read()
        logger.info("Resumes loaded into cache (will not re-read from disk this session)")
    return _RESUME_CACHE


def _html_to_pdf(html_path: Path, pdf_path: Path) -> bool:
    cmd = [
        _get_chrome_bin(), "--headless", "--disable-gpu", "--no-sandbox",
        f"--print-to-pdf={pdf_path}", "--print-to-pdf-no-header",
        f"file://{html_path}",
    ]
    subprocess.run(cmd, capture_output=True, timeout=30)
    return pdf_path.exists()


def _fetch_jd_from_url(url: str) -> str:
    """Fetch JD text from a URL using headless Chrome."""
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    import time

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()), options=options
    )
    try:
        driver.get(url)
        time.sleep(3)
        return driver.find_element("tag name", "body").text[:8000]
    finally:
        driver.quit()


def _analyse_jd(client: Anthropic, jd_text: str, resumes: dict) -> tuple[str, str, str, str]:
    """
    Ask Claude to pick the best resume and do a gap analysis.
    Returns: (selected_key, company_name, coverage, analysis_text)
    Uses Haiku + stripped text (not full HTML) to minimise token cost.
    """
    candidate_name = _get_candidate_name()
    resume_files = _get_resume_files()

    resume_summary = "\n\n".join([
        f"=== RESUME: {key} ===\n{RESUME_DESCRIPTIONS[key]}\n{_strip_html(html)[:2000]}"
        for key, html in resumes.items()
    ])

    prompt = f"""You are an expert resume consultant. Select the best base resume for this job and do a gap analysis.

Candidate: {candidate_name}
{len(resumes)} resume variants (same candidate, different positioning):

{resume_summary}

JOB DESCRIPTION:
{jd_text[:3000]}

Tasks:
1. Select which resume is the best base ({', '.join(resume_files.keys())})
2. List top 5 matching bullets
3. List bullets from other resumes to pull in
4. List skills gaps
5. List specific changes needed

End your response with EXACTLY these 3 lines:
SELECTED_RESUME: <{"|".join(resume_files.keys())}>
COMPANY: <company name, no punctuation>
COVERAGE: <0-100%>"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",  # Haiku: 20x cheaper than Sonnet for selection
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )
    analysis_text = response.content[0].text

    selected_key = next(iter(resume_files))
    company_name = "Unknown_Company"
    coverage = "N/A"
    for line in analysis_text.splitlines():
        line = line.strip()
        if line.startswith("SELECTED_RESUME:"):
            val = line.replace("SELECTED_RESUME:", "").strip()
            if val in resume_files:
                selected_key = val
        elif line.startswith("COMPANY:"):
            raw = line.replace("COMPANY:", "").strip()
            company_name = raw.replace(" ", "_").replace("/", "_") or "Unknown_Company"
        elif line.startswith("COVERAGE:"):
            coverage = line.replace("COVERAGE:", "").strip()

    return selected_key, company_name, coverage, analysis_text


def _generate_tailored_html(client: Anthropic, jd_text: str, resumes: dict,
                             selected_key: str, analysis_text: str) -> str:
    """
    Ask Claude Sonnet to generate the tailored HTML resume.
    Sends full HTML only for the selected base resume.
    Other resumes sent as stripped text (reference for bullet pulling) to save tokens.
    """
    candidate_name = _get_candidate_name()

    other_resumes_text = "\n\n".join([
        f"--- {key} (stripped text, for bullet reference) ---\n{_strip_html(html)[:1500]}"
        for key, html in resumes.items() if key != selected_key
    ])

    prompt = f"""You are an expert resume writer. Create a tailored HTML resume for {candidate_name}.

BASE RESUME — keep its exact HTML/CSS structure:
{resumes[selected_key]}

OTHER RESUMES (text only — pull better bullets from these where they match the JD):
{other_resumes_text}

JOB DESCRIPTION:
{jd_text[:3000]}

CHANGES TO MAKE:
{analysis_text[:1500]}

INSTRUCTIONS:
1. Keep the base resume's exact HTML and CSS structure
2. Update the summary to mirror the JD's language and priorities
3. Reorder/rewrite bullets to front-load JD-relevant experience
4. Pull stronger bullets from other resumes where they better match the JD
5. Add missing skills/keywords from the JD to the skills section
6. Remove or deprioritise bullets irrelevant to this role
7. Do NOT use the JD's exact role title in the header
8. Do NOT fabricate any experience, metrics, or skills not in the existing resumes
9. Return ONLY the complete HTML — no explanation, no markdown fences"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=5000,
        messages=[{"role": "user", "content": prompt}],
    )
    html = response.content[0].text.strip()

    if html.startswith("```"):
        lines = html.split("\n")
        html = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    return html


def _build_cover_letter_profile(resume_data: dict) -> str:
    """Build a profile summary string for cover letter prompts from plain_text_resume.yaml data."""
    pi = resume_data.get("personal_information", {})
    name = f"{pi.get('name', '')} {pi.get('surname', '')}".strip()
    city = pi.get("city", "")
    country = pi.get("country", "")
    location = ", ".join(p for p in [city, country] if p)

    exp_list = resume_data.get("experience_details", [])
    current_role = ""
    if exp_list:
        e = exp_list[0]
        pos = e.get("position", "")
        comp = e.get("company", "")
        period = e.get("employment_period", "")
        current_role = f"{pos} at {comp} ({period})".strip()

    all_skills = []
    for exp in exp_list:
        all_skills.extend(exp.get("skills_acquired", []))
    skills = ", ".join(dict.fromkeys(all_skills))

    edu_list = resume_data.get("education_details", [])
    education = ""
    if edu_list:
        e = edu_list[0]
        education = f"{e.get('education_level', '')} in {e.get('field_of_study', '')}, {e.get('institution', '')}".strip(", ")

    legal = resume_data.get("legal_authorization", {})
    auth_parts = []
    for region, key in [("EU", "eu_work_authorization"), ("US", "us_work_authorization"),
                        ("UK", "uk_work_authorization"), ("Canada", "canada_work_authorization")]:
        if str(legal.get(key, "")).lower() == "yes":
            auth_parts.append(region)
    visa = f"Authorized to work in: {', '.join(auth_parts)}" if auth_parts else ""

    lines = [
        f"Candidate: {name}",
        f"Location: {location}",
        f"Current role: {current_role}",
        f"Skills: {skills}",
        f"Education: {education}",
        f"Work authorization: {visa}",
    ]
    return "\n".join(line for line in lines if line.split(": ", 1)[-1].strip())


def tailor_resume_for_jd(api_key: str, jd_text: str, company_name: str = None) -> Optional[Path]:
    """
    Programmatic entry point — no user prompts.
    Picks the best resume, tailors it for the JD, saves HTML + PDF.
    Returns the Path to the generated PDF, or None on failure.
    """
    client = Anthropic(api_key=api_key)
    stem = _output_stem()

    try:
        resumes = _load_all_resumes()
    except Exception as e:
        logger.error(f"Failed to load resumes: {e}")
        return None

    try:
        selected_key, detected_company, coverage, analysis_text = _analyse_jd(client, jd_text, resumes)
    except Exception as e:
        logger.error(f"JD analysis failed: {e}")
        return None

    folder_name = (company_name or detected_company).replace(" ", "_").replace("/", "_") or "Unknown_Company"
    logger.info(f"Selected resume: {selected_key} | Company: {folder_name} | Coverage: {coverage}")

    try:
        tailored_html = _generate_tailored_html(client, jd_text, resumes, selected_key, analysis_text)
    except Exception as e:
        logger.error(f"Resume generation failed: {e}")
        return None

    output_dir = _get_output_base_dir() / folder_name
    output_dir.mkdir(parents=True, exist_ok=True)

    html_path = output_dir / f"{stem}_Resume.html"
    pdf_path = output_dir / f"{stem}_Resume.pdf"

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(tailored_html)

    if _html_to_pdf(html_path, pdf_path):
        logger.info(f"Tailored resume saved: {pdf_path}")
        review_resume_pdf(pdf_path, html_path=html_path, auto_fix=True)
        notes_path = output_dir / "review_notes.md"
        with open(notes_path, "w", encoding="utf-8") as f:
            f.write(f"# Resume Tailoring — {folder_name}\n\n"
                    f"**Base resume:** {selected_key}\n"
                    f"**Coverage:** {coverage}\n\n"
                    f"## Analysis\n{analysis_text}\n")
        return pdf_path
    else:
        logger.warning("PDF conversion failed — returning HTML path instead")
        return html_path


def generate_cover_letter_for_jd(api_key: str, jd_text: str, company_name: str,
                                  job_title: str, output_dir: Path = None,
                                  resume_data: dict = None) -> Optional[str]:
    """
    Generate a personalized cover letter for the given JD.
    Returns the cover letter text (suitable for pasting into a form textarea).
    Optionally saves to output_dir/cover_letter.txt.

    resume_data: full dict from plain_text_resume.yaml — used to build the candidate profile.
                 If omitted, falls back to data_folder/plain_text_resume.yaml.
    """
    client = Anthropic(api_key=api_key)
    candidate_name = _get_candidate_name()

    if resume_data is None:
        import yaml
        resume_yaml = Path("data_folder/plain_text_resume.yaml")
        if resume_yaml.exists():
            with open(resume_yaml, "r") as f:
                resume_data = yaml.safe_load(f) or {}
        else:
            resume_data = {}

    profile_summary = _build_cover_letter_profile(resume_data)

    prompt = f"""Write a professional, specific cover letter for {candidate_name} applying to this role.

CANDIDATE PROFILE:
{profile_summary}

JOB DESCRIPTION:
{jd_text[:3000]}

COMPANY: {company_name}
ROLE: {job_title}

RULES:
- 3 short paragraphs, 200-250 words total
- Paragraph 1: Reference the specific role and ONE specific detail about the company or JD — no generic opener
- Paragraph 2: Connect 2-3 of the candidate's most relevant achievements directly to what the JD asks for — use numbers and be specific
- Paragraph 3: Brief closing — genuine interest, invite a conversation
- Tone: direct and confident — NOT corporate boilerplate
- Do NOT start with "I am writing to apply for..."
- Do NOT use "passionate", "dynamic", "synergy", or similar buzzwords
- Return only the letter body — no subject line, no greeting, no sign-off"""

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text.strip()

        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            cl_path = output_dir / "cover_letter.txt"
            with open(cl_path, "w", encoding="utf-8") as f:
                f.write(text)
            logger.info(f"Cover letter saved: {cl_path}")

        return text
    except Exception as e:
        logger.error(f"Cover letter generation failed: {e}")
        return None


def run_jd_match(api_key: str):
    """Interactive CLI entry point — asks for URL, shows analysis, confirms before generating."""
    client = Anthropic(api_key=api_key)
    stem = _output_stem()

    print("\n" + "=" * 60)
    print("  JD Resume Matcher — Powered by Claude")
    print("=" * 60)
    print("\nEnter the job URL (LinkedIn, Workday, Greenhouse, etc.):\n")

    url = input("Job URL: ").strip()
    if not url or not url.startswith("http"):
        print("Invalid URL. Exiting.")
        return

    print(f"\nFetching JD from: {url}")
    jd_text = _fetch_jd_from_url(url)
    if not jd_text.strip():
        print("Could not fetch JD content. Exiting.")
        return
    print(f"JD fetched ({len(jd_text)} chars).")

    print("\nReading all resumes...")
    try:
        resumes = _load_all_resumes()
    except Exception as e:
        print(f"ERROR reading resumes: {e}")
        return

    print("Analysing JD and selecting best resume...\n")
    try:
        selected_key, company_name, coverage, analysis_text = _analyse_jd(client, jd_text, resumes)
    except Exception as e:
        print(f"ERROR calling Claude API: {e}")
        return

    print(analysis_text)
    print("\n" + "=" * 60)
    print(f"Selected resume: {selected_key}")
    print(f"Company: {company_name}")
    print(f"Coverage: {coverage}")

    confirm = input("\nShould I go ahead and create the tailored resume? (yes/no): ").strip().lower()
    if confirm not in ("yes", "y"):
        print("Cancelled.")
        return

    print("\nGenerating tailored resume...")
    try:
        tailored_html = _generate_tailored_html(client, jd_text, resumes, selected_key, analysis_text)
    except Exception as e:
        print(f"ERROR generating resume: {e}")
        return

    output_dir = _get_output_base_dir() / company_name
    output_dir.mkdir(parents=True, exist_ok=True)
    html_path = output_dir / f"{stem}_Resume.html"
    pdf_path = output_dir / f"{stem}_Resume.pdf"

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(tailored_html)
    print(f"HTML saved: {html_path}")

    print("Converting to PDF...")
    if _html_to_pdf(html_path, pdf_path):
        print(f"PDF saved: {pdf_path} ({pdf_path.stat().st_size // 1024} KB)")
        review_resume_pdf(pdf_path, html_path=html_path, auto_fix=True)
    else:
        print("PDF conversion failed. Open the HTML in Chrome and print manually.")

    notes_path = output_dir / "review_notes.md"
    with open(notes_path, "w", encoding="utf-8") as f:
        f.write(f"# Resume Tailoring — {company_name}\n\n"
                f"**Base resume:** {selected_key}\n"
                f"**Coverage:** {coverage}\n\n"
                f"## Analysis\n{analysis_text}\n")
    print(f"Review notes: {notes_path}")
    print(f"\nDone! Files saved to: {output_dir}")
