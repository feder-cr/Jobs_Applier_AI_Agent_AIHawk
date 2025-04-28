# In this file, you can set the configurations of the app.

from src.utils.constants import DEBUG, ERROR, LLM_MODEL, OPENAI

#config related to logging must have prefix LOG_
LOG_LEVEL = 'ERROR'
LOG_SELENIUM_LEVEL = ERROR
LOG_TO_FILE = False
LOG_TO_CONSOLE = False

MINIMUM_WAIT_TIME_IN_SECONDS = 60

JOB_APPLICATIONS_DIR = "job_applications"
JOB_SUITABILITY_SCORE = 7

JOB_MAX_APPLICATIONS = 5
JOB_MIN_APPLICATIONS = 1

LLM_MODEL_TYPE = 'openai'
LLM_MODEL = 'gpt-4o-mini'
# Only required for OLLAMA models
LLM_API_URL = ''

SUPPORTED_OPENAI_MODELS = [
    "gpt-4o-mini", "gpt-4o",
    "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-turbo", "gpt-4.1-nano",
    "o4-mini",
    "o3", "o3-mini",
    "o1", "o1-mini", "o1-pro",
]
