"""
Create a class that generates a job description based on a resume and a job description template.
"""
# app/libs/resume_and_cover_builder/llm_generate_resume_from_job.py
from src.libs.resume_and_cover_builder.llm.llm_generate_resume import LLMResumer
from src.libs.resume_and_cover_builder.utils import LoggerChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from loguru import logger
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

log_folder = Path('log/resume/gpt_resum_job_descr')
log_folder.mkdir(parents=True, exist_ok=True)

log_path = Path(log_folder).resolve()
logger.add(log_path / "gpt_resum_job_descr.log", rotation="1 day", compression="zip", retention="7 days", level="DEBUG")

class LLMResumeJobDescription(LLMResumer):
    def __init__(self, openai_api_key, strings):
        super().__init__(openai_api_key, strings)

    def set_job_description_from_text(self, job_description_text) -> None:
        """
        Set the job description text to be used for generating the resume.
        Args:
            job_description_text (str): The plain text job description to be used.
        """
        prompt = ChatPromptTemplate.from_template(self.strings.summarize_prompt_template)
        chain = prompt | self.llm_cheap | StrOutputParser()
        output = chain.invoke({"text": job_description_text})
        self.job_description = output
    
    def generate_header(self) -> str:
        """
        Generate the header section of the resume.
        Returns:
            str: The generated header section.
        """
        return super().generate_header(data={
            "personal_information": self.resume.personal_information,
            "job_description": self.job_description
        })

    def generate_education_section(self) -> str:
        """
        Generate the education section of the resume.
        Returns:
            str: The generated education section.
        """
        return super().generate_education_section(data={
            "education_details": self.resume.education_details,
            "job_description": self.job_description
        })

    def generate_work_experience_section(self) -> str:
        """
        Generate the work experience section of the resume.
        Returns:
            str: The generated work experience section.
        """
        return super().generate_work_experience_section(data={
            "experience_details": self.resume.experience_details,
            "job_description": self.job_description
        })

    def generate_projects_section(self) -> str:
        """
        Generate the side projects section of the resume.
        Returns:
            str: The generated side projects section.
        """
        return super().generate_projects_section(data={
            "projects": self.resume.projects,
            "job_description": self.job_description
        })

    def generate_achievements_section(self) -> str:
        """
        Generate the achievements section of the resume.
        Returns:
            str: The generated achievements section.
        """
        return super().generate_achievements_section(data={
            "achievements": self.resume.achievements,
            "job_description": self.job_description
        })


    def generate_certifications_section(self) -> str:
        """
        Generate the certifications section of the resume.
        Returns:
            str: The generated certifications section.
        """
        return super().generate_certifications_section(data={
            "certifications": self.resume.certifications,
            "job_description": self.job_description
        })

    def generate_additional_skills_section(self) -> str:
        """
        Generate the additional skills section of the resume.
        Returns:
            str: The generated additional skills section.
        """
        additional_skills_prompt_template = self._preprocess_template_string(
            self.strings.prompt_additional_skills
        )
        skills = set()
        if self.resume.experience_details:
            for exp in self.resume.experience_details:
                if exp.skills_acquired:
                    skills.update(exp.skills_acquired)

        if self.resume.education_details:
            for edu in self.resume.education_details:
                if edu.exam:
                    for exam in edu.exam:
                        skills.update(exam.keys())
        prompt = ChatPromptTemplate.from_template(additional_skills_prompt_template)
        chain = prompt | self.llm_cheap | StrOutputParser()
        output = chain.invoke({
            "languages": self.resume.languages,
            "interests": self.resume.interests,
            "skills": skills,
            "job_description": self.job_description
        })
        return output
