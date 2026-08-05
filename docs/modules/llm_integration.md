# LLM Integration

The application relies heavily on Large Language Models (LLMs) for understanding job descriptions and generating human-like text for resumes and cover letters.

## LLM Manager (`src/libs/llm_manager.py`)

This module handles the abstraction layer for different AI providers.

### AI Model Adapter Pattern

The `AIAdapter` class acts as a factory, instantiating the correct model class based on the configuration (`LLM_MODEL_TYPE`).

Supported Providers:
- **OpenAI** (`OpenAIModel`)
- **Claude** (`ClaudeModel`)
- **Ollama** (`OllamaModel`) - for local inference
- **Gemini** (`GeminiModel`)
- **HuggingFace** (`HuggingFaceModel`)
- **Perplexity** (`PerplexityModel`)

### GPTAnswerer

The `GPTAnswerer` class is a high-level service that uses the configured LLM to answer specific questions related to the resume or job application.

**Key Features:**
- **`answer_question_textual_wide_range`**: Determines which section of the resume (e.g., Experience, Education) is relevant to a question and uses an appropriate prompt chain to generate an answer.
- **`is_job_suitable`**: Analyzes the job description against the resume to calculate a suitability score.
- **`summarize_job_description`**: Compresses long job descriptions into concise summaries.

### Logging (`LLMLogger`)
All LLM requests and responses are logged to `open_ai_calls.json` for debugging and cost tracking. It captures:
- Model Name
- Token Usage (Input/Output/Total)
- Estimated Cost
- Prompts and Replies

## Prompt Engineering
Prompts are stored in `src/libs/llm/prompts.py` (referenced in `llm_manager.py`). The application uses `LangChain` templates to structure these prompts dynamically with input variables like `{resume_section}` or `{job_description}`.
