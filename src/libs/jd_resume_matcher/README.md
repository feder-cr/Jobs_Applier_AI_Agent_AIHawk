# JD Resume Matcher

Picks the best-matching resume from a set of pre-written HTML variants,
tailors it for a specific job description using Claude, and outputs HTML + PDF.

## How it works

1. **Select** — Claude Haiku reads a short description of each resume variant
   alongside the job description and picks the best base. Costs ~1k tokens.
2. **Analyse** — Haiku identifies matching bullets, gaps, and changes needed.
3. **Tailor** — Claude Sonnet rewrites the selected resume's HTML to match the
   JD: reorders bullets, pulls stronger ones from other variants, adds missing
   keywords. Only the selected resume is sent in full; others are sent as
   stripped text to minimise token cost.
4. **Output** — Saves the tailored resume as HTML + PDF under
   `output_base_dir/<company_name>/`.

## Setup

### 1. Prerequisites

- An [Anthropic API key](https://console.anthropic.com/)
- Google Chrome installed (used for headless HTML → PDF conversion)
- Your resumes prepared as HTML files (one per variant/positioning)

### 2. Create your config file

Copy the example config and fill in your paths:

```bash
cp data_folder_example/jd_matcher_config.yaml data_folder/jd_matcher_config.yaml
```

`data_folder/jd_matcher_config.yaml` is gitignored — safe to put real paths here.

### 3. Configure `jd_matcher_config.yaml`

```yaml
# Where your HTML resume files live
resumes_dir: "/path/to/your/resumes"

# Where tailored resumes will be saved (one sub-folder per company)
output_base_dir: "/path/to/output/TailoredResumes"

# Path to the Chrome binary (used for HTML → PDF conversion)
chrome_bin: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Your name — used as the output filename prefix
candidate_name: "Jane Smith"

# Your resume variants — key can be anything meaningful to you
resume_files:
  SoftwareEngineer: "JaneSmith_Resume_SoftwareEngineer.html"
  DataEngineer: "JaneSmith_Resume_DataEngineer.html"
  TechLead: "JaneSmith_Resume_TechLead.html"

# One-line description per variant — Claude uses these to pick the best base
resume_descriptions:
  SoftwareEngineer: "Best for full-stack, backend, and product engineering roles"
  DataEngineer: "Best for data pipelines, ETL, Spark, and cloud data platform roles"
  TechLead: "Best for staff/lead roles requiring architecture and cross-team ownership"
```

### 4. Chrome binary path by OS

| OS | Default path |
|----|-------------|
| macOS | `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` |
| Linux | `/usr/bin/google-chrome` |
| Windows | `C:\Program Files\Google\Chrome\Application\chrome.exe` |

## Usage

### Interactive CLI

Run from the project root:

```python
from src.libs.jd_resume_matcher.jd_matcher import run_jd_match

run_jd_match(api_key="your-anthropic-api-key")
```

You will be prompted for a job URL. The matcher fetches the JD, shows the
gap analysis, asks for confirmation, then generates the tailored resume.

### Programmatic (no prompts)

```python
from src.libs.jd_resume_matcher.jd_matcher import tailor_resume_for_jd

pdf_path = tailor_resume_for_jd(
    api_key="your-anthropic-api-key",
    jd_text="...full job description text...",
    company_name="Acme Corp",   # optional — Claude detects it if omitted
)
# Returns Path to the generated PDF, or None on failure
```

### Cover letter generation

```python
from src.libs.jd_resume_matcher.jd_matcher import generate_cover_letter_for_jd
from pathlib import Path

cover_letter = generate_cover_letter_for_jd(
    api_key="your-anthropic-api-key",
    jd_text="...full job description text...",
    company_name="Acme Corp",
    job_title="Senior Data Engineer",
    output_dir=Path("output/AcmeCorp"),   # optional — saves cover_letter.txt
    resume_data={...},                    # optional — full plain_text_resume.yaml dict
)
print(cover_letter)
```

## Output structure

For each application, the matcher creates:

```
output_base_dir/
  Acme_Corp/
    JaneSmith_Resume.html     # tailored resume (HTML)
    JaneSmith_Resume.pdf      # tailored resume (PDF)
    cover_letter.txt          # cover letter (if generated)
    review_notes.md           # gap analysis + formatting review
```

## Tips

- **More variants = better selection.** 2–4 variants covering different
  positioning (e.g. IC vs lead, backend vs data) gives Claude more to work with.
- **Keep variant descriptions concise.** One sentence summarising when to use
  each variant is enough — Claude uses these before reading the resume content.
- **HTML resumes work best.** The matcher preserves your HTML/CSS structure
  exactly — fonts, layout, and styling are unchanged.
- **PDF conversion requires Chrome.** If Chrome isn't found, the matcher
  returns the HTML path instead and logs a warning.
