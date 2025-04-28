"""
This module contains the FacadeManager class, which is responsible for managing the interaction between the user and other components of the application.
"""
# app/libs/resume_and_cover_builder/manager_facade.py
import hashlib
import inquirer
from pathlib import Path
import config as cfg

from loguru import logger

from src.libs.resume_and_cover_builder.llm.llm_job_parser import LLMParser
from src.job import Job
from src.utils.chrome_utils import HTML_to_PDF
from .config import global_config

class ResumeFacade:
    def __init__(self, api_key, style_manager, resume_generator, resume_object, output_path):
        """
        Initialize the FacadeManager with the given API key, style manager, resume generator, resume object, and log path.
        Args:
            api_key (str): The OpenAI API key to be used for generating text.
            style_manager (StyleManager): The StyleManager instance to manage the styles.
            resume_generator (ResumeGenerator): The ResumeGenerator instance to generate resumes and cover letters.
            resume_object (str): The resume object to be used for generating resumes and cover letters.
            output_path (str): The path to the log file.
        """
        lib_directory = Path(__file__).resolve().parent
        global_config.STRINGS_MODULE_RESUME_PATH = lib_directory / "resume_prompt/strings_feder-cr.py"
        global_config.STRINGS_MODULE_RESUME_JOB_DESCRIPTION_PATH = lib_directory / "resume_job_description_prompt/strings_feder-cr.py"
        global_config.STRINGS_MODULE_COVER_LETTER_JOB_DESCRIPTION_PATH = lib_directory / "cover_letter_prompt/strings_feder-cr.py"
        global_config.STRINGS_MODULE_NAME = "strings_feder_cr"
        global_config.STYLES_DIRECTORY = lib_directory / "resume_style"
        global_config.LOG_OUTPUT_FILE_PATH = output_path
        global_config.API_KEY = api_key
        self.style_manager = style_manager
        self.resume_generator = resume_generator
        self.resume_generator.set_resume_object(resume_object)
        self.selected_style = None  # Property to store the selected style
    
    def set_driver(self, driver):
         self.driver = driver

    def prompt_user(self, choices: list[str], message: str) -> str:
        """
        Prompt the user with the given message and choices.
        Args:
            choices (list[str]): The list of choices to present to the user.
            message (str): The message to display to the user.
        Returns:
            str: The choice selected by the user.
        """
        questions = [
            inquirer.List('selection', message=message, choices=choices),
        ]
        return inquirer.prompt(questions)['selection']

    def prompt_for_text(self, message: str) -> str:
        """
        Prompt the user to enter text with the given message.
        Args:
            message (str): The message to display to the user.
        Returns:
            str: The text entered by the user.
        """
        questions = [
            inquirer.Text('text', message=message),
        ]
        return inquirer.prompt(questions)['text']

        
    def link_to_job(self, job_url):
        self.driver.get(job_url)
        self.driver.implicitly_wait(10)
        body_element = self.driver.find_element("tag name", "body")
        body_element = body_element.get_attribute("outerHTML")
        self.llm_job_parser = LLMParser(openai_api_key=global_config.API_KEY,
                                        model_name=cfg.LLM_MODEL)
        self.llm_job_parser.set_body_html(body_element)

        self.job = Job()
        self.job.role = self.llm_job_parser.extract_role()
        self.job.company = self.llm_job_parser.extract_company_name()
        self.job.description = self.llm_job_parser.extract_job_description()
        self.job.location = self.llm_job_parser.extract_location()
        self.job.link = job_url
        logger.info(f"Extracting job details from URL: {job_url}")


    def create_resume_pdf_job_tailored(self) -> tuple[bytes, str]:
        """
        Create a resume PDF using the selected style and the given job description text.
        Args:
            job_url (str): The job URL to generate the hash for.
            job_description_text (str): The job description text to include in the resume.
        Returns:
            tuple: A tuple containing the PDF content as bytes and the unique filename.
        """
        style_path = self.style_manager.get_style_path()
        if style_path is None:
            raise ValueError("You must choose a style before generating the PDF.")


        html_resume = self.resume_generator.create_resume_job_description_text(
            style_path, self.job.description, cfg.LLM_MODEL)

        # Generate a unique name using the job URL hash
        suggested_name = hashlib.md5(self.job.link.encode()).hexdigest()[:10]
        
        result = HTML_to_PDF(html_resume, self.driver)
        self.driver.quit()
        return result, suggested_name
    
    
    
    def create_resume_pdf(self) -> tuple[bytes, str]:
        """
        Create a resume PDF using the selected style and the given job description text.
        Args:
            job_url (str): The job URL to generate the hash for.
            job_description_text (str): The job description text to include in the resume.
        Returns:
            tuple: A tuple containing the PDF content as bytes and the unique filename.
        """
        style_path = self.style_manager.get_style_path()
        if style_path is None:
            raise ValueError("You must choose a style before generating the PDF.")
        
        html_resume = self.resume_generator.create_resume(style_path, cfg.LLM_MODEL)
        result = HTML_to_PDF(html_resume, self.driver)
        self.driver.quit()
        return result

    def create_cover_letter(self) -> tuple[bytes, str]:
        """
        Create a cover letter based on the given job description text and job URL.
        Args:
            job_url (str): The job URL to generate the hash for.
            job_description_text (str): The job description text to include in the cover letter.
        Returns:
            tuple: A tuple containing the PDF content as bytes and the unique filename.
        """
        style_path = self.style_manager.get_style_path()
        if style_path is None:
            raise ValueError("You must choose a style before generating the PDF.")
        
        
        cover_letter_html = self.resume_generator.create_cover_letter_job_description(
            style_path, self.job.description, cfg.LLM_MODEL)

        # Generate a unique name using the job URL hash
        suggested_name = hashlib.md5(self.job.link.encode()).hexdigest()[:10]

        
        result = HTML_to_PDF(cover_letter_html, self.driver)
        self.driver.quit()
        return result, suggested_name
