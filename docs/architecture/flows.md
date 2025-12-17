# Application Flows

This document details the key workflows within the AIHawk application using Mermaid diagrams.

## 1. App Startup Flow

The application initialization process ensures all configurations and dependencies are ready before user interaction.

```mermaid
graph TD
    Start([Start main.py]) --> ValidateData[Validate Data Folder & Files]
    ValidateData -->|Check| Secrets[secrets.yaml]
    ValidateData -->|Check| Config[config.yaml]
    ValidateData -->|Check| Resume[plain_text_resume.yaml]
    
    Secrets -->|Validate| LoadSecrets[Load API Keys]
    Config -->|Validate| LoadConfig[Load User Preferences]
    
    LoadSecrets --> PromptUser[Prompt User for Action]
    LoadConfig --> PromptUser
    
    PromptUser -->|Select Action| HandleInquiries[Handle Inquiries]
```

## 2. Resume Parsing & Tailoring Flow

How the system takes a specific job URL and tailored a resume for it.

```mermaid
sequenceDiagram
    participant User
    participant Facade as ResumeFacade
    participant Browser as Selenium Browser
    participant Parser as LLMJobParser
    participant LLM as LLM Service
    participant Generator as ResumeGenerator

    User->>Facade: Select "Tailor Resume"
    Facade->>User: Request Job URL
    User->>Facade: Provide URL
    
    Facade->>Browser: Navigate to Job URL
    Browser->>Facade: Return Page HTML
    
    Facade->>Parser: Parse HTML
    Parser->>LLM: Extract Role, Company, Description
    LLM-->>Parser: Structured Job Data
    
    Facade->>Generator: Generate Tailored Resume
    Generator->>LLM: Compare Resume vs Job Desc
    LLM-->>Generator: Contextual Suggestions
    
    Generator->>Browser: Render HTML Template
    Browser->>Facade: Return PDF Bytes
    Facade->>User: Save PDF to Output
```

## 3. General Resume Generation Flow

Generating a generic resume without specific job tailoring.

```mermaid
graph TD
    User[User Input] -->|Select Style| StyleManager[Style Manager]
    StyleManager -->|Template Path| Generator[Resume Generator]
    
    subgraph Generation Process
        ResumeData[Load Resume Data] -->|Inject| Generator
        Generator -->|Render| HTML[HTML Resume]
        HTML -->|Convert| PDF[PDF Generator (Selenium)]
    end
    
    PDF --> Output[Output Folder]
```

## 4. LLM Request Lifecycle

How the system handles requests to the Large Language Model, including logging and error handling.

```mermaid
graph LR
    Request[App Request] --> Adapter[AI Adapter]
    Adapter -->|Select Provider| ModelFactory{Provider?}
    
    ModelFactory -->|OpenAI| OpenAI[OpenAI Model]
    ModelFactory -->|Claude| Claude[Claude Model]
    ModelFactory -->|Ollama| Ollama[Ollama Model]
    
    OpenAI --> API[External API]
    Claude --> API
    Ollama --> Local[Local Inference]
    
    API -->|Response| Logger[LLM Logger]
    Local -->|Response| Logger
    
    Logger -->|Log Token Usage| LogFile[open_ai_calls.json]
    Logger -->|Return Content| App[Application Logic]
```
