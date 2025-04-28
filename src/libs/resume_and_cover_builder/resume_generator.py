"""
This module is responsible for generating resumes and cover letters using the LLM model.
"""
# app/libs/resume_and_cover_builder/resume_generator.py
from string import Template
from typing import Any
import config as cfg
from src.libs.resume_and_cover_builder.llm.llm_generate_resume import LLMResumer
from src.libs.resume_and_cover_builder.llm.llm_generate_resume_from_job import LLMResumeJobDescription
from src.libs.resume_and_cover_builder.llm.llm_generate_cover_letter_from_job import LLMCoverLetterJobDescription
from .module_loader import load_module
from .config import global_config

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

    def create_resume(self, style_path, model_name: str | None = None):
        strings = load_module(global_config.STRINGS_MODULE_RESUME_PATH, global_config.STRINGS_MODULE_NAME)
        gpt_answerer = LLMResumer(global_config.API_KEY, strings,
                                  model_name or cfg.LLM_MODEL)
        return self._create_resume(gpt_answerer, style_path)

    def create_resume_job_description_text(self, style_path: str, job_description_text: str,
                                          model_name: str | None = None):
        strings = load_module(global_config.STRINGS_MODULE_RESUME_JOB_DESCRIPTION_PATH, global_config.STRINGS_MODULE_NAME)
        gpt_answerer = LLMResumeJobDescription(global_config.API_KEY, strings,
                                               model_name or cfg.LLM_MODEL)
        gpt_answerer.set_job_description_from_text(job_description_text)
        return self._create_resume(gpt_answerer, style_path)

    def create_cover_letter_job_description(self, style_path: str, job_description_text: str,
                                           model_name: str | None = None):
        strings = load_module(global_config.STRINGS_MODULE_COVER_LETTER_JOB_DESCRIPTION_PATH, global_config.STRINGS_MODULE_NAME)
        gpt_answerer = LLMCoverLetterJobDescription(global_config.API_KEY, strings,
                                                    model_name or cfg.LLM_MODEL)
        gpt_answerer.set_resume(self.resume_object)
        gpt_answerer.set_job_description_from_text(job_description_text)
        cover_letter_html = gpt_answerer.generate_cover_letter()
        template = Template(global_config.html_template)
        with open(style_path, "r") as f:
            style_css = f.read()
        return template.substitute(body=cover_letter_html, style_css=style_css)
    
    
    
