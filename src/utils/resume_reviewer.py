"""
Resume PDF Reviewer — checks generated PDFs for common formatting issues.

Issues detected:
  1. Page overflow   — resume spills beyond 1 page
  2. Print headers   — Chrome date/time/path headers leaked into the PDF
  3. Print footers   — file:// URL footer leaked into the PDF

Auto-fix: if issues found, tightens CSS margins in the HTML and regenerates.
"""
import re
import subprocess
from pathlib import Path

from src.logging import logger

CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Patterns that indicate Chrome print headers/footers leaked in
_HEADER_PATTERNS = [
    r"\d{1,2}/\d{1,2}/\d{2,4},?\s+\d{1,2}:\d{2}",  # date like "4/3/26, 4:15 PM"
    r"file:///",                                        # file:// footer
    r"https?://\S+\s+\d+/\d+",                         # URL + page number
]

_TIGHTER_PRINT_CSS = """\
    @media print {
      body { padding: 10px 25px; font-size: 10.5px; }
      @page { margin: 8mm; size: A4; }
      section { margin-bottom: 10px; }
      .job { margin-bottom: 8px; }
      ul li { margin-bottom: 2px; }
    }"""

_OLD_PRINT_CSS_PATTERN = re.compile(
    r"@media print\s*\{[^}]*body\s*\{[^}]*padding[^}]*\}[^}]*@page[^}]*\}[^}]*\}",
    re.DOTALL,
)


def _extract_text_sample(pdf_path: Path) -> tuple[int, str]:
    """Return (page_count, sample_text_from_page_boundaries)."""
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            pages = len(pdf.pages)
            # Sample text from top of page 1, bottom of page 1, top of page 2 (if exists)
            samples = []
            for i, page in enumerate(pdf.pages[:2]):
                text = page.extract_text() or ""
                if i == 0:
                    # bottom of page 1 (last 200 chars)
                    samples.append(text[-200:])
                else:
                    # top of page 2 (first 200 chars)
                    samples.append(text[:200])
            return pages, "\n".join(samples)
    except ImportError:
        logger.warning("pdfplumber not installed — skipping text-based header check.")
        return _check_page_count_fallback(pdf_path), ""
    except Exception as e:
        logger.warning(f"PDF read error: {e}")
        return 1, ""


def _check_page_count_fallback(pdf_path: Path) -> int:
    """Fallback: use mdls (macOS) or pdfinfo to get page count."""
    try:
        result = subprocess.run(
            ["mdls", "-name", "kMDItemNumberOfPages", str(pdf_path)],
            capture_output=True, text=True,
        )
        match = re.search(r"(\d+)", result.stdout)
        return int(match.group(1)) if match else 1
    except Exception:
        return 1


def _fix_html_print_css(html_path: Path) -> bool:
    """Replace old @media print block with tighter one. Returns True if changed."""
    content = html_path.read_text(encoding="utf-8")
    if _TIGHTER_PRINT_CSS.strip() in content:
        return False  # already tight
    new_content = _OLD_PRINT_CSS_PATTERN.sub(_TIGHTER_PRINT_CSS, content)
    if new_content != content:
        html_path.write_text(new_content, encoding="utf-8")
        return True
    return False


def _regenerate_pdf(html_path: Path, pdf_path: Path) -> bool:
    """Regenerate PDF from HTML using Chrome headless with header suppression."""
    try:
        result = subprocess.run(
            [
                CHROME_BIN,
                "--headless", "--disable-gpu",
                f"--print-to-pdf={pdf_path}",
                "--print-to-pdf-no-header",
                "--no-pdf-header-footer",
                f"file://{html_path}",
            ],
            capture_output=True, text=True,
        )
        return pdf_path.exists()
    except Exception as e:
        logger.error(f"PDF regeneration failed: {e}")
        return False


def review_resume_pdf(pdf_path: Path, html_path: Path = None, auto_fix: bool = True) -> list[str]:
    """
    Review a generated resume PDF for formatting issues.

    Args:
        pdf_path:  Path to the generated PDF
        html_path: Path to the source HTML (needed for auto-fix)
        auto_fix:  If True, attempt to fix issues automatically

    Returns:
        List of issue strings. Empty list = all good.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        return [f"PDF not found: {pdf_path}"]

    issues = []
    page_count, text_sample = _extract_text_sample(pdf_path)

    # Check 1: page overflow
    if page_count > 1:
        issues.append(f"OVERFLOW — resume is {page_count} pages (should be 1)")

    # Check 2: print headers/footers leaked
    for pattern in _HEADER_PATTERNS:
        if re.search(pattern, text_sample, re.IGNORECASE):
            issues.append(f"HEADERS — Chrome print headers/footers detected in PDF")
            break

    if not issues:
        logger.info(f"  ✓ Resume review passed: 1 page, no headers — {pdf_path.name}")
        print(f"  ✓ Resume OK — 1 page, no print headers.")
        return []

    # Report issues
    print(f"\n  ⚠️  Resume review found {len(issues)} issue(s) in {pdf_path.name}:")
    for issue in issues:
        print(f"     - {issue}")

    # Auto-fix
    if auto_fix and html_path:
        html_path = Path(html_path)
        print(f"  → Auto-fixing: tightening CSS and regenerating PDF...")
        css_changed = _fix_html_print_css(html_path)
        if css_changed:
            logger.info(f"Updated print CSS in {html_path.name}")
        success = _regenerate_pdf(html_path, pdf_path)
        if success:
            # Re-check after fix
            new_pages, new_sample = _extract_text_sample(pdf_path)
            remaining = []
            if new_pages > 1:
                remaining.append(f"OVERFLOW — still {new_pages} pages after fix (manual trim needed)")
            for pattern in _HEADER_PATTERNS:
                if re.search(pattern, new_sample, re.IGNORECASE):
                    remaining.append("HEADERS — still present after fix")
                    break
            if not remaining:
                print(f"  ✓ Fixed — PDF now looks clean.")
                return issues  # return original issues (fixed)
            else:
                print(f"  ✗ Still have issues after auto-fix:")
                for r in remaining:
                    print(f"     - {r}")
                return remaining
        else:
            print(f"  ✗ PDF regeneration failed.")

    return issues
