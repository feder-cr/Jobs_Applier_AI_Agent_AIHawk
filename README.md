# AIHawk Job Application Bot

A Python-based application designed to streamline the job application process by automatically generating professional resumes and cover letters. This tool can tailor these documents to specific job descriptions using Large Language Models (LLM), helping users create targeted and effective applications.

## About The Project

The AIHawk Job Application Bot aims to reduce the time and effort involved in crafting application materials for each job. By leveraging user-provided resume data, work preferences, and the power of LLMs, it can produce high-quality, customized documents.

Key Features:

*   **Automated Resume Generation:** Creates well-formatted resumes from a user's plain text data.
*   **Tailored Resume Generation:** Adapts resumes to specific job descriptions, highlighting relevant skills and experiences.
*   **Cover Letter Generation:** Generates personalized cover letters based on the job requirements and user profile.
*   **Multiple Resume Styles:** Offers a selection of resume templates/styles to choose from.
*   **Interactive CLI:** User-friendly command-line interface for easy operation.
*   **Configuration Driven:** Utilizes YAML files for managing user data, preferences, and API keys.

## Table of Contents

*   [About The Project](#about-the-project)
*   [Getting Started](#getting-started)
    *   [Prerequisites](#prerequisites)
    *   [Installation](#installation)
    *   [Configuration](#configuration)
*   [Usage](#usage)
*   [Key Components](#key-components)
*   [Technologies Used](#technologies-used)
*   [Contributing](#contributing)
*   [License](#license)
*   [Acknowledgements](#acknowledgements)

## Getting Started

Follow these instructions to get a local copy up and running.

### Prerequisites

*   Python 3.8 or higher
*   `pip` (Python package installer)
*   A Git client

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/feder-cr/Jobs_Applier_AI_Agent.git
    ```
2.  **Navigate to the project directory:**
    ```bash
    cd Jobs_Applier_AI_Agent
    ```
3.  **Install required packages:**
    It's highly recommended to create a virtual environment first:
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```
    Then install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

The application requires several configuration files located in the `data_folder`. You will need to create this folder and the files within it based on the examples or schemas provided.

1.  **Create `data_folder`:**
    In the root of the project, create a directory named `data_folder`.

2.  **`secrets.yaml`:**
    This file stores sensitive information like API keys. Create `data_folder/secrets.yaml`.
    *   **Content:**
        ```yaml
        llm_api_key: "YOUR_LLM_API_KEY_HERE"
        # Add other secrets if required by specific LLM providers
        ```
    *   Replace `"YOUR_LLM_API_KEY_HERE"` with your actual Large Language Model API key (e.g., OpenAI API key).

3.  **`work_preferences.yaml`:**
    This file defines your job search preferences, which might be used for tailoring or future features. Create `data_folder/work_preferences.yaml`.
    *   **Example Structure (based on `ConfigValidator` in `main.py`):**
        ```yaml
        remote: true
        experience_level:
          internship: false
          entry: true
          associate: true
          mid_senior_level: true
          director: false
          executive: false
        job_types:
          full_time: true
          contract: true
          part_time: false
          temporary: false
          internship: false
          other: false
          volunteer: false
        date: # Potentially for date posted preferences, structure needs clarification from code
          # Example: last_24_hours: true
        positions: ["Software Engineer", "Python Developer", "Data Analyst"]
        locations: ["New York, NY", "Remote"]
        location_blacklist: ["Specific City To Avoid"]
        distance: 50 # Assuming miles or km, clarify from usage
        company_blacklist: ["Company A", "Company B"]
        title_blacklist: ["Sales Manager", "Marketing Intern"]
        ```
    *   Adjust the values according to your preferences. The exact structure for `date` might need to be inferred from its usage in the application.

4.  **`plain_text_resume.yaml`:**
    This file contains your base resume information in a structured YAML format. Create `data_folder/plain_text_resume.yaml`.
    *   **Schema:** The structure for this file is defined in `assets/resume_schema.yaml`. Please refer to it for detailed field information and formatting.
    *   **Example Snippet (refer to `resume_schema.yaml` for the full structure):**
        ```yaml
        personal_information:
          name: "Liam"
          surname: "Murphy"
          # ... other personal details
        
        professional_summary: |
          A highly motivated and results-oriented Software Developer with X years of experience in...

        experience:
          - job_title: "Software Developer"
            company: "Tech Solutions Inc."
            # ... other experience details

        education:
          - degree: "B.Sc. Computer Science"
            institution: "University of Example"
            # ... other education details
        
        # ... skills, projects, achievements, languages, interests etc.
        ```

5.  **Application Configuration (`config.py`):**
    The `config.py` file in the root directory contains application-level settings such as logging levels, LLM model preferences, etc. Review and adjust these settings if needed.
    ```python
    # Example settings from config.py
    LOG_LEVEL = "ERROR" # Can be DEBUG, INFO, WARNING, ERROR
    LLM_MODEL_TYPE = 'openai' # or 'anthropic', 'ollama', etc.
    LLM_MODEL = 'gpt-4o-mini' # Specific model name
    # LLM_API_URL = '' # Only required for OLLAMA models
    ```

## Usage

Once the installation and configuration are complete, you can run the application from the command line:

```bash
python main.py
```

The application will start and present you with an interactive prompt to select actions, such as:

*   Generate Resume
*   Generate Resume Tailored for Job Description
*   Generate Cover Letter (if implemented as a separate option)

Follow the on-screen prompts:
*   If generating a tailored resume or cover letter, you will be asked to provide the URL of the job description.
*   You may be asked to select a resume style from available options.

Generated documents (likely in PDF format) will be saved in the `data_folder/output/` directory.

## Key Components

*   **`main.py`**: The main entry point of the application. It handles command-line arguments (via `click`), user interactions (via `inquirer`), loads configurations, validates inputs, and orchestrates the resume/cover letter generation process.
*   **`src/libs/resume_and_cover_builder/`**: This directory contains the core logic for building resumes and cover letters.
    *   `ResumeFacade.py`: Acts as a high-level interface for the generation process, coordinating between the resume data, styling, LLM interaction, and PDF output.
    *   `ResumeGenerator.py`: Responsible for the actual construction and content generation of the resume, possibly involving LLM calls for text generation or refinement.
    *   `StyleManager.py`: Manages different resume styles/templates, allowing users to choose the appearance of their generated documents.
    *   `config.py` (within this lib): Likely holds configuration specific to the resume building library.
*   **`src/resume_schemas/`**: Defines Pydantic models (e.g., `JobApplicationProfile.py`, `Resume.py`) for structuring and validating resume data and job application profiles. This ensures data integrity.
*   **`src/utils/`**: Contains utility modules.
    *   `chrome_utils.py`: Provides functions for initializing and managing a Selenium WebDriver for browser interactions (e.g., fetching job description content from a URL).
    *   `constants.py`: Defines constant values used throughout the application (e.g., file names, default settings).
    *   `logging.py`: Configures the logging setup for the application.
*   **`data_folder/`**:
    *   Stores user-specific configuration files (`secrets.yaml`, `work_preferences.yaml`, `plain_text_resume.yaml`).
    *   `output/`: The subdirectory where generated resumes and cover letters are saved.
*   **`config.py` (root level)**: Global application configuration settings like logging preferences, API endpoints, and default behaviors.
*   **`assets/resume_schema.yaml`**: A YAML schema defining the expected structure and data types for the `plain_text_resume.yaml` file.
*   **`requirements.txt`**: Lists all Python dependencies required for the project.
*   **`.github/workflows/ci.yml`**: Defines a GitHub Actions workflow for Continuous Integration, likely running tests on push or pull request.

## Technologies Used

*   **Python**: Core programming language.
*   **Langchain**: Framework for developing applications powered by large language models.
    *   `langchain-openai`, `langchain-anthropic`, `langchain-google-genai`, `langchain-ollama`: Specific integrations for various LLM providers.
*   **OpenAI API (or other LLMs)**: Used for generating and tailoring text content.
*   **Selenium**: For browser automation, likely used to fetch content from job description URLs.
*   **WebDriver Manager**: Simplifies the management of browser drivers for Selenium.
*   **Click**: For creating the command-line interface.
*   **Inquirer**: For creating interactive command-line user prompts.
*   **PyYAML**: For reading and writing YAML configuration files.
*   **ReportLab**: A library for creating PDF documents programmatically (inferred from typical resume generation needs).
*   **PDFMiner.six**: For extracting text and data from PDF documents (might be used for parsing existing resumes or job descriptions if they are in PDF format).
*   **Loguru**: For enhanced logging capabilities.
*   **pytest**: For running automated tests.
*   **HTTPX**: A modern HTTP client, likely used for API interactions.

## Contributing

Contributions are welcome! Please read the `CONTRIBUTING.md` file for guidelines on how to contribute to this project. This includes information on:

*   Reporting bugs
*   Suggesting enhancements
*   Coding standards (PEP 8)
*   Setting up a development environment
*   Testing procedures
*   Branching strategy and pull requests

## License

This project is licensed under the **GNU Affero General Public License v3.0**. See the `LICENSE` file for more details.

## Acknowledgements

*   The various open-source Python libraries that make this project possible.
*   The developers and community behind Langchain for their powerful LLM framework.

---
*This README was generated with the assistance of an AI coding agent.*

