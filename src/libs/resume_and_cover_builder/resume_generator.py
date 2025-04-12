"""
This module is responsible for generating resumes and cover letters using the LLM model.
"""
# app/libs/resume_and_cover_builder/resume_generator.py
from string import Template
from typing import Any
import jinja2
from src.libs.resume_and_cover_builder.llm.llm_generate_resume import LLMResumer
from src.libs.resume_and_cover_builder.llm.llm_generate_resume_from_job import LLMResumeJobDescription
from src.libs.resume_and_cover_builder.llm.llm_generate_cover_letter_from_job import LLMCoverLetterJobDescription
from .module_loader import load_module
from .config import global_config
import logging

class ResumeGenerator:
    def __init__(self):
        pass
    
    def set_resume_object(self, resume_object):
         self.resume_object = resume_object
         

    def _create_resume(self, gpt_answerer: Any, style_path):
        # Imposta il resume nell'oggetto gpt_answerer
        gpt_answerer.set_resume(self.resume_object)
        
        # Leggi il template HTML
        template = Template(global_config.html_template)
        
        try:
            with open(style_path, "r") as f:
                style_css = f.read()  # Correzione: chiama il metodo `read` con le parentesi
        except FileNotFoundError:
            raise ValueError(f"Il file di stile non è stato trovato nel percorso: {style_path}")
        except Exception as e:
            raise RuntimeError(f"Errore durante la lettura del file CSS: {e}")
        
        # Genera l'HTML del resume
        body_html = gpt_answerer.generate_html_resume()
        
        # Applica i contenuti al template
        return template.substitute(body=body_html, style_css=style_css)

    def create_resume(self, style_path):
        strings = load_module(global_config.STRINGS_MODULE_RESUME_PATH, global_config.STRINGS_MODULE_NAME)
        gpt_answerer = LLMResumer(global_config.API_KEY, strings)
        return self._create_resume(gpt_answerer, style_path)

    def create_resume_job_description_text(self, style_path: str, job_description_text: str):
        strings = load_module(global_config.STRINGS_MODULE_RESUME_JOB_DESCRIPTION_PATH, global_config.STRINGS_MODULE_NAME)
        gpt_answerer = LLMResumeJobDescription(global_config.API_KEY, strings)
        gpt_answerer.set_job_description_from_text(job_description_text)
        return self._create_resume(gpt_answerer, style_path)

    def create_cover_letter_job_description(self, style_path: str, job_description_text: str):
        strings = load_module(global_config.STRINGS_MODULE_COVER_LETTER_JOB_DESCRIPTION_PATH, global_config.STRINGS_MODULE_NAME)
        gpt_answerer = LLMCoverLetterJobDescription(global_config.API_KEY, strings)
        gpt_answerer.set_resume(self.resume_object)
        gpt_answerer.set_job_description_from_text(job_description_text)
        cover_letter_html = gpt_answerer.generate_cover_letter()
        template = Template(global_config.html_template)
        with open(style_path, "r") as f:
            style_css = f.read()
        return template.substitute(body=cover_letter_html, style_css=style_css)
    
    def generate_resume_html(self, resume_text: str, css_content: str) -> str:
        """
        Generate HTML for the resume.
        
        Args:
            resume_text (str): The plain text resume content
            css_content (str): The CSS styling to apply
            
        Returns:
            str: The generated HTML content
        """
        try:
            logging.info("Generating resume HTML from text")
            
            # Parse the resume text into sections
            sections = self._parse_resume_text(resume_text)
            
            # Create HTML template
            html_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Resume</title>
                <style>
                    {{ css_content }}
                </style>
            </head>
            <body>
                <div class="resume-container">
                    {% if personal_info %}
                    <header>
                        <h1>{{ personal_info.name }}</h1>
                        <div class="contact-info">
                            {% if personal_info.email %}
                            <p>Email: {{ personal_info.email }}</p>
                            {% endif %}
                            {% if personal_info.phone %}
                            <p>Phone: {{ personal_info.phone }}</p>
                            {% endif %}
                            {% if personal_info.address %}
                            <p>Address: {{ personal_info.address }}</p>
                            {% endif %}
                            {% if personal_info.linkedin %}
                            <p>LinkedIn: {{ personal_info.linkedin }}</p>
                            {% endif %}
                            {% if personal_info.website %}
                            <p>Website: {{ personal_info.website }}</p>
                            {% endif %}
                        </div>
                        {% if personal_info.summary %}
                        <div class="summary">
                            <p>{{ personal_info.summary }}</p>
                        </div>
                        {% endif %}
                    </header>
                    {% endif %}
                    
                    {% for section in sections %}
                    <section class="resume-section">
                        <h2>{{ section.title }}</h2>
                        <div class="section-content">
                            {{ section.content|safe }}
                        </div>
                    </section>
                    {% endfor %}
                </div>
            </body>
            </html>
            """
            
            # Create Jinja2 template
            template = jinja2.Template(html_template)
            
            # Render the template with the resume data
            html = template.render(
                css_content=css_content,
                personal_info=self._extract_personal_info(resume_text),
                sections=sections
            )
            
            logging.info("Resume HTML generation successful")
            return html
            
        except Exception as e:
            logging.error(f"Error generating resume HTML: {e}")
            # Return a simple fallback HTML in case of error
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Resume</title>
                <style>{css_content}</style>
            </head>
            <body>
                <pre>{resume_text}</pre>
            </body>
            </html>
            """
    
    def _extract_personal_info(self, resume_text: str) -> dict:
        """
        Extract personal information from the resume text.
        """
        try:
            # Try to extract basic info - in a real implementation this would be more sophisticated
            lines = resume_text.split('\n')
            name = lines[0] if lines else "Name"
            
            personal_info = {
                "name": name,
                "email": "",
                "phone": "",
                "address": "",
                "linkedin": "",
                "website": "",
                "summary": ""
            }
            
            # Try to extract information from resume_object if available
            if hasattr(self, 'resume_object') and self.resume_object:
                try:
                    if hasattr(self.resume_object, 'personal_information'):
                        personal_info["name"] = (
                            f"{self.resume_object.personal_information.first_name} "
                            f"{self.resume_object.personal_information.last_name}"
                        )
                        personal_info["email"] = self.resume_object.personal_information.email
                        personal_info["phone"] = self.resume_object.personal_information.phone
                        personal_info["address"] = self.resume_object.personal_information.address
                        personal_info["linkedin"] = self.resume_object.personal_information.linkedin
                        personal_info["website"] = self.resume_object.personal_information.website
                        personal_info["summary"] = self.resume_object.personal_information.summary
                except Exception as e:
                    logging.warning(f"Error extracting data from resume object: {e}")
            
            return personal_info
        except Exception as e:
            logging.error(f"Error extracting personal info: {e}")
            return {"name": "Resume"}
    
    def _parse_resume_text(self, resume_text: str) -> list:
        """
        Parse the resume text into sections.
        """
        try:
            # Simple section parsing - in a real implementation this would be more sophisticated
            sections = []
            current_section = None
            current_content = []
            
            lines = resume_text.strip().split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Check if this is a section header (assuming uppercase or ending with a colon)
                if line.isupper() or (line.endswith(':') and len(line) < 50):
                    # Save the previous section if there was one
                    if current_section:
                        sections.append({
                            "title": current_section,
                            "content": '<p>' + '</p><p>'.join(current_content) + '</p>'
                        })
                    
                    # Start a new section
                    current_section = line.rstrip(':')
                    current_content = []
                else:
                    current_content.append(line)
            
            # Add the last section
            if current_section and current_content:
                sections.append({
                    "title": current_section,
                    "content": '<p>' + '</p><p>'.join(current_content) + '</p>'
                })
                
            # If no sections were identified, create a single section with all content
            if not sections and resume_text.strip():
                sections.append({
                    "title": "Resume",
                    "content": '<p>' + resume_text.replace('\n\n', '</p><p>').replace('\n', '<br>') + '</p>'
                })
                
            return sections
        except Exception as e:
            logging.error(f"Error parsing resume text: {e}")
            return [{"title": "Resume", "content": f"<p>{resume_text}</p>"}]
    
    
    