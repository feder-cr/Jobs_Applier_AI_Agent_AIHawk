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
from src.resume_schemas.job_application_profile import JobApplicationProfile
from src.resume_schemas.resume import Resume
from src.resume_versioning import ResumeVersionManager, VersionType, VersionStatus
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


def handle_inquiries(selected_actions: str, parameters: dict, llm_api_key: str):
    """
    Decide which function to call based on the selected user actions.

    Args:
        selected_actions (str): Action selected by the user.
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


def manage_resume_versions(parameters: dict) -> None:
    """
    Main function to manage resume versions.

    Args:
        parameters (dict): Configuration parameters.
    """
    try:
        version_manager = ResumeVersionManager()

        while True:
            questions = [
                inquirer.List(
                    'action',
                    message="Resume Version Management - Select an action:",
                    choices=[
                        "Create New Version",
                        "List All Versions",
                        "View Version Details",
                        "Set Default Version",
                        "Compare Versions",
                        "Duplicate Version",
                        "Archive Version",
                        "Delete Version",
                        "Back to Main Menu",
                    ],
                ),
            ]
            answer = inquirer.prompt(questions)
            if not answer or answer.get('action') == "Back to Main Menu":
                break

            action = answer.get('action')

            if action == "Create New Version":
                create_new_version(version_manager, parameters)
            elif action == "List All Versions":
                list_all_versions(version_manager)
            elif action == "View Version Details":
                view_version_details(version_manager)
            elif action == "Set Default Version":
                set_default_version(version_manager)
            elif action == "Compare Versions":
                compare_versions(version_manager)
            elif action == "Duplicate Version":
                duplicate_version(version_manager)
            elif action == "Archive Version":
                archive_version(version_manager)
            elif action == "Delete Version":
                delete_version(version_manager)

    except Exception as e:
        logger.error(f"Error in resume version management: {e}")


def create_new_version(version_manager: ResumeVersionManager, parameters: dict) -> None:
    """Create a new resume version."""
    try:
        # Get version details from user
        questions = [
            inquirer.Text('name', message="Enter a name for this version:"),
            inquirer.List('type', message="Select version type:",
                         choices=[vt.value for vt in VersionType]),
            inquirer.Text('description', message="Enter a description (optional):"),
            inquirer.Text('tags', message="Enter tags (comma-separated, optional):"),
            inquirer.Text('companies', message="Enter target companies (comma-separated, optional):"),
            inquirer.Text('roles', message="Enter target roles (comma-separated, optional):"),
            inquirer.Text('notes', message="Enter additional notes (optional):"),
        ]

        answers = inquirer.prompt(questions)
        if not answers or not answers.get('name'):
            print("Version creation cancelled.")
            return

        # Load current resume content
        with open(parameters["uploads"]["plainTextResume"], "r", encoding="utf-8") as file:
            resume_content = file.read()

        # Parse lists
        tags = [tag.strip() for tag in answers.get('tags', '').split(',') if tag.strip()]
        companies = [comp.strip() for comp in answers.get('companies', '').split(',') if comp.strip()]
        roles = [role.strip() for role in answers.get('roles', '').split(',') if role.strip()]

        # Create version
        version_id = version_manager.create_version(
            name=answers['name'],
            resume_content=resume_content,
            version_type=VersionType(answers['type']),
            description=answers.get('description', ''),
            tags=tags,
            target_companies=companies,
            target_roles=roles,
            notes=answers.get('notes', '')
        )

        if version_id:
            print(f"✅ Successfully created version: {answers['name']} (ID: {version_id})")
        else:
            print("❌ Failed to create version.")

    except Exception as e:
        logger.error(f"Error creating new version: {e}")
        print(f"❌ Error creating version: {e}")


def list_all_versions(version_manager: ResumeVersionManager) -> None:
    """List all resume versions."""
    try:
        versions = version_manager.list_versions()

        if not versions:
            print("📝 No resume versions found.")
            return

        print("\n📋 Resume Versions:")
        print("-" * 80)

        for version in versions:
            status_icon = "⭐" if version.is_default else "📄"
            status_text = f"({version.status.value.upper()})"

            print(f"{status_icon} {version.name} {status_text}")
            print(f"   ID: {version.version_id}")
            print(f"   Type: {version.version_type.value}")
            print(f"   Created: {version.created_date.strftime('%Y-%m-%d %H:%M')}")
            print(f"   Modified: {version.modified_date.strftime('%Y-%m-%d %H:%M')}")
            if version.description:
                print(f"   Description: {version.description}")
            if version.tags:
                print(f"   Tags: {', '.join(version.tags)}")
            print()

    except Exception as e:
        logger.error(f"Error listing versions: {e}")
        print(f"❌ Error listing versions: {e}")


def view_version_details(version_manager: ResumeVersionManager) -> None:
    """View detailed information about a specific version."""
    try:
        versions = version_manager.list_versions()
        if not versions:
            print("📝 No resume versions found.")
            return

        choices = [f"{v.name} ({v.version_id[:8]}...)" for v in versions]
        questions = [
            inquirer.List('version', message="Select a version to view:", choices=choices)
        ]

        answer = inquirer.prompt(questions)
        if not answer:
            return

        # Extract version ID from choice
        selected_choice = answer['version']
        version_id = None
        for v in versions:
            if selected_choice.startswith(v.name):
                version_id = v.version_id
                break

        if not version_id:
            print("❌ Version not found.")
            return

        metadata = version_manager.get_version(version_id)
        content = version_manager.get_version_content(version_id)

        if not metadata:
            print("❌ Version not found.")
            return

        print(f"\n📄 Version Details: {metadata.name}")
        print("-" * 50)
        print(f"ID: {metadata.version_id}")
        print(f"Type: {metadata.version_type.value}")
        print(f"Status: {metadata.status.value}")
        print(f"Default: {'Yes' if metadata.is_default else 'No'}")
        print(f"Created: {metadata.created_date.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Modified: {metadata.modified_date.strftime('%Y-%m-%d %H:%M:%S')}")

        if metadata.description:
            print(f"Description: {metadata.description}")
        if metadata.tags:
            print(f"Tags: {', '.join(metadata.tags)}")
        if metadata.target_companies:
            print(f"Target Companies: {', '.join(metadata.target_companies)}")
        if metadata.target_roles:
            print(f"Target Roles: {', '.join(metadata.target_roles)}")
        if metadata.notes:
            print(f"Notes: {metadata.notes}")
        if metadata.parent_version_id:
            print(f"Parent Version: {metadata.parent_version_id}")

        # Ask if user wants to see content
        show_content = inquirer.prompt([
            inquirer.Confirm('show', message="Show resume content?", default=False)
        ])

        if show_content and show_content.get('show') and content:
            print(f"\n📝 Resume Content:")
            print("-" * 50)
            print(content[:500] + "..." if len(content) > 500 else content)

    except Exception as e:
        logger.error(f"Error viewing version details: {e}")
        print(f"❌ Error viewing version details: {e}")


def set_default_version(version_manager: ResumeVersionManager) -> None:
    """Set a version as the default."""
    try:
        versions = version_manager.list_versions()
        if not versions:
            print("📝 No resume versions found.")
            return

        choices = [f"{v.name} ({v.version_id[:8]}...)" for v in versions]
        questions = [
            inquirer.List('version', message="Select a version to set as default:", choices=choices)
        ]

        answer = inquirer.prompt(questions)
        if not answer:
            return

        # Extract version ID from choice
        selected_choice = answer['version']
        version_id = None
        for v in versions:
            if selected_choice.startswith(v.name):
                version_id = v.version_id
                break

        if version_id and version_manager.set_default_version(version_id):
            print(f"✅ Successfully set {selected_choice.split(' (')[0]} as default version.")
        else:
            print("❌ Failed to set default version.")

    except Exception as e:
        logger.error(f"Error setting default version: {e}")
        print(f"❌ Error setting default version: {e}")


def compare_versions(version_manager: ResumeVersionManager) -> None:
    """Compare two versions."""
    try:
        versions = version_manager.list_versions()
        if len(versions) < 2:
            print("📝 Need at least 2 versions to compare.")
            return

        choices = [f"{v.name} ({v.version_id[:8]}...)" for v in versions]

        questions = [
            inquirer.List('version1', message="Select first version:", choices=choices),
            inquirer.List('version2', message="Select second version:", choices=choices)
        ]

        answers = inquirer.prompt(questions)
        if not answers:
            return

        # Extract version IDs
        version_id1 = version_id2 = None
        for v in versions:
            if answers['version1'].startswith(v.name):
                version_id1 = v.version_id
            if answers['version2'].startswith(v.name):
                version_id2 = v.version_id

        if not version_id1 or not version_id2:
            print("❌ Invalid version selection.")
            return

        if version_id1 == version_id2:
            print("❌ Cannot compare a version with itself.")
            return

        comparison = version_manager.compare_versions(version_id1, version_id2)
        if not comparison:
            print("❌ Failed to compare versions.")
            return

        print(f"\n🔍 Comparison Results:")
        print("-" * 50)
        print(f"Version 1: {comparison['version1']['name']}")
        print(f"Version 2: {comparison['version2']['name']}")
        print(f"Has Differences: {'Yes' if comparison['has_differences'] else 'No'}")

        if comparison['has_differences']:
            show_diff = inquirer.prompt([
                inquirer.Confirm('show', message="Show detailed differences?", default=False)
            ])

            if show_diff and show_diff.get('show'):
                print("\n📝 Detailed Differences:")
                print("-" * 50)
                for line in comparison['diff'][:20]:  # Show first 20 lines
                    print(line.rstrip())
                if len(comparison['diff']) > 20:
                    print("... (truncated)")

    except Exception as e:
        logger.error(f"Error comparing versions: {e}")
        print(f"❌ Error comparing versions: {e}")


def duplicate_version(version_manager: ResumeVersionManager) -> None:
    """Duplicate an existing version."""
    try:
        versions = version_manager.list_versions()
        if not versions:
            print("📝 No resume versions found.")
            return

        choices = [f"{v.name} ({v.version_id[:8]}...)" for v in versions]
        questions = [
            inquirer.List('version', message="Select a version to duplicate:", choices=choices),
            inquirer.Text('name', message="Enter a name for the new version:")
        ]

        answers = inquirer.prompt(questions)
        if not answers or not answers.get('name'):
            print("Duplication cancelled.")
            return

        # Extract version ID
        selected_choice = answers['version']
        version_id = None
        for v in versions:
            if selected_choice.startswith(v.name):
                version_id = v.version_id
                break

        if not version_id:
            print("❌ Version not found.")
            return

        new_version_id = version_manager.duplicate_version(version_id, answers['name'])
        if new_version_id:
            print(f"✅ Successfully duplicated version: {answers['name']} (ID: {new_version_id})")
        else:
            print("❌ Failed to duplicate version.")

    except Exception as e:
        logger.error(f"Error duplicating version: {e}")
        print(f"❌ Error duplicating version: {e}")


def archive_version(version_manager: ResumeVersionManager) -> None:
    """Archive a version."""
    try:
        versions = [v for v in version_manager.list_versions() if v.status != VersionStatus.ARCHIVED]
        if not versions:
            print("📝 No active versions found.")
            return

        choices = [f"{v.name} ({v.version_id[:8]}...)" for v in versions]
        questions = [
            inquirer.List('version', message="Select a version to archive:", choices=choices)
        ]

        answer = inquirer.prompt(questions)
        if not answer:
            return

        # Extract version ID
        selected_choice = answer['version']
        version_id = None
        for v in versions:
            if selected_choice.startswith(v.name):
                version_id = v.version_id
                break

        if version_id and version_manager.archive_version(version_id):
            print(f"✅ Successfully archived version: {selected_choice.split(' (')[0]}")
        else:
            print("❌ Failed to archive version.")

    except Exception as e:
        logger.error(f"Error archiving version: {e}")
        print(f"❌ Error archiving version: {e}")


def delete_version(version_manager: ResumeVersionManager) -> None:
    """Delete a version."""
    try:
        versions = version_manager.list_versions()
        if not versions:
            print("📝 No resume versions found.")
            return

        choices = [f"{v.name} ({v.version_id[:8]}...)" for v in versions]
        questions = [
            inquirer.List('version', message="Select a version to delete:", choices=choices),
            inquirer.Confirm('backup', message="Create backup before deletion?", default=True),
            inquirer.Confirm('confirm', message="Are you sure you want to delete this version?", default=False)
        ]

        answers = inquirer.prompt(questions)
        if not answers or not answers.get('confirm'):
            print("Deletion cancelled.")
            return

        # Extract version ID
        selected_choice = answers['version']
        version_id = None
        for v in versions:
            if selected_choice.startswith(v.name):
                version_id = v.version_id
                break

        if not version_id:
            print("❌ Version not found.")
            return

        if version_manager.delete_version(version_id, answers.get('backup', True)):
            print(f"✅ Successfully deleted version: {selected_choice.split(' (')[0]}")
        else:
            print("❌ Failed to delete version.")

    except Exception as e:
        logger.error(f"Error deleting version: {e}")
        print(f"❌ Error deleting version: {e}")


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
