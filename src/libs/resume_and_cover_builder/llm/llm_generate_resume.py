"""
Create a class that generates a resume based on a resume and a resume template.
"""
# app/libs/resume_and_cover_builder/gpt_resume.py
import textwrap
from src.libs.resume_schemas.resume import Resume
from src.libs.resume_and_cover_builder.utils import LoggerChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from loguru import logger
from pathlib import Path
from typing import Optional

# Load environment variables from .env file
if not load_dotenv():
    logger.error("Error loading environment variables from .env file")

# Configure log file
log_folder = Path('log/resume/gpt_resume')
log_folder.mkdir(parents=True, exist_ok=True)

# Resolve the log path
log_path = log_folder.resolve()
logger.add(
    log_path / "gpt_resume.log",
    rotation="1 day", compression="zip",
    retention="7 days", level="DEBUG",
    backtrace=True, diagnose=True
)

class LLMResumer:
    def __init__(self, openai_api_key, strings):
        self.llm_cheap = LoggerChatModel(
            ChatOpenAI(
                model_name="gpt-4o-mini",
                openai_api_key=openai_api_key,
                temperature=0.4
            )
        )
        self.strings = strings

    @staticmethod
    def _preprocess_template_string(template: str) -> str:
        """
        Preprocess the template string by removing leading whitespace and indentation.
        Args:
            template (str): The template string to preprocess.
        Returns:
            str: The preprocessed template string.
        """
        return textwrap.dedent(template)

    def set_resume(self, resume: Resume) -> None:
        """
        Set the resume object to be used for generating the resume.
        Args:
            resume (Resume): The resume object to be used.
        """
        self.resume = resume

    def generate_header(self, data: Optional[dict] = None) -> str:
        """
        Generate the header section of the resume.
        Args:
            data (dict): The personal information to use for generating the header.
        Returns:
            str: The generated header section.
        """
        header_prompt_template = self._preprocess_template_string(
            self.strings.prompt_header
        )
        prompt = ChatPromptTemplate.from_template(header_prompt_template)
        chain = prompt | self.llm_cheap | StrOutputParser()
        input_data = data if data is not None else {
            "personal_information": self.resume.personal_information
        }
        logger.debug(f"Input data for the chain: {input_data}")
        try:
            output = chain.invoke(input_data)
        except Exception as e:
            logger.error(f"Error generating header: {e}", exc_info=True)
            return ""
        return output
    
    def generate_education_section(self, data: Optional[dict] = None) -> str:
        """
        Generate the education section of the resume.
        Args:
            data (dict): The education details to use for generating the education section.
        Returns:
            str: The generated education section.
        """
        logger.debug("Starting education section generation")

        education_prompt_template = self._preprocess_template_string(self.strings.prompt_education)
        logger.debug(f"Education template: {education_prompt_template}")

        prompt = ChatPromptTemplate.from_template(education_prompt_template)
        logger.debug(f"Prompt: {prompt}")
        
        chain = prompt | self.llm_cheap | StrOutputParser()
        logger.debug(f"Chain created: {chain}")
        
        input_data = {
            "education_details": self.resume.education_details
        } if data is None else data
        output = chain.invoke(input_data)
        logger.debug(f"Chain invocation result: {output}")

        logger.debug("Education section generation completed")
        return output

    def generate_work_experience_section(self, data: Optional[dict] = None) -> str:
        """
        Generate the work experience section of the resume.
        Args:
            data (dict): The work experience details to use for generating the work experience section.
        Returns:
            str: The generated work experience section.
        """
        logger.debug("Starting work experience section generation")

        work_experience_prompt_template = self._preprocess_template_string(self.strings.prompt_working_experience)
        logger.debug(f"Work experience template: {work_experience_prompt_template}")

        prompt = ChatPromptTemplate.from_template(work_experience_prompt_template)
        logger.debug(f"Prompt: {prompt}")
        
        chain = prompt | self.llm_cheap | StrOutputParser()
        logger.debug(f"Chain created: {chain}")
        
        input_data = {
            "experience_details": self.resume.experience_details
        } if data is None else data
        output = chain.invoke(input_data)
        logger.debug(f"Chain invocation result: {output}")

        logger.debug("Work experience section generation completed")
        return output

    def generate_projects_section(self, data = None) -> str:
        """
        Generate the side projects section of the resume.
        Args:
            data (dict): The side projects to use for generating the side projects section.
        Returns:
            str: The generated side projects section.
        """
        logger.debug("Starting side projects section generation")

        projects_prompt_template = self._preprocess_template_string(self.strings.prompt_projects)
        logger.debug(f"Side projects template: {projects_prompt_template}")

        prompt = ChatPromptTemplate.from_template(projects_prompt_template)
        logger.debug(f"Prompt: {prompt}")
        
        chain = prompt | self.llm_cheap | StrOutputParser()
        logger.debug(f"Chain created: {chain}")
        
        input_data = {
            "projects": self.resume.projects
        } if data is None else data
        output = chain.invoke(input_data)
        logger.debug(f"Chain invocation result: {output}")

        logger.debug("Side projects section generation completed")
        return output

    def generate_achievements_section(self, data: Optional[dict] = None) -> str:
        """
        Generate the achievements section of the resume.
        Args:
            data (dict): The achievements to use for generating the achievements section.
        Returns:
            str: The generated achievements section.
        """
        logger.debug("Starting achievements section generation")

        achievements_prompt_template = self._preprocess_template_string(self.strings.prompt_achievements)
        logger.debug(f"Achievements template: {achievements_prompt_template}")

        prompt = ChatPromptTemplate.from_template(achievements_prompt_template)
        logger.debug(f"Prompt: {prompt}")

        chain = prompt | self.llm_cheap | StrOutputParser()
        logger.debug(f"Chain created: {chain}")

        input_data = {
            "achievements": self.resume.achievements,
            "certifications": self.resume.certifications,
        } if data is None else data
        logger.debug(f"Input data for the chain: {input_data}")

        output = chain.invoke(input_data)
        logger.debug(f"Chain invocation result: {output}")

        logger.debug("Achievements section generation completed")
        return output

    def generate_certifications_section(self, data = None) -> str:
        """
        Generate the certifications section of the resume.
        Args:
            data (dict): The certifications to use for generating the certifications section.
        Returns:
            str: The generated certifications section.
        """
        logger.debug("Starting Certifications section generation")

        certifications_prompt_template = self._preprocess_template_string(self.strings.prompt_certifications)
        logger.debug(f"Certifications template: {certifications_prompt_template}")

        prompt = ChatPromptTemplate.from_template(certifications_prompt_template)
        logger.debug(f"Prompt: {prompt}")

        chain = prompt | self.llm_cheap | StrOutputParser()
        logger.debug(f"Chain created: {chain}")

        input_data = {
            "certifications": self.resume.certifications
        } if data is None else data
        logger.debug(f"Input data for the chain: {input_data}")

        output = chain.invoke(input_data)
        logger.debug(f"Chain invocation result: {output}")

        logger.debug("Certifications section generation completed")
        return output
    
    def generate_additional_skills_section(self, data = None) -> str:
        """
        Generate the additional skills section of the resume.
        Args:
            data (dict): The additional skills to use for generating the additional skills section.
        Returns:
            str: The generated additional skills section.
        """
        additional_skills_prompt_template = self._preprocess_template_string(self.strings.prompt_additional_skills)

        skills = {
            skill for exp in (self.resume.experience_details or []) for skill in exp.skills_acquired
        }

        if self.resume.education_details:
            for edu in self.resume.education_details:
                if edu.exam:
                    for exam in edu.exam:
                        skills.update(exam.keys())
        prompt = ChatPromptTemplate.from_template(additional_skills_prompt_template)
        chain = prompt | self.llm_cheap | StrOutputParser()
        input_data = {
            "languages": self.resume.languages,
            "interests": self.resume.interests,
            "skills": skills,
        } if data is None else data
        output = chain.invoke(input_data)

        return output

    def generate_html_resume(self) -> str:
        """
        Generate the full HTML resume based on the resume object,
        fetching and generating various sections.

        Returns:
            str: The generated HTML resume.
        
        Example:
        
        """

        def generate_section(name: str, condition: bool, generate_fn: callable):
            """
            Returns the HTML content for a section if the condition is true.

            Args:
                name (str): The name of the section.
                condition (bool): The condition to check.
                generate_fn (callable): The function to generate the section content.

            Returns:
                str: The HTML content for the section if the condition is true, otherwise an empty string.
            """
            return generate_fn() if condition else ""

        def header_fn():
            return generate_section(
                "header", bool(self.resume.personal_information), self.generate_header
            )

        def education_fn():
            return generate_section(
                "education", bool(self.resume.education_details), self.generate_education_section
            )

        def work_experience_fn():
            if self.resume.experience_details:
                return self.generate_work_experience_section()
            return ""

        def projects_fn():
            return generate_section(
                "projects", bool(self.resume.projects), self.generate_projects_section
            )

        def achievements_fn():
            return generate_section(
                "achievements", bool(self.resume.achievements), self.generate_achievements_section
            )

        def certifications_fn():
            return generate_section(
                "certifications", bool(self.resume.certifications), self.generate_certifications_section
            )

        def additional_skills_fn():
            condition = (self.resume.experience_details or self.resume.education_details or
                         self.resume.languages or self.resume.interests)
            return generate_section("additional_skills", condition, self.generate_additional_skills_section)

        # Create a dictionary to map the function names to their respective callables
        functions = {
            "header": header_fn,
            "education": education_fn,
            "work_experience": work_experience_fn,
            "projects": projects_fn,
            "achievements": achievements_fn,
            "certifications": certifications_fn,
            "additional_skills": additional_skills_fn,
        }

        # Use ThreadPoolExecutor to run the functions in parallel
        with ThreadPoolExecutor(max_workers=min(len(functions), 7)) as executor:
            future_to_section = {executor.submit(fn): section for section, fn in functions.items()}
            results = {}
            # Iterate over the completed futures
            for future in as_completed(future_to_section):
                section = future_to_section[future]
                try:
                    result = future.result()
                    if result:
                        results[section] = result
                except Exception as exc:
                    logger.error(f'{section} raised an exception: {exc}')
        full_resume = textwrap.dedent(f"""
            <body>
                {results.get('header', '')}
                <main>
                    {results.get('education', '')}
                    {results.get('work_experience', '')}
                    {results.get('projects', '')}
                    {results.get('achievements', '')}
                    {results.get('certifications', '')}
                    {results.get('additional_skills', '')}
                </main>
            </body>
        """)
        return full_resume
