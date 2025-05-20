"""
This creates the cover letter (in html, utils will then convert in PDF) matching with job description and plain-text resume
"""
# app/libs/resume_and_cover_builder/llm_generate_cover_letter_from_job.py
import textwrap
from ..utils import LoggerChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pathlib import Path
from dotenv import load_dotenv
from requests.exceptions import HTTPError as HTTPStatusError
from loguru import logger
import time

# Load environment variables from .env file
load_dotenv()


def configure_logging() -> None:
    """
    Configure logging for the module.
    Creates a rotating log file in a structured folder.
    """
    log_folder: Path = Path('log/cover_letter/gpt_cover_letter_job_descr')
    log_folder.mkdir(parents=True, exist_ok=True)

    log_path = Path(log_folder).resolve()
    logger.add(
        log_path / "gpt_cover_letter_job_descr.log",
        rotation="1 day",
        compression="zip",
        retention="7 days",
        backtrace=True,
        diagnose=True,
        level="DEBUG",
    )

# Configure logging.
configure_logging()


class LLMCoverLetterJobDescription:
    """
    This class generates a cover letter based on a job description and a resume.
    """
    def __init__(self, openai_api_key, strings):
        if not openai_api_key:
            raise ValueError("OpenAI API key is required.")
        self.llm_cheap = LoggerChatModel(ChatOpenAI(model_name="gpt-4o-mini", openai_api_key=openai_api_key, temperature=0.4))
        self.llm_embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.strings = strings

    @staticmethod
    def _preprocess_template_string(template: str, dedent: bool = True) -> str:
        """
        Preprocess the template string by removing leading whitespace and indentation.

        Args:
            template (str): The template string to preprocess.

        Returns:
            str: The preprocessed template string.
        """
        return textwrap.dedent(template) if dedent else template.strip()

    def set_resume(self, resume: str) -> None:
        """
        Set the resume text to be used for generating the cover letter.

        Args:
            resume (str): The plain text resume to be used.
        """
        self.resume = resume

    def set_job_description_from_text(self, job_description_text) -> None:
        """
        Set the job description text to be used for generating the cover letter.

        Args:
            job_description_text (str): The plain text job description to be used.
        """
        logger.debug("Starting job description summarization...")
        prompt = ChatPromptTemplate.from_template(self.strings.summarize_prompt_template)
        chain = prompt | self.llm_cheap | StrOutputParser()
        for _ in range(3):
            try:
                output = chain.invoke({"text": job_description_text})
                break
            except HTTPStatusError as e:
                logger.warning("Retrying job description summarization...")
                time.sleep(2)
            except Exception as e:
                logger.error(f"Error during job description summarization: {e}")
                raise
        else:
            logger.error("Failed to summarize job description after 3 attempts.")
            raise
        self.job_description = output
        logger.debug(f"Job description summarization complete: {self.job_description}")

    def generate_cover_letter(self) -> str:
        """
        Generate the cover letter based on the job description and resume.

        Returns:
            str: The generated cover letter
        """
        logger.debug("Starting cover letter generation...")
        prompt_template = self._preprocess_template_string(self.strings.cover_letter_template)
        logger.debug(f"Cover letter template after preprocessing: {prompt_template}")

        prompt = ChatPromptTemplate.from_template(prompt_template)
        logger.debug(f"Prompt created: {prompt}")

        chain = prompt | self.llm_cheap | StrOutputParser()
        logger.debug(f"Chain created: {chain}")

        input_data = {
            "job_description": self.job_description,
            "resume": self.resume
        }
        logger.debug(f"Input data: {input_data}")
        try:
            output = chain.invoke(input_data)
        except Exception as e:
            logger.error(f"Error during cover letter generation: {e}")
            raise
        logger.debug(f"Cover letter generation result: {output}")

        logger.debug("Cover letter generation completed")
        return output
