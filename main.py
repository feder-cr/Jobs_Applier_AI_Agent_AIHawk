import base64
from pathlib import Path
from functools import lru_cache
from traceback import format_exc
from typing import Dict, List, Tuple
from threading import Lock

import click
import inquirer
import yaml
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import re
from src.libs.resume_and_cover_builder import ResumeFacade, ResumeGenerator, StyleManager
from src.libs.resume_versioning import ResumeVersionManager
from src.resume_schemas.job_application_profile import JobApplicationProfile
from src.resume_schemas.resume import Resume
from src.logging import logger
from src.utils.chrome_utils import init_browser
from src.utils.constants import (
    PLAIN_TEXT_RESUME_YAML,
    SECRETS_YAML,
    WORK_PREFERENCES_YAML,
)
# from ai_hawk.bot_facade import AIHawkBotFacade
# from ai_hawk.job_manager import AIHawkJobManager
# from ai_hawk.llm.llm_manager import GPTAnswerer

driver_lock = Lock()


def get_thread_safe_driver() -> webdriver.Chrome:
    """
    Get a thread-safe instance of the Chrome WebDriver.

    Returns:
        webdriver.Chrome: A thread-safe instance of the Chrome WebDriver.
    """
    with driver_lock:
        return init_browser()


def validate_file_existence(file_path: Path, error_message: str = None) -> None:
    """Validate the existence of a file."""
    error_message = f"File not found: {file_path}" if error_message is None else error_message
    if not file_path.exists():
        raise FileNotFoundError(error_message)


@lru_cache(maxsize=None)
def get_email_regex() -> re.Pattern:
    """
    Get the email regular expression.

    Returns:
        re.Pattern: The compiled regular expression.
    """
    return re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


@lru_cache(maxsize=128)
def load_yaml_file(yaml_path: Path) -> dict:
    try:
        with open(yaml_path, "r") as stream:
            return yaml.safe_load(stream, Loader=yaml.CLoader)
    except yaml.YAMLError as e:
        raise ConfigError(f"Error reading YAML file {yaml_path}: {e}")
    except FileNotFoundError:
        raise ConfigError(f"YAML file not found: {yaml_path}")


class ConfigError(Exception):
    """
    Custom exception for configuration-related errors.
    This class inherits from the built-in Exception class.
    """
    pass


