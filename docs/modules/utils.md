# Utilities and Helpers

Common utility functions used throughout the application.

## Chrome Utils (`src/utils/chrome_utils.py`)

Handles interactions with the Chrome browser via Selenium.

- **`init_browser()`**: Initializes a Selenium Chrome driver with specific options (headless mode, user-agent spoofing, window size).
- **`HTML_to_PDF(html_content, driver)`**: Uses the browser's print-to-PDF capability to convert a rendered HTML string into a PDF byte stream.

## Constants (`src/utils/constants.py`)

Central repository for string constants used in prompts and configuration keys.
- **LLM Command Keys**: `PERSONAL_INFORMATION`, `SELF_IDENTIFICATION`, `EXPERIENCE_DETAILS`, etc.
- **File Names**: `SECRETS_YAML`, `WORK_PREFERENCES_YAML`.
- **Model Aliases**: `OPENAI`, `CLAUDE`, `GEMINI`.
