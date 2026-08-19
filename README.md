<p align="center">
  <a href="https://github.com/feder-cr/invisible_playwright"><img src="https://raw.githubusercontent.com/feder-cr/Jobs_Applier_AI_Agent_AIHawk/main/assets/invisible-playwright-banner.png" alt="invisible_playwright - the best undetectable browser" width="880"></a>
</p>

<p align="center">
  <a href="https://pypi.org/project/invisible-playwright/"><img src="https://img.shields.io/pypi/v/invisible-playwright?color=38f0c8&label=pypi" alt="PyPI"></a>
  <a href="https://pypi.org/project/invisible-playwright/"><img src="https://static.pepy.tech/badge/invisible-playwright" alt="Downloads"></a>
  <img src="https://img.shields.io/pypi/pyversions/invisible-playwright" alt="Python">
  <img src="https://img.shields.io/github/license/feder-cr/invisible_playwright" alt="License">
  <a href="https://github.com/feder-cr/invisible_playwright"><img src="https://img.shields.io/github/stars/feder-cr/invisible_playwright?style=social" alt="Stars"></a>
</p>

<h3 align="center">The best undetectable browser, open source.<br>An undetected Playwright on a real Firefox, patched at the source, that passes every bot detection test.</h3>

## Why invisible_playwright?

- **Undetected by design**: a real Firefox patched at the C++ source, so the fingerprint (navigator, screen, GPU/WebGL, canvas, fonts, audio, WebRTC) is set inside the engine, not injected into the page. No JS shim, no seam to read.
- **Passes every bot detection test**: reCAPTCHA, hCaptcha and Cloudflare Turnstile score it as human. 5/5 detection suites.
- **Human actions**: every click, hover and drag follows a Bezier-curve mouse path with real timing and trusted events, no teleporting cursor.
- **100% Playwright-compatible**: sync and async, all methods, zero API changes. Switching from Playwright is two lines.
- **Reproducible**: seed a run and get the same GPU, canvas hash and audio context every time.
- **Proxies built in**: socks5, socks4, http and https, with DNS routed through the proxy so there is no local leak.
- **Open source**.

## Quick start

```bash
pip install invisible-playwright
python -m invisible_playwright fetch
```

```python
from invisible_playwright import InvisiblePlaywright

with InvisiblePlaywright() as browser:
    page = browser.new_page()
    page.goto("https://example.com")
    page.click("#submit")   # mouse arcs to the button on a Bezier curve
```

Full docs and source: [github.com/feder-cr/invisible_playwright](https://github.com/feder-cr/invisible_playwright)

---

<div align="center">


# AIHawk: The first Jobs Applier AI Web Agent


[![LinkedIn](https://img.shields.io/badge/LinkedIn-Federico%20Elia-0A66C2?logo=linkedin&logoColor=white)](https://it.linkedin.com/in/federico-elia-5199951b6)

AIHawk's core architecture remains **open source**, allowing developers to inspect and extend the codebase. However, due to copyright considerations, we have removed all third‑party provider plugins from this repository.



---


AIHawk has been featured by major media outlets for revolutionizing how job seekers interact with the job market:

[**Business Insider**](https://www.businessinsider.com/aihawk-applies-jobs-for-you-linkedin-risks-inaccuracies-mistakes-2024-11)
[**TechCrunch**](https://techcrunch.com/2024/10/10/a-reporter-used-ai-to-apply-to-2843-jobs/)
[**Semafor**](https://www.semafor.com/article/09/12/2024/linkedins-have-nots-and-have-bots)
[**Dev.by**](https://devby.io/news/ya-razoslal-rezume-na-2843-vakansii-po-17-v-chas-kak-ii-boty-vytesnyaut-ludei-iz-protsessa-naima.amp)
[**Wired**](https://www.wired.it/article/aihawk-come-automatizzare-ricerca-lavoro/)
[**The Verge**](https://www.theverge.com/2024/10/10/24266898/ai-is-enabling-job-seekers-to-think-like-spammers)
[**Vanity Fair**](https://www.vanityfair.it/article/intelligenza-artificiale-candidature-di-lavoro)
[**404 Media**](https://www.404media.co/i-applied-to-2-843-roles-the-rise-of-ai-powered-job-application-bots/)

---

</div>