class ConfigValidator:
    """Validates configuration and secrets YAML files."""

    EMAIL_REGEX = get_email_regex()
    REQUIRED_CONFIG_KEYS = {
        "remote": bool,
        "experience_level": dict,
        "job_types": dict,
        "date": dict,
        "positions": list,
        "locations": list,
        "location_blacklist": list,
        "distance": int,
        "company_blacklist": list,
        "title_blacklist": list,
    }
    EXPERIENCE_LEVELS = [
        "internship",
        "entry",
        "associate",
        "mid_senior_level",
        "director",
        "executive",
    ]
    JOB_TYPES = [
        "full_time",
        "contract",
        "part_time",
        "temporary",
        "internship",
        "other",
        "volunteer",
    ]
    DATE_FILTERS = frozenset(["all_time", "month", "week", "24_hours"])
    APPROVED_DISTANCES = {0, 5, 10, 25, 50, 100}

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate the format of an email address.

        Args:
            email (str): The email address to validate.

        Returns:
            bool: True if the email is valid, False otherwise.
        """
        return bool(ConfigValidator.EMAIL_REGEX.match(email))

    @staticmethod
    def load_yaml(yaml_path: Path) -> dict:
        """Load and parse a YAML file."""
        try:
            with open(yaml_path, "r", encoding="utf-8") as stream:
                return yaml.safe_load(stream)
        except yaml.YAMLError as e:
            raise ConfigError(f"Error reading YAML file {yaml_path}: {e}")
        except FileNotFoundError:
            raise ConfigError(f"YAML file not found: {yaml_path}")

    @classmethod
    def validate_config(cls, config_yaml_path: Path) -> dict:
        """Validate the main configuration YAML file."""
        parameters = load_yaml_file(config_yaml_path)
        # Check for required keys and their types
        for key, expected_type in cls.REQUIRED_CONFIG_KEYS.items():
            if key not in parameters:
                if key in ["company_blacklist", "title_blacklist", "location_blacklist"]:
                    parameters[key] = []
                else:
                    raise ConfigError(f"Missing required key '{key}' in {config_yaml_path}")
            elif not isinstance(parameters[key], expected_type):
                if key in ["company_blacklist", "title_blacklist", "location_blacklist"] and parameters[key] is None:
                    parameters[key] = []
                else:
                    raise ConfigError(
                        f"Invalid type for key '{key}' in {config_yaml_path}. Expected {expected_type.__name__}."
                    )
        cls._validate_experience_levels(parameters["experience_level"], config_yaml_path)
        cls._validate_job_types(parameters["job_types"], config_yaml_path)
        cls._validate_date_filters(parameters["date"], config_yaml_path)
        cls._validate_list_of_strings(parameters, ["positions", "locations"], config_yaml_path)
        cls._validate_distance(parameters["distance"], config_yaml_path)
        cls._validate_blacklists(parameters, config_yaml_path)
        return parameters

    @classmethod
    def _validate_experience_levels(cls, experience_levels: dict, config_path: Path):
        """Ensure experience levels are booleans."""
        for level in cls.EXPERIENCE_LEVELS:
            if not isinstance(experience_levels.get(level), bool):
                raise ConfigError(
                    f"Experience level '{level}' must be a boolean in {config_path}"
                )

    @classmethod
    def _validate_job_types(cls, job_types: dict, config_path: Path):
        """
        Ensure job types are booleans.

        Args:
            job_types (dict): Dictionary of job types.
            config_path (Path): Path to the configuration file for validation.
        """
        for job_type in cls.JOB_TYPES:
            if not isinstance(job_types.get(job_type), bool):
                raise ConfigError(
                    f"Job type '{job_type}' must be a boolean in {config_path}"
                )

    @classmethod
    def _validate_date_filters(cls, date_filters: dict, config_path: Path):
        """
        Ensure date filters are booleans.

        Args:
            date_filters (dict): Dictionary of date filters.
            config_path (Path): Path to the configuration file for validation.
        """
        for date_filter in cls.DATE_FILTERS:
            if not isinstance(date_filters.get(date_filter), bool):
                raise ConfigError(
                    f"Date filter '{date_filter}' must be a boolean in {config_path}"
                )

    @classmethod
    def _validate_list_of_strings(cls, parameters: dict, keys: list, config_path: Path):
        """
        Ensure specified keys are lists of strings.

        Args:
            parameters (dict): Dictionary of configuration parameters.
            keys (list): List of keys to validate.
            config_path (Path): Path to the configuration file for validation.
        """
        for key in keys:
            if not all(isinstance(item, str) for item in parameters[key]):
                raise ConfigError(
                    f"'{key}' must be a list of strings in {config_path}"
                )

    @classmethod
    def _validate_distance(cls, distance: int, config_path: Path):
        """Validate the distance value."""
        if distance not in cls.APPROVED_DISTANCES:
            raise ConfigError(
                f"Invalid distance value '{distance}' in {config_path}. Must be one of: {cls.APPROVED_DISTANCES}"
            )

    @classmethod
    def _validate_blacklists(cls, parameters: dict, config_path: Path):
        """Ensure blacklists are lists."""
        for blacklist in ["company_blacklist", "title_blacklist", "location_blacklist"]:
            blacklist_value = parameters.get(blacklist)
            if not isinstance(blacklist_value, list):
                raise ConfigError(
                    f"'{blacklist}' must be a list in {config_path}"
                )
            if blacklist_value is None:
                parameters[blacklist] = []

    @staticmethod
    def validate_secrets(secrets_yaml_path: Path) -> str:
        """Validate the secrets YAML file and retrieve the LLM API key."""
        secrets = ConfigValidator.load_yaml(secrets_yaml_path)
        mandatory_secrets = ["llm_api_key"]

        for secret in mandatory_secrets:
            if secret not in secrets:
                raise ConfigError(f"Missing secret '{secret}' in {secrets_yaml_path}")

            if not secrets[secret]:
                raise ConfigError(f"Secret '{secret}' cannot be empty in {secrets_yaml_path}")

        return secrets["llm_api_key"]


class FileManager:
    """Handles file system operations and validations."""

    REQUIRED_FILES = [SECRETS_YAML, WORK_PREFERENCES_YAML, PLAIN_TEXT_RESUME_YAML]

    @staticmethod
    def validate_data_folder(app_data_folder: Path) -> Tuple[Path, Path, Path, Path]:
        """Validate the existence of the data folder and required files."""
        if not app_data_folder.is_dir():
            raise FileNotFoundError(f"Data folder not found: {app_data_folder}")
        app_data_folder_files = [file.name for file in app_data_folder.iterdir()]
        missing_files = [file for file in FileManager.REQUIRED_FILES if file not in app_data_folder_files]
        if missing_files:
            raise FileNotFoundError(f"Missing files in data folder: {', '.join(missing_files)}")

        output_folder = app_data_folder / "output"
        output_folder.mkdir(exist_ok=True)

        return (
            app_data_folder / SECRETS_YAML,
            app_data_folder / WORK_PREFERENCES_YAML,
            app_data_folder / PLAIN_TEXT_RESUME_YAML,
            output_folder,
        )

    @staticmethod
    def get_uploads(plain_text_resume_file: Path) -> Dict[str, Path]:
        """
        Convert resume file paths to a dictionary.

        Args:
            plain_text_resume_file (Path): Path to the plain text resume file.

        Raises:
            FileNotFoundError: If the file at `plain_text_resume_file` does not exist.

        Returns:
            Dict[str, Path]: A dictionary containing the upload name as the key and the file path as the value.
                The dictionary will include a key `'plainTextResume'` and the provided `plain_text_resume_file`
                path as the value.
        """
        error_message = f"Plain text resume file not found. Expected at: {plain_text_resume_file}"
        validate_file_existence(plain_text_resume_file, error_message)

        uploads = {"plainTextResume": plain_text_resume_file}

        return uploads


def create_resume_with_cover_letter(parameters: dict, llm_api_key: str) -> None:
    """
    Logic to create a CV and cover letter.

    Args:
        parameters (dict): Configuration parameters.
        llm_api_key (str): API key for the language model.
    """
    try:
        logger.info("Generating a CV based on provided parameters.")

        # Carica il resume in testo semplice
        with open(parameters["uploads"]["plainTextResume"], "r", encoding="utf-8") as file:
            plain_text_resume = file.read()

        style_manager = StyleManager()
        available_styles = style_manager.get_styles()

        if not available_styles:
            logger.warning(
                "No styles available due to an empty styles dictionary. "
                "Proceeding without style selection."
            )
        else:
            # Present style choices to the user
            choices = style_manager.format_choices(available_styles)
            questions = [
                inquirer.List(
                    "style",
                    message="Select a style for the resume:",
                    choices=choices,
                )
            ]
            style_answer = inquirer.prompt(questions)
            if style_answer and "style" in style_answer:
                selected_choice = style_answer["style"]
                for style_name, (file_name, author_link) in available_styles.items():
                    if selected_choice.startswith(style_name):
                        style_manager.set_selected_style(style_name)
                        logger.info(f"Selected style: {style_name}")
                        break
            else:
                logger.warning("No style selected. Proceeding with default style.")
        questions = [
            inquirer.Text('job_url', message="Please enter the URL of the job description:")
        ]
        job_url = inquirer.prompt(questions).get('job_url')
        resume_generator = ResumeGenerator()
        resume_object = Resume(plain_text_resume)
        driver = get_thread_safe_driver()
        resume_generator.set_resume_object(resume_object)
        resume_facade = ResumeFacade(
            api_key=llm_api_key,
            style_manager=style_manager,
            resume_generator=resume_generator,
            resume_object=resume_object,
            output_path=Path("data_folder/output"),
        )
        resume_facade.set_driver(driver)
        resume_facade.link_to_job(job_url)
        result_base64, suggested_name = resume_facade.create_cover_letter()

        # Decodifica Base64 in dati binari
        try:
            pdf_data = base64.b64decode(result_base64)
        except base64.binascii.Error as e:
            logger.error("Error decoding Base64: %s", e)
            raise

        # Definisci il percorso della cartella di output utilizzando `suggested_name`
        output_dir = Path(parameters["outputFileDirectory"]) / suggested_name

        # Crea la cartella se non esiste
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Cartella di output creata o già esistente: {output_dir}")
        except IOError as e:
            logger.error("Error creating output directory: %s", e)
            raise

        output_path = output_dir / "cover_letter_tailored.pdf"
        try:
            with open(output_path, "wb") as file:
                file.write(pdf_data)
            logger.info(f"CV salvato in: {output_path}")
        except IOError as e:
            logger.error("Error writing file: %s", e)
            raise
    except Exception as e:
        logger.exception(f"An error occurred while creating the CV: {e}")
        raise


def create_resume_pdf_job_tailored(parameters: dict, llm_api_key: str):
    """
    Logic to create a job tailored CV.

    Args:
        parameters (dict): Configuration parameters.
        llm_api_key (str): API key for the language model.
    """
    try:
        logger.info("Generating a CV based on provided parameters.")

        # Carica il resume in testo semplice
        with open(parameters["uploads"]["plainTextResume"], "r", encoding="utf-8") as file:
            plain_text_resume = file.read()

        style_manager = StyleManager()
        available_styles = lru_cache(maxsize=128)(style_manager.get_styles())

        if not available_styles:
            logger.warning("No styles available. Proceeding without style selection.")
        else:
            # Present style choices to the user
            choices = style_manager.format_choices(available_styles)
            questions = [
                inquirer.List(
                    "style",
                    message="Select a style for the resume:",
                    choices=choices,
                )
            ]
            style_answer = inquirer.prompt(questions)
            if style_answer and "style" in style_answer:
                selected_choice = style_answer["style"]
                for style_name, (file_name, author_link) in available_styles.items():
                    if selected_choice.startswith(style_name):
                        style_manager.set_selected_style(style_name)
                        logger.info(f"Selected style: {style_name}")
                        break
            else:
                logger.warning("No style selected. Proceeding with default style.")
        questions = [inquirer.Text('job_url', message="Please enter the URL of the job description:")]
        answers = inquirer.prompt(questions)
        job_url = answers.get('job_url')
        resume_generator = ResumeGenerator()
        resume_object = Resume(plain_text_resume)
        driver = get_thread_safe_driver()
        resume_generator.set_resume_object(resume_object)
        resume_facade = ResumeFacade(
            api_key=llm_api_key,
            style_manager=style_manager,
            resume_generator=resume_generator,
            resume_object=resume_object,
            output_path=Path("data_folder/output"),
        )
        resume_facade.set_driver(driver)
        resume_facade.link_to_job(job_url)
        result_base64, suggested_name = resume_facade.create_resume_pdf_job_tailored()

        # Decodifica Base64 in dati binari
        try:
            pdf_data = base64.b64decode(result_base64)
        except base64.binascii.Error as e:
            logger.error("Error decoding Base64: %s", e)
            raise

        # Definisci il percorso della cartella di output utilizzando `suggested_name`
        output_dir = Path(parameters["outputFileDirectory"]).joinpath(suggested_name)

        # Crea la cartella se non esiste
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Cartella di output creata o già esistente: {output_dir}")
        except IOError as e:
            logger.error("Error creating output directory: %s", e)
            raise

        output_path = output_dir / "resume_tailored.pdf"
        try:
            with open(output_path, "wb") as file:
                file.write(pdf_data)
            logger.info(f"CV salvato in: {output_path}")
        except IOError as e:
            logger.error("Error writing file: %s", e)
            raise
    except Exception as e:
        logger.exception(f"An error occurred while creating the CV: {e}")
        raise


def create_resume_pdf(parameters: dict, llm_api_key: str):
    """
    Logic to create a CV.

    Args:
        parameters (dict): Configuration parameters.
        llm_api_key (str): API key for the language model.
    """
    try:
        logger.info("Generating a CV based on provided parameters.")

        # Load the plain text resume
        with open(parameters["uploads"]["plainTextResume"], "r", encoding="utf-8") as file:
            plain_text_resume = file.read()

        # Initialize StyleManager
        style_manager = StyleManager()
        available_styles = style_manager.get_styles()

        # Check if styles are available
        if not available_styles:
            logger.warning("No styles available. Proceeding without style selection.")
        else:
            # Present style choices to the user
            choices = style_manager.format_choices(available_styles)
            questions = [
                inquirer.List(
                    "style",
                    message="Select a style for the resume:",
                    choices=choices,
                )
            ]
            style_answer = inquirer.prompt(questions)
            if style_answer and "style" in style_answer:
                selected_choice = style_answer["style"]
                for style_name, (file_name, author_link) in available_styles.items():
                    if selected_choice.startswith(style_name):
                        style_manager.set_selected_style(style_name)
                        logger.info(f"Selected style: {style_name}")
                        break
            else:
                logger.warning("No style selected. Proceeding with default style.")

        # Initialize the Resume Generator
        resume_generator = ResumeGenerator()
        resume_object = Resume(plain_text_resume)
        driver = init_browser()
        resume_generator.set_resume_object(resume_object)

        # Create the ResumeFacade
        resume_facade = ResumeFacade(
            api_key=llm_api_key,
            style_manager=style_manager,
            resume_generator=resume_generator,
            resume_object=resume_object,
            output_path=Path("data_folder/output"),
        )
        resume_facade.set_driver(driver)
        result_base64 = resume_facade.create_resume_pdf()

        # Decode Base64 to binary data
        try:
            pdf_data = base64.b64decode(result_base64)
        except base64.binascii.Error as e:
            logger.error("Error decoding Base64: %s", e)
            raise

        # Define the output directory using `suggested_name`
        output_dir = Path(parameters["outputFileDirectory"])

        # Write the PDF file
        output_path = output_dir / "resume_base.pdf"
        try:
            with open(output_path, "wb") as file:
                file.write(pdf_data)
            logger.info(f"CV saved at: {output_path}")
        except IOError as e:
            logger.error("Error writing file: %s", e)
            raise
    except Exception as e:
        logger.exception(
            "An error occurred while creating the CV. "
            "Ensure all input data and configuration are correct.",
            exc_info=True
        )
        raise


def handle_inquiries(selected_actions: List[str], parameters: dict, llm_api_key: str):
    """
    Decide which function to call based on the selected user actions.

    Args:
        selected_actions (List[str]): List of actions selected by the user.
        parameters (dict): Configuration parameters dictionary.
        llm_api_key (str): API key for the language model.
    """
    try:
        if selected_actions:
            if "Generate Resume" == selected_actions:
                logger.info("Crafting a standout professional resume...")
                create_resume_pdf(parameters, llm_api_key)

            elif "Generate Resume Tailored for Job Description" == selected_actions:
                logger.info("Customizing your resume to enhance your job application...")
                create_resume_pdf_job_tailored(parameters, llm_api_key)

            elif "Generate Tailored Cover Letter for Job Description" == selected_actions:
                logger.info("Designing a personalized cover letter to enhance your job application...")
                create_resume_with_cover_letter(parameters, llm_api_key)

            elif "Manage Resume Versions" == selected_actions:
                logger.info("Managing resume versions...")
                manage_resume_versions(parameters)

        else:
            logger.warning("No actions selected. Nothing to execute.")
    except Exception as e:
        logger.exception(f"An error occurred while handling inquiries: {e}")
        raise


def manage_resume_versions(parameters: dict) -> None:
    """
    Handle resume versioning operations.

    Args:
        parameters (dict): Configuration parameters.
    """
    try:
        version_manager = ResumeVersionManager()

        while True:
            questions = [
                inquirer.List(
                    'version_action',
                    message="Select a resume versioning action:",
                    choices=[
                        "Create New Version",
                        "List All Versions",
                        "Set Active Version",
                        "Compare Versions",
                        "Clone Version",
                        "Export Version",
                        "Import Version",
                        "Delete Version",
                        "View Statistics",
                        "Back to Main Menu"
                    ],
                ),
            ]
            answer = inquirer.prompt(questions)
            if not answer or answer.get('version_action') == "Back to Main Menu":
                break

            action = answer.get('version_action')

            if action == "Create New Version":
                _create_resume_version(version_manager, parameters)
            elif action == "List All Versions":
                _list_resume_versions(version_manager)
            elif action == "Set Active Version":
                _set_active_version(version_manager)
            elif action == "Compare Versions":
                _compare_versions(version_manager)
            elif action == "Clone Version":
                _clone_version(version_manager)
            elif action == "Export Version":
                _export_version(version_manager, parameters)
            elif action == "Import Version":
                _import_version(version_manager)
            elif action == "Delete Version":
                _delete_version(version_manager)
            elif action == "View Statistics":
                _view_statistics(version_manager)

    except Exception as e:
        logger.exception(f"Error in resume versioning: {e}")


def _create_resume_version(version_manager: ResumeVersionManager, parameters: dict) -> None:
    """Create a new resume version."""
    try:
        # Load current resume
        with open(parameters["uploads"]["plainTextResume"], "r", encoding="utf-8") as file:
            resume_content = yaml.safe_load(file)

        # Get version details from user
        questions = [
            inquirer.Text('name', message="Enter version name:"),
            inquirer.Text('description', message="Enter version description (optional):"),
            inquirer.Text('tags', message="Enter tags (comma-separated, optional):"),
        ]
        answers = inquirer.prompt(questions)

        if not answers or not answers.get('name'):
            logger.warning("Version name is required")
            return

        name = answers['name']
        description = answers.get('description', '')
        tags = [tag.strip() for tag in answers.get('tags', '').split(',') if tag.strip()]

        version = version_manager.create_version(resume_content, name, description, tags)
        if version:
            logger.info(f"Created version: {name}")
            print(f"✓ Successfully created version '{name}' with ID: {version.version_id}")
        else:
            logger.error("Failed to create version")
            print("✗ Failed to create version")

    except Exception as e:
        logger.error(f"Error creating version: {e}")
        print(f"✗ Error creating version: {e}")


def _list_resume_versions(version_manager: ResumeVersionManager) -> None:
    """List all resume versions."""
    try:
        versions = version_manager.list_versions()

        if not versions:
            print("No resume versions found.")
            return

        print(f"\nFound {len(versions)} resume versions:")
        print("-" * 80)

        for version in versions:
            status = " [ACTIVE]" if version.is_active else ""
            tags_str = f" (Tags: {', '.join(version.tags)})" if version.tags else ""
            print(f"• {version.name}{status}")
            print(f"  ID: {version.version_id}")
            print(f"  Created: {version.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            if version.description:
                print(f"  Description: {version.description}")
            print(f"  Tags: {', '.join(version.tags) if version.tags else 'None'}")
            print()

    except Exception as e:
        logger.error(f"Error listing versions: {e}")
        print(f"✗ Error listing versions: {e}")


def _set_active_version(version_manager: ResumeVersionManager) -> None:
    """Set a version as active."""
    try:
        versions = version_manager.list_versions()

        if not versions:
            print("No versions available.")
            return

        choices = [f"{v.name} ({v.version_id[:8]}...)" for v in versions]
        questions = [
            inquirer.List(
                'version',
                message="Select version to set as active:",
                choices=choices,
            ),
        ]
        answer = inquirer.prompt(questions)

        if not answer:
            return

        selected_choice = answer['version']
        version_id = None

        for i, choice in enumerate(choices):
            if choice == selected_choice:
                version_id = versions[i].version_id
                break

        if version_id and version_manager.set_active_version(version_id):
            print(f"✓ Set version as active: {versions[i].name}")
        else:
            print("✗ Failed to set active version")

    except Exception as e:
        logger.error(f"Error setting active version: {e}")
        print(f"✗ Error setting active version: {e}")


def _compare_versions(version_manager: ResumeVersionManager) -> None:
    """Compare two versions."""
    try:
        versions = version_manager.list_versions()

        if len(versions) < 2:
            print("Need at least 2 versions to compare.")
            return

        choices = [f"{v.name} ({v.version_id[:8]}...)" for v in versions]

        questions = [
            inquirer.List('version1', message="Select first version:", choices=choices),
            inquirer.List('version2', message="Select second version:", choices=choices),
        ]
        answers = inquirer.prompt(questions)

        if not answers:
            return

        # Find version IDs
        version1_id = version2_id = None
        for i, choice in enumerate(choices):
            if choice == answers['version1']:
                version1_id = versions[i].version_id
            if choice == answers['version2']:
                version2_id = versions[i].version_id

        if version1_id == version2_id:
            print("Cannot compare a version with itself.")
            return

        comparison = version_manager.compare_versions(version1_id, version2_id)
        if comparison:
            print(f"\nComparison Results:")
            print(f"Similarity: {comparison.similarity_score:.1%}")
            print(f"Differences found: {len(comparison.differences)}")

            if comparison.differences:
                print("\nKey differences:")
                for key, diff in list(comparison.differences.items())[:5]:  # Show first 5
                    print(f"  • {key}: '{diff['version1']}' → '{diff['version2']}'")
                if len(comparison.differences) > 5:
                    print(f"  ... and {len(comparison.differences) - 5} more differences")
        else:
            print("✗ Failed to compare versions")

    except Exception as e:
        logger.error(f"Error comparing versions: {e}")
        print(f"✗ Error comparing versions: {e}")


def _clone_version(version_manager: ResumeVersionManager) -> None:
    """Clone an existing version."""
    try:
        versions = version_manager.list_versions()

        if not versions:
            print("No versions available to clone.")
            return

        choices = [f"{v.name} ({v.version_id[:8]}...)" for v in versions]
        questions = [
            inquirer.List('version', message="Select version to clone:", choices=choices),
            inquirer.Text('new_name', message="Enter name for cloned version:"),
            inquirer.Text('new_description', message="Enter description for cloned version (optional):"),
        ]
        answers = inquirer.prompt(questions)

        if not answers or not answers.get('new_name'):
            print("Clone name is required.")
            return

        # Find version ID
        version_id = None
        for i, choice in enumerate(choices):
            if choice == answers['version']:
                version_id = versions[i].version_id
                break

        cloned = version_manager.clone_version(
            version_id,
            answers['new_name'],
            answers.get('new_description', '')
        )

        if cloned:
            print(f"✓ Successfully cloned version: {answers['new_name']}")
        else:
            print("✗ Failed to clone version")

    except Exception as e:
        logger.error(f"Error cloning version: {e}")
        print(f"✗ Error cloning version: {e}")


def _export_version(version_manager: ResumeVersionManager, parameters: dict) -> None:
    """Export a version to file."""
    try:
        versions = version_manager.list_versions()

        if not versions:
            print("No versions available to export.")
            return

        choices = [f"{v.name} ({v.version_id[:8]}...)" for v in versions]
        questions = [
            inquirer.List('version', message="Select version to export:", choices=choices),
            inquirer.Text('filename', message="Enter export filename (without extension):"),
        ]
        answers = inquirer.prompt(questions)

        if not answers or not answers.get('filename'):
            print("Filename is required.")
            return

        # Find version ID
        version_id = None
        for i, choice in enumerate(choices):
            if choice == answers['version']:
                version_id = versions[i].version_id
                break

        export_path = Path(parameters["outputFileDirectory"]) / f"{answers['filename']}.zip"

        if version_manager.export_version(version_id, export_path):
            print(f"✓ Successfully exported version to: {export_path}")
        else:
            print("✗ Failed to export version")

    except Exception as e:
        logger.error(f"Error exporting version: {e}")
        print(f"✗ Error exporting version: {e}")


def _import_version(version_manager: ResumeVersionManager) -> None:
    """Import a version from file."""
    try:
        questions = [
            inquirer.Text('import_path', message="Enter path to import file (.zip):"),
            inquirer.Text('new_name', message="Enter name for imported version (optional):"),
        ]
        answers = inquirer.prompt(questions)

        if not answers or not answers.get('import_path'):
            print("Import path is required.")
            return

        import_path = Path(answers['import_path'])
        new_name = answers.get('new_name') or None

        version = version_manager.import_version(import_path, new_name)
        if version:
            print(f"✓ Successfully imported version: {version.name}")
        else:
            print("✗ Failed to import version")

    except Exception as e:
        logger.error(f"Error importing version: {e}")
        print(f"✗ Error importing version: {e}")


def _delete_version(version_manager: ResumeVersionManager) -> None:
    """Delete a version."""
    try:
        versions = version_manager.list_versions()

        if not versions:
            print("No versions available to delete.")
            return

        # Filter out active versions
        deletable_versions = [v for v in versions if not v.is_active]

        if not deletable_versions:
            print("No deletable versions (cannot delete active version).")
            return

        choices = [f"{v.name} ({v.version_id[:8]}...)" for v in deletable_versions]
        questions = [
            inquirer.List('version', message="Select version to delete:", choices=choices),
            inquirer.Confirm('confirm', message="Are you sure you want to delete this version?", default=False),
        ]
        answers = inquirer.prompt(questions)

        if not answers or not answers.get('confirm'):
            print("Delete cancelled.")
            return

        # Find version ID
        version_id = None
        for i, choice in enumerate(choices):
            if choice == answers['version']:
                version_id = deletable_versions[i].version_id
                break

        if version_manager.delete_version(version_id):
            print(f"✓ Successfully deleted version")
        else:
            print("✗ Failed to delete version")

    except Exception as e:
        logger.error(f"Error deleting version: {e}")
        print(f"✗ Error deleting version: {e}")


def _view_statistics(version_manager: ResumeVersionManager) -> None:
    """View version statistics."""
    try:
        stats = version_manager.get_version_statistics()

        print("\nResume Version Statistics:")
        print("-" * 40)
        print(f"Total versions: {stats['total_versions']}")

        if stats['total_versions'] > 0:
            print(f"Active version: {stats.get('active_version', 'None')}")
            print(f"Total storage size: {stats['total_storage_size']} bytes")
            print(f"Average version size: {stats['average_version_size']:.0f} bytes")
            print(f"Oldest version: {stats['oldest_version']}")
            print(f"Newest version: {stats['newest_version']}")

            if stats['tag_counts']:
                print("\nTag usage:")
                for tag, count in stats['tag_counts'].items():
                    print(f"  • {tag}: {count} version(s)")

    except Exception as e:
        logger.error(f"Error viewing statistics: {e}")
        print(f"✗ Error viewing statistics: {e}")


def prompt_user_action() -> str:
    """
    Use inquirer to ask the user which action they want to perform.

    :return: Selected action.
    """
    try:
        questions = [
            inquirer.List(
                'action',
                message="Select the action you want to perform:",
                choices=[
                    "Generate Resume",
                    "Generate Resume Tailored for Job Description",
                    "Generate Tailored Cover Letter for Job Description",
                    "Manage Resume Versions",
                ],
            ),
        ]
        answer = inquirer.prompt(questions)
        if answer is None:
            print("No answer provided. The user may have interrupted.")
            return ""
        return answer.get('action', "")
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""


def main() -> None:
    """Main entry point for the AIHawk Job Application Bot."""
    try:
        # Define and validate the data folder
        data_folder = Path("data_folder")
        secrets_file, config_file, plain_text_resume_file, output_folder = FileManager.validate_data_folder(data_folder)

        # Validate configuration and secrets
        config = ConfigValidator.validate_config(config_file)
        llm_api_key = ConfigValidator.validate_secrets(secrets_file)

        # Prepare parameters
        config["uploads"] = FileManager.get_uploads(plain_text_resume_file)
        config["outputFileDirectory"] = output_folder

        # Interactive prompt for user to select actions
        selected_actions = prompt_user_action()

        # Handle selected actions and execute them
        handle_inquiries(selected_actions, config, llm_api_key)

    except ConfigError as ce:
        logger.error(f"Configuration error: {ce}")
        logger.error(
            "Refer to the configuration guide for troubleshooting: "
            "https://github.com/feder-cr/Auto_Jobs_Applier_AIHawk?tab=readme-ov-file#configuration"
        )
    except FileNotFoundError as fnf:
        logger.error(f"File not found: {fnf}")
        logger.debug("Traceback details", exc_info=True)
        logger.error("Ensure all required files are present in the data folder.")
    except RuntimeError as re:
        logger.error(f"Runtime error: {re}")
        logger.debug(format_exc())
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
