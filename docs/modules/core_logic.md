# Core Logic & Entry Point

## Main Application Entry (`main.py`)

The `main.py` file serves as the CLI entry point for the application.

### Key Functions

- **`main()`**: The primary execution function.
  - Initializes `FileManager` to validate data directories.
  - Calls `ConfigValidator` to ensure all YAML configs are correct.
  - Invokes `prompt_user_action()` to determine the user's intent.
  - Delegates execution to `handle_inquiries()`.

- **`handle_inquiries(selected_actions, parameters, llm_api_key)`**:
  - Routes the user's selection to the appropriate `create_*` function.
  - Supports: "Generate Resume", "Generate Tailored Resume", "Generate Cover Letter".

- **`promp_user_action()`**:
  - Uses the `inquirer` library to present an interactive CLI selection menu.

## Resume Facade (`src/libs/resume_and_cover_builder/resume_facade.py`)

The `ResumeFacade` class implements the Facade pattern to simplify the interface for resume generation operations.

### Responsibilities
- **Initialization**: Sets up the environment, including API keys, style paths, and log output.
- **Job Parsing**: Coordinates with `LLMJobParser` to extract structured data from a raw job URL.
- **Browser Control**: Manages the Selenium driver instance for scraping and PDF generation.

### Key Methods

- **`create_resume_pdf_job_tailored()`**:
  - Fetches the selected style.
  - Generates HTML using `ResumeGenerator`.
  - Converts HTML to PDF via `HTML_to_PDF` utility.

- **`link_to_job(job_url)`**:
  - Navigates the browser to the provided URL.
  - Extracts the HTML body.
  - Initialize `LLMJobParser` to interpret the page content.
