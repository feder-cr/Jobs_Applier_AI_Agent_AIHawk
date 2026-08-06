import os
import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import urllib
from src.logging import logger

# Rotate through realistic user agents so each session looks different to LinkedIn
_USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]


def chrome_browser_options():
    logger.debug("Setting Chrome browser options")
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("window-size=1200x800")
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--disable-translate")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-logging")
    options.add_argument("--disable-autofill")
    options.add_argument("--disable-plugins")
    options.add_argument("--disable-animations")
    options.add_argument("--disable-cache")
    options.add_argument("--allow-file-access-from-files")
    options.add_argument("--disable-web-security")

    # Use a persistent profile so the browser remembers the session across runs.
    # Override by setting the BROWSER_PROFILE_DIR environment variable.
    import os
    profile_dir = os.environ.get(
        "BROWSER_PROFILE_DIR",
        os.path.expanduser("~/.aihawk_browser_profile")
    )
    options.add_argument(f"--user-data-dir={profile_dir}")

    ua = _USER_AGENTS[0]
    options.add_argument(f"--user-agent={ua}")
    logger.debug(f"Using user agent: {ua[:60]}...")

    # Suppress automation detection flags
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    return options


def _clear_profile_locks():
    """Kill any orphaned Chrome processes using the bot profile and remove stale lock files."""
    import subprocess
    profile_dir = os.environ.get(
        "BROWSER_PROFILE_DIR",
        os.path.expanduser("~/.aihawk_browser_profile")
    )
    # Kill any Chrome processes still using the bot profile (orphans from previous runs)
    try:
        result = subprocess.run(
            ["pgrep", "-f", profile_dir],
            capture_output=True, text=True
        )
        pids = result.stdout.strip().split()
        if pids:
            subprocess.run(["kill", "-9"] + pids, capture_output=True)
            import time as _t
            _t.sleep(1)
            logger.debug(f"Killed {len(pids)} orphaned Chrome process(es).")
    except Exception:
        pass

    # Remove stale lock files
    for lock_file in ["SingletonLock", "SingletonCookie", "SingletonSocket", "lockfile"]:
        path = os.path.join(profile_dir, lock_file)
        try:
            if os.path.exists(path) or os.path.islink(path):
                os.remove(path)
                logger.debug(f"Removed stale lock: {path}")
        except Exception:
            pass


def init_browser() -> webdriver.Chrome:
    _clear_profile_locks()

    # Try undetected-chromedriver first (much harder for LinkedIn to fingerprint)
    try:
        import undetected_chromedriver as uc
        options = uc.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        ua = random.choice(_USER_AGENTS)
        options.add_argument(f"--user-agent={ua}")
        driver = uc.Chrome(options=options)
        logger.info("Browser initialized with undetected-chromedriver (stealth mode).")
        return driver
    except ImportError:
        logger.info("undetected-chromedriver not installed — falling back to standard Selenium.")
    except Exception as e:
        logger.warning(f"undetected-chromedriver failed ({e}) — falling back to standard Selenium.")

    # Standard Selenium fallback
    try:
        options = chrome_browser_options()
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        # Patch navigator.webdriver to reduce detection
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })
        logger.debug("Chrome browser initialized (standard Selenium).")
        return driver
    except Exception as e:
        logger.error(f"Failed to initialize browser: {str(e)}")
        raise RuntimeError(f"Failed to initialize browser: {str(e)}")



def HTML_to_PDF(html_content, driver):
    """
    Converte una stringa HTML in un PDF e restituisce il PDF come stringa base64.

    :param html_content: Stringa contenente il codice HTML da convertire.
    :param driver: Istanza del WebDriver di Selenium.
    :return: Stringa base64 del PDF generato.
    :raises ValueError: Se l'input HTML non è una stringa valida.
    :raises RuntimeError: Se si verifica un'eccezione nel WebDriver.
    """
    # Validazione del contenuto HTML
    if not isinstance(html_content, str) or not html_content.strip():
        raise ValueError("Il contenuto HTML deve essere una stringa non vuota.")

    # Codifica l'HTML in un URL di tipo data
    encoded_html = urllib.parse.quote(html_content)
    data_url = f"data:text/html;charset=utf-8,{encoded_html}"

    try:
        driver.get(data_url)
        # Attendi che la pagina si carichi completamente
        time.sleep(2)  # Potrebbe essere necessario aumentare questo tempo per HTML complessi

        # Esegue il comando CDP per stampare la pagina in PDF
        pdf_base64 = driver.execute_cdp_cmd("Page.printToPDF", {
            "printBackground": True,          # Includi lo sfondo nella stampa
            "landscape": False,               # Stampa in verticale (False per ritratto)
            "paperWidth": 8.27,               # Larghezza del foglio in pollici (A4)
            "paperHeight": 11.69,             # Altezza del foglio in pollici (A4)
            "marginTop": 0.8,                  # Margine superiore in pollici (circa 2 cm)
            "marginBottom": 0.8,               # Margine inferiore in pollici (circa 2 cm)
            "marginLeft": 0.5,                 # Margine sinistro in pollici (circa 1.27 cm)
            "marginRight": 0.5,                # Margine destro in pollici (circa 1.27 cm)
            "displayHeaderFooter": False,      # Non visualizzare intestazioni e piè di pagina
            "preferCSSPageSize": True,         # Preferire le dimensioni della pagina CSS
            "generateDocumentOutline": False,  # Non generare un sommario del documento
            "generateTaggedPDF": False,        # Non generare PDF taggato
            "transferMode": "ReturnAsBase64"   # Restituire il PDF come stringa base64
        })
        return pdf_base64['data']
    except Exception as e:
        logger.error(f"Si è verificata un'eccezione WebDriver: {e}")
        raise RuntimeError(f"Si è verificata un'eccezione WebDriver: {e}")
