"""
This module contains the FacadeManager class, which is responsible for managing the interaction between the user and other components of the application.
"""
# app/libs/resume_and_cover_builder/manager_facade.py
import hashlib
import inquirer
from pathlib import Path
import sys
import base64
import inspect
import os
import tempfile
from typing import List, Tuple, Optional
import requests
import json
import jinja2

from loguru import logger
from selenium import webdriver

from src.libs.resume_and_cover_builder.llm.llm_job_parser import LLMParser
from src.libs.resume_and_cover_builder.style_manager import StyleManager
from src.libs.resume_and_cover_builder.resume_generator import ResumeGenerator
from src.job import Job
from src.resume_schemas.resume import Resume
from src.utils.chrome_utils import HTML_to_PDF, get_chromedriver_path, get_job_description
from .config import global_config

# Import OpenAI if available, but make it optional
try:
    import openai
except ImportError:
    openai = None

class ResumeFacade:
    def __init__(
        self,
        api_key: str,
        style_manager: StyleManager,
        resume_generator: ResumeGenerator,
        resume_object: Resume,
        output_path: Path,
        use_deepseek: bool = False,
    ):
        """
        Initialize the FacadeManager with the given API key, style manager, resume generator, resume object, and log path.
        Args:
            api_key (str): The OpenAI API key to be used for generating text.
            style_manager (StyleManager): The StyleManager instance to manage the styles.
            resume_generator (ResumeGenerator): The ResumeGenerator instance to generate resumes and cover letters.
            resume_object (str): The resume object to be used for generating resumes and cover letters.
            output_path (str): The path to the log file.
            use_deepseek (bool): Flag to use DeepSeek API instead of OpenAI
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
        self.use_deepseek = use_deepseek  # Flag to use DeepSeek API instead of OpenAI
        self.job_description = None
        self.job_url = None
        self.company_name = None
        self.driver = None
    
    def set_driver(self, driver: webdriver.Chrome):
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

    def link_to_job(self, job_url: str):
        """
        Link the resume to a specific job description URL.
        """
        self.job_url = job_url
        self.job_description = get_job_description(self.driver, job_url)
        # Extract company name from job description (you may need to refine this)
        try:
            # This is a simple example, might need to be improved
            if self.job_description:
                company_indicators = ["at ", "with ", "join ", "company: "]
                for indicator in company_indicators:
                    if indicator in self.job_description.lower():
                        parts = self.job_description.lower().split(indicator)
                        if len(parts) > 1:
                            potential_company = parts[1].split()[0]
                            if len(potential_company) > 2:  # Simple validation
                                self.company_name = potential_company.title()
                                break
                
                if not self.company_name:
                    # Fallback to URL domain
                    from urllib.parse import urlparse
                    domain = urlparse(job_url).netloc
                    self.company_name = domain.split('.')[0].title()
            else:
                # Fallback to URL domain if no job description
                from urllib.parse import urlparse
                domain = urlparse(job_url).netloc
                self.company_name = domain.split('.')[0].title()
        except Exception as e:
            logger.warning(f"Error extracting company name: {e}")
            self.company_name = "Company"  # Default fallback
            
    def set_manual_job_description(self, description: str):
        """
        Set a manually entered job description without URL scraping.
        
        Args:
            description (str): The manually entered job description text
        """
        self.job_description = description
        
        # Try to extract company name from the job description
        try:
            if self.job_description:
                company_indicators = ["at ", "with ", "join ", "company: "]
                for indicator in company_indicators:
                    if indicator in self.job_description.lower():
                        parts = self.job_description.lower().split(indicator)
                        if len(parts) > 1:
                            potential_company = parts[1].split()[0]
                            if len(potential_company) > 2:  # Simple validation
                                self.company_name = potential_company.title()
                                break
            
            # Set default if not found
            if not self.company_name:
                self.company_name = "Company"
        except Exception as e:
            logger.warning(f"Error extracting company name from manual description: {e}")
            self.company_name = "Company"  # Default fallback

    def create_resume_pdf_job_tailored(self) -> Tuple[str, str]:
        """
        Generate a tailored resume PDF for the specified job.
        
        Returns:
            Tuple[str, str]: Base64-encoded PDF content and suggested name for the resume
        """
        if not self.job_description:
            raise ValueError("No job description found. Please call link_to_job first.")
        
        # Prepare the prompt
        prompt = f"""
        Please analyze this resume and job description, then provide specific recommendations 
        for tailoring the resume to better match the job requirements:
        
        Job Description:
        {self.job_description}
        
        Resume:
        {self.resume_generator.resume_object.to_text()}
        
        Provide the tailored resume content directly, making sure to:
        1. Highlight relevant skills and experiences that match the job requirements
        2. Use similar keywords from the job description
        3. Prioritize the most relevant accomplishments
        4. Keep the overall format and structure similar
        """
        
        try:
            # Generate content using the appropriate API
            if self.use_deepseek:
                response = self._generate_with_deepseek(prompt)
            else:
                response = self._generate_with_openai(prompt)
                
            # Process the response
            tailored_resume_content = response
            
            # Create a suggested filename
            company_part = self.company_name.replace(" ", "_").lower() if self.company_name else "company"
            suggested_name = f"resume_{company_part}"
            
            # Generate a resume HTML
            css_content = self.style_manager.get_selected_style_content()
            resume_html = self.resume_generator.generate_resume_html(
                tailored_resume_content, 
                css_content
            )
            
            # Convert to PDF
            pdf_content = self._html_to_pdf(resume_html)
            
            return base64.b64encode(pdf_content).decode('utf-8'), suggested_name
            
        except Exception as e:
            logger.error(f"Error generating tailored resume: {e}")
            raise
    
    def create_resume_pdf(self) -> str:
        """
        Generate a base resume PDF without tailoring.
        
        Returns:
            str: Base64-encoded PDF content
        """
        try:
            # Generate HTML using the resume generator
            logger.info("Generating resume HTML...")
            css_content = self.style_manager.get_selected_style_content()
            resume_html = self.resume_generator.generate_resume_html(
                self.resume_generator.resume_object.to_text(), 
                css_content
            )
            logger.info("Resume HTML generated successfully.")
            
            # Convert to PDF
            logger.info("Converting HTML to PDF...")
            pdf_content = self._html_to_pdf(resume_html)
            logger.info("PDF conversion completed successfully.")
            
            # Return as base64 string
            return base64.b64encode(pdf_content).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Error generating resume PDF: {e}")
            raise

    def create_cover_letter(self) -> Tuple[str, str]:
        """
        Generate a cover letter PDF for the specified job.
        
        Returns:
            Tuple[str, str]: Base64-encoded PDF content and suggested name for the cover letter
        """
        if not self.job_description:
            raise ValueError("No job description found. Please call link_to_job first.")
        
        # Extract relevant info - handle different ways name might be stored
        personal_info = self.resume_generator.resume_object.personal_information
        
        # Get the full name using available attributes
        if hasattr(personal_info, 'name') and personal_info.name and hasattr(personal_info, 'surname') and personal_info.surname:
            name = f"{personal_info.name} {personal_info.surname}"
        elif hasattr(personal_info, 'first_name') and personal_info.first_name and hasattr(personal_info, 'last_name') and personal_info.last_name:
            name = f"{personal_info.first_name} {personal_info.last_name}"
        elif hasattr(personal_info, 'name') and personal_info.name:
            name = personal_info.name
        else:
            name = "Applicant"  # Fallback if no name found
        
        # Prepare the prompt
        prompt = f"""
        Based on the following information, create a professional and personalized cover letter:
        
        Job Description:
        {self.job_description}
        
        Resume Summary:
        {personal_info.summary if hasattr(personal_info, 'summary') and personal_info.summary else 'N/A'}
        
        Applicant Name: {name}
        
        Format the cover letter professionally, addressing it to the hiring manager at {self.company_name}.
        Focus on matching the applicant's skills and experience with the job requirements.
        Keep it concise (around 300-400 words), personalized, and engaging.
        """
        
        try:
            # Generate content using the appropriate API
            if self.use_deepseek:
                response = self._generate_with_deepseek(prompt)
            else:
                response = self._generate_with_openai(prompt)
                
            # Process the response
            cover_letter_content = response
            
            # Create a suggested filename
            company_part = self.company_name.replace(" ", "_").lower() if self.company_name else "company"
            suggested_name = f"cover_letter_{company_part}"
            
            # Generate HTML
            html_content = self._generate_cover_letter_html(cover_letter_content, name)
            
            # Convert to PDF
            pdf_content = self._html_to_pdf(html_content)
            
            return base64.b64encode(pdf_content).decode('utf-8'), suggested_name
            
        except Exception as e:
            logger.error(f"Error generating cover letter: {e}")
            raise

    def _generate_with_openai(self, prompt: str) -> str:
        """
        Generate content using OpenAI API
        """
        if not openai:
            raise ImportError("OpenAI package is not installed. Please install it with: pip install openai")
            
        # Configure OpenAI client
        client = openai.OpenAI(api_key=global_config.API_KEY)
        
        try:
            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional resume writer and career advisor."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )
            
            # Extract the content
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content
            else:
                raise Exception("No content received from OpenAI API")
                
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            raise
    
    def _generate_with_deepseek(self, prompt: str, model: str = "deepseek/deepseek-r1:free") -> str:
        """
        Generate content using DeepSeek through OpenRouter API
        """
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {global_config.API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://jobs-applier-ai-agent.com",
                    "X-Title": "Jobs Applier AI Agent",
                },
                data=json.dumps({
                    "model": model,
                    "messages": [
                        {
                            "role": "system", 
                            "content": "You are a professional resume writer and career advisor."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                })
            )
            
            response.raise_for_status()
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                logger.error(f"Unexpected response format from OpenRouter: {result}")
                raise Exception("Unexpected response format from OpenRouter")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to OpenRouter: {e}")
            raise Exception(f"Error making request to OpenRouter: {e}")
    
    def _generate_cover_letter_html(self, content: str, name: str) -> str:
        """
        Generate HTML for the cover letter from the provided content.
        """
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Cover Letter</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 2em;
                    max-width: 800px;
                }
                .header {
                    text-align: right;
                    margin-bottom: 2em;
                }
                .signature {
                    margin-top: 2em;
                }
                h1 {
                    font-size: 16pt;
                }
                p {
                    margin-bottom: 1em;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{{ name }}</h1>
                {% if email %}
                <p>{{ email }}</p>
                {% endif %}
                {% if phone %}
                <p>{{ phone }}</p>
                {% endif %}
                {% if address %}
                <p>{{ address }}</p>
                {% endif %}
                <p>{{ date }}</p>
            </div>
            
            <div class="content">
                {{ content | safe }}
            </div>
            
            <div class="signature">
                <p>Sincerely,</p>
                <p>{{ name }}</p>
            </div>
        </body>
        </html>
        """
        
        # Create a Jinja2 template
        template = jinja2.Template(html_template)
        
        # Format the content to preserve line breaks and paragraphs
        formatted_content = ""
        for line in content.split('\n'):
            if line.strip():
                formatted_content += f"<p>{line}</p>\n"
        
        # Get today's date
        from datetime import datetime
        today = datetime.now().strftime("%B %d, %Y")
        
        # Safely get personal information fields
        personal_info = self.resume_generator.resume_object.personal_information
        email = personal_info.email if hasattr(personal_info, 'email') and personal_info.email else ""
        phone = personal_info.phone if hasattr(personal_info, 'phone') and personal_info.phone else ""
        address = personal_info.address if hasattr(personal_info, 'address') and personal_info.address else ""
        
        # Render the template
        html = template.render(
            name=name,
            email=email,
            phone=phone,
            address=address,
            date=today,
            content=formatted_content
        )
        
        return html
    
    def _html_to_pdf(self, html_content: str) -> bytes:
        """
        Convert HTML content to PDF.
        """
        try:
            import pdfkit
            
            # Define options for pdfkit
            options = {
                'page-size': 'A4',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': 'UTF-8',
            }
            
            # Write the HTML to a temporary file
            with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as temp:
                temp.write(html_content.encode('utf-8'))
                temp_path = temp.name
            
            # Use the exact path to wkhtmltopdf
            wkhtmltopdf_path = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
            config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
            
            # Convert HTML to PDF
            pdf_data = pdfkit.from_file(temp_path, False, options=options, configuration=config)
            
            # Clean up the temporary file
            os.unlink(temp_path)
            
            return pdf_data
            
        except Exception as e:
            logger.error(f"Error converting HTML to PDF: {e}")
            raise