"""
VisualFormFiller — uses Claude Vision to fill arbitrary job application forms.

Flow:
  1. Take a screenshot of the current page
  2. Send to Claude Sonnet with candidate profile
  3. Claude identifies visible fields + values to fill
  4. Selenium fills each field
  5. Click Next/Continue if present
  6. Repeat until done or human input needed
  7. Pause before final submit for human confirmation
"""
import base64
import json
import os
import re
import subprocess
import time

from anthropic import Anthropic
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.logging import logger


class VisualFormFiller:
    """Fill any job application form using Claude Vision + Selenium."""

    def __init__(self, driver, api_key: str, profile: dict, resume_pdf_path=None,
                 resume_data: dict = None):
        self.driver = driver
        self.client = Anthropic(api_key=api_key)
        self.profile = profile
        self.resume_data = resume_data or {}
        self.resume_pdf_path = resume_pdf_path
        self._profile_text = self._build_profile_text()

    # ------------------------------------------------------------------ #
    # Voice notification
    # ------------------------------------------------------------------ #

    def _speak(self, message: str):
        """Speak a message aloud (non-blocking). Falls back to print if TTS unavailable."""
        import platform
        print(f"\n[ATTENTION] {message}")
        try:
            system = platform.system()
            if system == "Darwin":
                subprocess.Popen(["say", message])
            elif system == "Linux":
                subprocess.Popen(["espeak", message], stderr=subprocess.DEVNULL)
            # Windows: no built-in CLI TTS; print fallback above is sufficient
        except Exception:
            pass  # print fallback already shown above

    # ------------------------------------------------------------------ #
    # Profile helpers
    # ------------------------------------------------------------------ #

    def _build_profile_text(self) -> str:
        """Format the candidate profile dict into plain text for Claude."""
        pi = self.profile if isinstance(self.profile, dict) else {}
        rd = self.resume_data

        name = f"{pi.get('name', '')} {pi.get('surname', '')}".strip()
        phone = f"{pi.get('phone_prefix', '')} {pi.get('phone', '')}".strip()

        # Notice period
        notice_period = rd.get("availability", {}).get("notice_period", "")

        # Salary
        salary = rd.get("salary_expectations", {}).get("salary_range_usd", "")

        # Current role — first entry in experience_details
        exp_list = rd.get("experience_details", [])
        current_role = ""
        if exp_list:
            e = exp_list[0]
            pos = e.get("position", "")
            comp = e.get("company", "")
            current_role = f"{pos} at {comp}".strip(" at") if pos or comp else ""

        # Years of experience — count from experience_details
        years_of_exp = len(exp_list) and f"{len(exp_list)}+ roles" or ""

        # Education — first entry in education_details
        edu_list = rd.get("education_details", [])
        education = ""
        if edu_list:
            e = edu_list[0]
            level = e.get("education_level", "")
            field = e.get("field_of_study", "")
            inst = e.get("institution", "")
            year = e.get("year_of_completion", "")
            education = ", ".join(p for p in [f"{level} in {field}" if level or field else "",
                                               inst, year] if p)

        # Skills — collect from all experience_details entries
        all_skills = []
        for exp in exp_list:
            all_skills.extend(exp.get("skills_acquired", []))
        skills = ", ".join(dict.fromkeys(all_skills))  # deduplicated, order-preserved

        # Work authorization summary
        legal = rd.get("legal_authorization", {})
        auth_parts = []
        for region, key in [("EU", "eu_work_authorization"), ("US", "us_work_authorization"),
                            ("UK", "uk_work_authorization"), ("Canada", "canada_work_authorization")]:
            if str(legal.get(key, "")).lower() == "yes":
                auth_parts.append(region)
        work_auth = f"Authorized to work in: {', '.join(auth_parts)}" if auth_parts else ""

        lines = [
            f"Full Name: {name}",
            f"Email: {pi.get('email', '')}",
            f"Phone: {phone}",
            f"Location: {pi.get('city', '')}, {pi.get('country', '')}",
            f"Address: {pi.get('address', '')}",
            f"LinkedIn: {pi.get('linkedin', '')}",
            f"GitHub: {pi.get('github', '')}",
            f"Notice Period: {notice_period}",
            f"Current Role: {current_role}",
            f"Years of Experience: {years_of_exp}",
            f"Desired Salary: {salary}",
            f"Work Authorization: {work_auth}",
            f"Education: {education}",
            f"Skills: {skills}",
        ]
        return "\n".join(line for line in lines if line.split(": ", 1)[-1].strip())

    # ------------------------------------------------------------------ #
    # Auto-dismiss blocking modals
    # ------------------------------------------------------------------ #

    def _dismiss_blocking_modals(self) -> bool:
        """
        Auto-click through common blocking popups: cookie banners, confirmation
        dialogs, navigation warnings, GDPR notices. Returns True if something was dismissed.
        """
        # --- Cookie / GDPR banners (common vendor selectors) ---
        cookie_selectors = [
            "#onetrust-accept-btn-handler",
            "#accept-cookies",
            "#cookieConsent button",
            "button[id*='accept'][id*='cookie']",
            "button[class*='accept'][class*='cookie']",
            "button[data-testid*='cookie']",
            ".cookie-consent button",
            ".cookie-banner button",
            ".cc-btn.cc-allow",
        ]
        for sel in cookie_selectors:
            try:
                btn = self.driver.find_element(By.CSS_SELECTOR, sel)
                if btn.is_displayed():
                    btn.click()
                    logger.info(f"Auto-dismissed cookie banner via: {sel}")
                    time.sleep(1.5)
                    return True
            except Exception:
                continue

        # --- Generic dialog / modal buttons ---
        # Ordered by preference: OK > Accept > Agree > Continue (before Reject/Close)
        accept_keywords = ["ok", "accept all", "accept cookies", "accept", "agree",
                           "got it", "allow all", "i agree", "continue", "proceed"]

        # Try buttons inside known dialog containers first
        dialog_containers = [
            "[role='dialog']", "[role='alertdialog']",
            ".modal", ".popup", ".overlay", ".dialog",
            ".confirmation", ".alert", "[aria-modal='true']",
        ]
        for container in dialog_containers:
            try:
                btns = self.driver.find_elements(By.CSS_SELECTOR, f"{container} button")
                for kw in accept_keywords:
                    for btn in btns:
                        try:
                            if btn.is_displayed() and btn.text.strip().lower() == kw:
                                btn.click()
                                logger.info(f"Auto-dismissed modal via button text '{kw}'")
                                time.sleep(1.5)
                                return True
                        except Exception:
                            continue
            except Exception:
                continue

        # --- Fallback: any visible button with exact OK / Accept text ---
        for kw in ["ok", "accept", "agree"]:
            try:
                btns = self.driver.find_elements(By.TAG_NAME, "button")
                for btn in btns:
                    try:
                        if btn.is_displayed() and btn.text.strip().lower() == kw:
                            btn.click()
                            logger.info(f"Auto-dismissed popup via fallback button '{kw}'")
                            time.sleep(1.5)
                            return True
                    except Exception:
                        continue
            except Exception:
                continue

        return False

    # ------------------------------------------------------------------ #
    # Screenshot
    # ------------------------------------------------------------------ #

    def _screenshot_b64(self) -> str:
        """Take a full-page screenshot and return as base64 PNG."""
        png = self.driver.get_screenshot_as_png()
        return base64.b64encode(png).decode()

    # ------------------------------------------------------------------ #
    # Claude Vision analysis
    # ------------------------------------------------------------------ #

    def _analyse_page(self, b64: str, job_title: str, company: str) -> dict:
        """Send screenshot to Claude and get structured fill instructions."""
        prompt = f"""You are helping fill a job application form for the position of "{job_title}" at "{company}".

Candidate profile:
{self._profile_text}

Look at this screenshot carefully and identify every visible, fillable form field.

Return ONLY valid JSON in this exact format — no markdown, no explanation:
{{
  "fields": [
    {{
      "description": "human-readable field name (e.g. First Name, Email, Phone Number)",
      "value": "the value to fill based on the candidate profile above",
      "field_type": "text|email|phone|textarea|select|file|checkbox|radio",
      "label_text": "exact label text visible next to the field, or empty string",
      "placeholder": "placeholder text inside the field if visible, or empty string",
      "skip": false,
      "reason": "why skip=true if applicable"
    }}
  ],
  "page_status": "form|job_listing|success|error|captcha|already_applied|other",
  "has_next_button": true,
  "has_submit_button": false,
  "needs_human": false,
  "human_note": ""
}}

Rules:
- For file upload fields (resume, CV, cover letter upload), set skip=true
- For CAPTCHA or verification, set needs_human=true with a clear human_note
- If page shows success/confirmation, set page_status="success"
- For checkboxes like "I agree to terms", set field_type="checkbox" and value="check"
- For select/dropdown, set value to the most appropriate visible option text
- Only include fields currently visible on screen
- If a field is already filled correctly, still include it with the correct value
- For textarea fields (cover letter, additional info), write a brief professional response"""

        try:
            resp = self.client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": b64,
                            }
                        },
                        {"type": "text", "text": prompt}
                    ]
                }]
            )
            text = resp.content[0].text.strip()
            # Strip markdown code fences if present
            text = re.sub(r'^```[a-z]*\n?', '', text)
            text = re.sub(r'\n?```$', '', text)
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.warning(f"Claude JSON parse error: {e}")
            return {
                "fields": [], "page_status": "other",
                "has_next_button": False, "has_submit_button": False,
                "needs_human": True, "human_note": "Could not parse Claude response"
            }
        except Exception as e:
            logger.error(f"Claude Vision error: {e}")
            return {
                "fields": [], "page_status": "other",
                "has_next_button": False, "has_submit_button": False,
                "needs_human": True, "human_note": f"API error: {e}"
            }

    # ------------------------------------------------------------------ #
    # Field filling
    # ------------------------------------------------------------------ #

    def _set_react_value(self, element, value: str):
        """Set value on React/Angular controlled inputs that ignore send_keys."""
        self.driver.execute_script("""
            var el = arguments[0];
            var val = arguments[1];
            var nativeSetter = Object.getOwnPropertyDescriptor(
                window.HTMLInputElement.prototype, 'value'
            ).set;
            nativeSetter.call(el, val);
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
        """, element, value)

    def _find_input_by_label(self, label_text: str):
        """Find input associated with a label containing the given text."""
        try:
            # Find label containing the text
            labels = self.driver.find_elements(By.TAG_NAME, "label")
            for label in labels:
                if label_text.lower() in label.text.lower():
                    for_attr = label.get_attribute("for")
                    if for_attr:
                        try:
                            return self.driver.find_element(By.ID, for_attr)
                        except Exception:
                            pass
                    # Try sibling/child input
                    try:
                        return label.find_element(By.CSS_SELECTOR, "input, textarea, select")
                    except Exception:
                        pass
        except Exception:
            pass
        return None

    def _find_input_by_placeholder(self, placeholder: str):
        """Find input by placeholder attribute (partial match)."""
        try:
            for tag in ["input", "textarea"]:
                els = self.driver.find_elements(By.TAG_NAME, tag)
                for el in els:
                    ph = (el.get_attribute("placeholder") or "").lower()
                    if placeholder.lower() in ph:
                        return el
        except Exception:
            pass
        return None

    def _find_input_by_type(self, field_type: str):
        """Find first visible input of a given type."""
        type_map = {"email": "email", "phone": "tel", "text": "text"}
        html_type = type_map.get(field_type)
        if not html_type:
            return None
        try:
            els = self.driver.find_elements(By.CSS_SELECTOR, f"input[type='{html_type}']")
            for el in els:
                if el.is_displayed() and el.is_enabled():
                    return el
        except Exception:
            pass
        return None

    def _find_input_by_aria(self, description: str):
        """Find input by aria-label (partial match)."""
        try:
            for tag in ["input", "textarea", "select"]:
                els = self.driver.find_elements(By.TAG_NAME, tag)
                for el in els:
                    aria = (el.get_attribute("aria-label") or "").lower()
                    name = (el.get_attribute("name") or "").lower()
                    if description.lower() in aria or description.lower() in name:
                        return el
        except Exception:
            pass
        return None

    def _fill_one_field(self, field: dict) -> bool:
        """Try to fill a single field. Returns True if successful."""
        if field.get("skip"):
            logger.debug(f"Skipping field: {field.get('description')} — {field.get('reason', '')}")
            return True

        description = field.get("description", "")
        value = field.get("value", "")
        field_type = field.get("field_type", "text")
        label_text = field.get("label_text", "")
        placeholder = field.get("placeholder", "")

        if not value:
            return True

        # Find the element using multiple strategies
        element = None
        if label_text:
            element = self._find_input_by_label(label_text)
        if not element and placeholder:
            element = self._find_input_by_placeholder(placeholder)
        if not element:
            element = self._find_input_by_aria(description)
        if not element and field_type in ("email", "phone"):
            element = self._find_input_by_type(field_type)

        if not element:
            logger.warning(f"Could not find element for: {description}")
            return False

        try:
            if not element.is_displayed() or not element.is_enabled():
                return False

            tag = element.tag_name.lower()

            if tag == "select" or field_type == "select":
                sel = Select(element)
                try:
                    sel.select_by_visible_text(value)
                except Exception:
                    # Try partial match
                    for opt in sel.options:
                        if value.lower() in opt.text.lower():
                            sel.select_by_visible_text(opt.text)
                            break
                logger.debug(f"Selected '{value}' for: {description}")
                return True

            if field_type == "checkbox":
                if not element.is_selected():
                    element.click()
                logger.debug(f"Checked checkbox: {description}")
                return True

            if field_type == "radio":
                element.click()
                logger.debug(f"Selected radio: {description}")
                return True

            # Text / email / phone / textarea
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.3)
            element.click()
            element.clear()
            element.send_keys(value)

            # Verify value was set — if not, try the React setter
            actual = element.get_attribute("value") or ""
            if actual.strip() != value.strip():
                self._set_react_value(element, value)

            logger.debug(f"Filled '{description}' = '{value[:40]}...' " if len(value) > 40 else f"Filled '{description}' = '{value}'")
            return True

        except Exception as e:
            logger.warning(f"Error filling '{description}': {e}")
            return False

    def _fill_all_fields(self, fields: list) -> int:
        """Fill all fields. Returns count of successfully filled fields."""
        filled = 0
        for field in fields:
            if self._fill_one_field(field):
                filled += 1
            time.sleep(0.4)  # brief pause between fields
        return filled

    # ------------------------------------------------------------------ #
    # Navigation
    # ------------------------------------------------------------------ #

    def _click_next_or_submit(self, has_next: bool, has_submit: bool) -> str:
        """Click Next or Submit button. Returns 'next', 'submit', or 'none'."""
        next_texts = ["next", "continue", "proceed", "save and continue", "下一步", "继续"]
        submit_texts = ["submit", "apply", "send application", "complete application",
                        "submit application", "提交"]

        # --- Strategy 1: LinkedIn Easy Apply modal CSS selectors ---
        linkedin_sels = [
            "button[aria-label='Continue to next step']",
            "button[aria-label='Submit application']",
            "button[aria-label='Review your application']",
            "footer button.artdeco-button--primary",
            ".jobs-easy-apply-modal footer button",
            ".artdeco-modal__actionbar button.artdeco-button--primary",
            ".artdeco-modal footer button",
            "div[data-test-modal] button.artdeco-button--primary",
        ]
        for sel in linkedin_sels:
            try:
                btn = self.driver.find_element(By.CSS_SELECTOR, sel)
                if btn.is_enabled():
                    self.driver.execute_script("arguments[0].click();", btn)
                    logger.info(f"Clicked modal button via CSS: {sel}")
                    return "next" if has_next else "submit"
            except Exception:
                continue

        # --- Strategy 2: JS scan all buttons by visible text ---
        target_texts = next_texts if has_next else submit_texts
        js_result = self.driver.execute_script("""
            var targets = arguments[0];
            var buttons = document.querySelectorAll('button, input[type="submit"]');
            for (var btn of buttons) {
                var txt = (btn.innerText || btn.value || '').trim().toLowerCase();
                for (var t of targets) {
                    if (txt === t || txt.indexOf(t) !== -1) {
                        if (btn.offsetParent !== null || btn.offsetWidth > 0) {
                            btn.click();
                            return btn.innerText || btn.value;
                        }
                    }
                }
            }
            return null;
        """, target_texts)

        if js_result:
            logger.info(f"Clicked button via JS: '{js_result}'")
            return "next" if has_next else "submit"

        # --- Strategy 3: Primary/highlighted button (last resort) ---
        primary_sels = [
            "button.artdeco-button--primary",
            "button[type='submit']",
            "button.primary",
            "button.btn-primary",
        ]
        for sel in primary_sels:
            try:
                btns = self.driver.find_elements(By.CSS_SELECTOR, sel)
                for btn in btns:
                    if btn.is_enabled():
                        txt = btn.text.strip().lower()
                        # Don't accidentally click Back/Cancel/Close
                        if any(skip in txt for skip in ["back", "cancel", "close", "discard", "dismiss"]):
                            continue
                        self.driver.execute_script("arguments[0].click();", btn)
                        logger.info(f"Clicked primary button '{btn.text.strip()}' via: {sel}")
                        return "next" if has_next else "submit"
            except Exception:
                continue

        return "none"

    def _click_apply_now(self) -> bool:
        """Click 'Apply Now' / 'Apply' on an external company job listing page."""
        apply_texts = ["apply now", "apply for this job", "apply for job",
                       "start application", "begin application", "apply online"]
        # Exact CSS selectors common on company career sites
        apply_sels = [
            "a[class*='apply']", "button[class*='apply']",
            "a[id*='apply']", "button[id*='apply']",
            "a[href*='apply']",
        ]
        for sel in apply_sels:
            try:
                btn = self.driver.find_element(By.CSS_SELECTOR, sel)
                if btn.is_displayed():
                    self.driver.execute_script("arguments[0].click();", btn)
                    logger.info(f"Clicked Apply via CSS: {sel}")
                    time.sleep(3)
                    return True
            except Exception:
                continue

        # JS text scan
        result = self.driver.execute_script("""
            var targets = arguments[0];
            var els = document.querySelectorAll('a, button');
            for (var el of els) {
                var txt = (el.innerText || el.textContent || '').trim().toLowerCase();
                for (var t of targets) {
                    if (txt === t) {
                        el.click();
                        return txt;
                    }
                }
            }
            return null;
        """, apply_texts)

        if result:
            logger.info(f"Clicked Apply via JS text: '{result}'")
            time.sleep(3)
            return True
        return False

    # ------------------------------------------------------------------ #
    # Main loop
    # ------------------------------------------------------------------ #

    def run(self, job_title: str = "the role", company: str = "the company",
            max_iterations: int = 8) -> bool:
        """
        Main vision loop. Returns True if application submitted, False otherwise.
        Pauses before final submit for human confirmation.
        """
        print(f"\n  [VisualFiller] Starting vision-based form fill for {job_title} @ {company}")
        print(f"  Profile loaded: {self._profile_text.splitlines()[0]}")

        for iteration in range(1, max_iterations + 1):
            print(f"\n  [VisualFiller] Iteration {iteration}/{max_iterations} — checking for popups...")
            time.sleep(2)  # let page settle

            # Auto-dismiss any blocking modals before analysing the page
            dismissed = self._dismiss_blocking_modals()
            if dismissed:
                print(f"  [VisualFiller] Auto-dismissed a blocking popup — re-checking page...")
                time.sleep(2)

            print(f"  [VisualFiller] Taking screenshot...")
            b64 = self._screenshot_b64()
            print(f"  [VisualFiller] Sending screenshot to Claude Vision...")
            analysis = self._analyse_page(b64, job_title, company)

            status = analysis.get("page_status", "other")
            logger.debug(f"Page status: {status}")

            if status == "success":
                print(f"  [VisualFiller] ✓ Application submitted successfully!")
                return True

            if status == "already_applied":
                print(f"  [VisualFiller] Already applied to this role — skipping.")
                return False

            # Auto-click "Apply Now" if we're on a job listing page (not a form yet)
            if status == "job_listing":
                print(f"  [VisualFiller] Job listing page detected — clicking Apply Now...")
                if self._click_apply_now():
                    print(f"  [VisualFiller] Clicked Apply Now — loading application form...")
                    time.sleep(3)
                    # Switch to new tab if one opened
                    handles = set(self.driver.window_handles)
                    if len(handles) > 1:
                        self.driver.switch_to.window(list(handles)[-1])
                        time.sleep(2)
                    continue
                else:
                    print(f"  [VisualFiller] Could not find Apply Now button — please click it manually.")
                    try:
                        input("  Press Enter when done...")
                    except EOFError:
                        pass
                    continue

            if analysis.get("needs_human"):
                note = analysis.get("human_note", "")
                print(f"\n  ⚠️  Human input needed: {note}")
                print("  Please complete the action in the browser, then press Enter to continue...")
                self._speak(f"Human input needed: {note}. Please check the browser and press Enter.")
                try:
                    input()
                except (KeyboardInterrupt, EOFError):
                    print("  (No interactive input — continuing automatically after 10s...)")
                    time.sleep(10)
                continue

            fields = analysis.get("fields", [])
            has_next = analysis.get("has_next_button", False)
            has_submit = analysis.get("has_submit_button", False)

            if not fields and not has_next and not has_submit:
                print(f"  [VisualFiller] No fields or buttons found — may need human review.")
                print("  Press Enter to continue or Ctrl+C to abort...")
                self._speak("No form fields or buttons detected. Please check the browser and press Enter.")
                try:
                    input()
                except (KeyboardInterrupt, EOFError):
                    print("  (Continuing automatically after 10s...)")
                    time.sleep(10)
                continue

            # Fill visible fields
            if fields:
                filled = self._fill_all_fields(fields)
                print(f"  [VisualFiller] Filled {filled}/{len(fields)} fields.")
            time.sleep(1)

            # If submit button — pause for human confirmation before clicking
            if has_submit and not has_next:
                print(f"\n  [VisualFiller] Ready to submit application for {job_title} @ {company}.")
                print("  Review the filled form in the browser window.")
                print("  Press Enter to SUBMIT, or Ctrl+C to abort...")
                self._speak(f"Application for {job_title} at {company} is ready to submit. Please review the form and press Enter to submit.")
                try:
                    input()
                except (KeyboardInterrupt, EOFError):
                    print("  (No interactive input — submission skipped)")
                    return False
                result = self._click_next_or_submit(False, True)
                if result == "submit":
                    print(f"  [VisualFiller] ✓ Submitted!")
                    time.sleep(3)
                    return True
                else:
                    print("  [VisualFiller] Could not find submit button — please submit manually.")
                    input("  Press Enter when done...")
                    return True

            # Click Next/Continue
            if has_next or has_submit:
                result = self._click_next_or_submit(has_next, has_submit)
                if result == "none":
                    print("  [VisualFiller] Could not find Next button — please click it manually.")
                    self._speak("Could not find the Next button. Please click it manually and press Enter.")
                    try:
                        input("  Press Enter when done...")
                    except (KeyboardInterrupt, EOFError):
                        time.sleep(5)
                else:
                    print(f"  [VisualFiller] Clicked '{result}' — loading next page...")
                time.sleep(3)

        print(f"  [VisualFiller] Max iterations reached. Please complete form manually.")
        self._speak("Maximum iterations reached. Please complete the form manually and press Enter.")
        try:
            input("  Press Enter when done (or Ctrl+C to skip)...")
        except (KeyboardInterrupt, EOFError):
            pass
        return False
