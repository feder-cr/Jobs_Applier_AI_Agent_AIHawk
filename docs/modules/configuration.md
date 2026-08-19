# Configuration & Validation

The application relies on three main YAML configuration files located in the `data_folder`.

## Configuration Files

1. **`secrets.yaml`**: Stores sensitive API keys (e.g., `llm_api_key`).
2. **`config.yaml`**: General settings like `remote`, `experience_level`, `locations`, `blacklists`.
3. **`plain_text_resume.yaml`**: The user's resume data in YAML format.

## Config Validator (`main.py`)

The `ConfigValidator` class ensures that the `config.yaml` file contains valid settings before the app runs.

### Validation Rules
- **Required Keys**: Checks for existence of keys like `positions`, `locations`, `distance`.
- **Type Checking**: Ensures values are of correct types (list, bool, int).
- **Enums**: Validates against allowed values:
  - `EXPERIENCE_LEVELS`: internship, entry, associate, etc.
  - `JOB_TYPES`: full_time, contract, part_time, etc.
  - `DATE_FILTERS`: all_time, month, week, 24_hours.
  - `APPROVED_DISTANCES`: 0, 5, 10, 25, 50, 100.
- **Email Validation**: Regex checking for email formats.

## File Manager (`main.py`)

The `FileManager` class handles the filesystem interface.
- **`validate_data_folder`**: Ensures `data_folder` exists and contains all required YAML files.
- Creates the `output` directory if it doesn't exist.
