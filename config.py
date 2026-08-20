# In this file, you can set the configurations of the app.

import os
from src.utils.constants import DEBUG, ERROR, LLM_MODEL, OPENAI

#config related to logging must have prefix LOG_
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'ERROR')
LOG_SELENIUM_LEVEL = ERROR
LOG_TO_FILE = os.environ.get('LOG_TO_FILE', 'false').lower() == 'true'
LOG_TO_CONSOLE = os.environ.get('LOG_TO_CONSOLE', 'false').lower() == 'true'

MINIMUM_WAIT_TIME_IN_SECONDS = 60

JOB_APPLICATIONS_DIR = "job_applications"
JOB_SUITABILITY_SCORE = 7

JOB_MAX_APPLICATIONS = 5
JOB_MIN_APPLICATIONS = 1

LLM_MODEL_TYPE = os.environ.get('LLM_MODEL_TYPE', 'claude')
LLM_MODEL = os.environ.get('LLM_MODEL', 'claude-sonnet-4-20250514')
# Only required for OLLAMA models
LLM_API_URL = os.environ.get('LLM_API_URL', '')

# Web server configuration
WEB_HOST = os.environ.get('WEB_HOST', '0.0.0.0')
WEB_PORT = int(os.environ.get('PORT', os.environ.get('WEB_PORT', '8080')))
