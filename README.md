# Jobs Applier AI Agent

An intelligent AI-powered tool that automates the creation of tailored resumes and cover letters for job applications. This application leverages advanced language models to analyze job descriptions and generate personalized application materials that align with specific job requirements.

## 🚀 Features

- **AI-Powered Resume Generation**: Create professional resumes using multiple styling options
- **Job-Tailored Documents**: Generate resumes and cover letters specifically tailored to job descriptions
- **Multiple LLM Support**: Compatible with OpenAI, Anthropic, Hugging Face, Google Gemini, and Ollama models
- **Web Scraping**: Automatically extract job details from job posting URLs
- **PDF Generation**: Export documents as high-quality PDF files
- **Interactive CLI**: User-friendly command-line interface with guided prompts
- **Flexible Styling**: Multiple resume templates and styles available
- **Job Application Tracking**: Save and organize generated application materials

## 📋 Prerequisites

- Python 3.8 or higher
- Chrome browser (for web scraping functionality)
- API key for your chosen LLM provider (OpenAI, Anthropic, etc.)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/feder-cr/Jobs_Applier_AI_Agent.git
   cd Jobs_Applier_AI_Agent
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the data folder**:
   ```bash
   mkdir data_folder
   ```

## ⚙️ Configuration

Create the following configuration files in the `data_folder` directory:

### 1. `secrets.yaml`
```yaml
llm_api_key: 'your-api-key-here'
```

### 2. `work_preferences.yaml`
```yaml
remote: true
hybrid: true
onsite: true

experience_level:
  internship: false
  entry: true
  associate: true
  mid_senior_level: true
  director: false
  executive: false

job_types:
  full_time: true
  contract: false
  part_time: false
  temporary: true
  internship: false
  other: false
  volunteer: true

date:
  all_time: false
  month: false
  week: false
  24_hours: true

positions:
  - Software Engineer
  - Data Scientist

locations:
  - Remote
  - New York
  - San Francisco

apply_once_at_company: true
distance: 100

company_blacklist:
  - company1
  - company2

title_blacklist:
  - unwanted_title1
  - unwanted_title2

location_blacklist:
  - unwanted_location1
```

### 3. `plain_text_resume.yaml`
```yaml
personal_information:
  name: "Your Name"
  surname: "Your Surname"
  date_of_birth: "01/01/1990"
  country: "Your Country"
  city: "Your City"
  address: "Your Address"
  zip_code: "12345"
  phone_prefix: "+1"
  phone: "1234567890"
  email: "your.email@example.com"
  github: "https://github.com/yourusername"
  linkedin: "https://www.linkedin.com/in/yourusername"

education_details:
  - education_level: "Bachelor's Degree"
    institution: "University Name"
    field_of_study: "Computer Science"
    final_evaluation_grade: "3.8"
    year_of_completion: "2020"
    start_date: "2016"

experience_details:
  - position: "Software Engineer"
    company: "Tech Company"
    employment_period: "01/2020 - Present"
    location: "San Francisco, CA"
    industry: "Technology"
    key_responsibilities:
      - responsibility: "Developed web applications using React and Node.js"
      - responsibility: "Collaborated with cross-functional teams"
    skills_acquired:
      - "React"
      - "Node.js"
      - "Python"

projects:
  - name: "Project Name"
    description: "Project description"
    link: "https://github.com/yourusername/project"

achievements:
  - name: "Achievement Name"
    description: "Achievement description"

certifications:
  - name: "Certification Name"
    description: "Certification description"

languages:
  - language: "English"
    proficiency: "Native"
  - language: "Spanish"
    proficiency: "Intermediate"

interests:
  - "Machine Learning"
  - "Open Source"

availability:
  notice_period: "2 weeks"

salary_expectations:
  salary_range_usd: "80000 - 120000"

self_identification:
  gender: "Prefer not to say"
  pronouns: "They/Them"
  veteran: "No"
  disability: "No"
  ethnicity: "Prefer not to say"

legal_authorization:
  eu_work_authorization: "Yes"
  us_work_authorization: "Yes"
  requires_us_visa: "No"
  requires_us_sponsorship: "No"
  requires_eu_visa: "No"
  legally_allowed_to_work_in_eu: "Yes"
  legally_allowed_to_work_in_us: "Yes"
  requires_eu_sponsorship: "No"

work_preferences:
  remote_work: "Yes"
  in_person_work: "Yes"
  open_to_relocation: "Yes"
  willing_to_complete_assessments: "Yes"
  willing_to_undergo_drug_tests: "Yes"
  willing_to_undergo_background_checks: "Yes"
```

## 🚀 Usage

Run the application:
```bash
python main.py
```

The application will present you with the following options:

1. **Generate Resume**: Create a standard professional resume
2. **Generate Resume Tailored for Job Description**: Create a resume customized for a specific job
3. **Generate Cover Letter for Job Description**: Create a tailored cover letter for a specific job

### Interactive Workflow

1. **Select an action** from the menu
2. **Choose a resume style** from available templates
3. **Provide job URL** (for tailored documents)
4. **Review generated documents** in the `data_folder/output` directory

## 📁 Project Structure

```
Jobs_Applier_AI_Agent/
├── main.py                    # Main application entry point
├── config.py                  # Application configuration
├── requirements.txt           # Python dependencies
├── data_folder/              # Configuration and output directory
│   ├── secrets.yaml          # API keys and secrets
│   ├── work_preferences.yaml # Job search preferences
│   ├── plain_text_resume.yaml # Resume data
│   └── output/               # Generated documents
├── src/                      # Source code
│   ├── libs/                 # Core libraries
│   │   └── resume_and_cover_builder/ # Resume/cover letter generation
│   ├── resume_schemas/       # Data models and schemas
│   ├── utils/                # Utility functions
│   └── logging.py            # Logging configuration
├── assets/                   # Static assets and schemas
├── .github/                  # GitHub workflows and templates
└── docs/                     # Documentation
```

## 🔧 Configuration Options

### LLM Models

The application supports multiple LLM providers. Configure in `config.py`:

```python
LLM_MODEL_TYPE = 'openai'  # Options: 'openai', 'anthropic', 'huggingface', 'google', 'ollama'
LLM_MODEL = 'gpt-4o-mini'  # Specific model name
```

### Logging

Customize logging behavior in `config.py`:

```python
LOG_LEVEL = ERROR
LOG_TO_FILE = False
LOG_TO_CONSOLE = False
```

## 🧪 Testing

Run the test suite:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=src
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Install development dependencies
4. Make your changes
5. Run tests
6. Submit a pull request

## 📄 License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0). See [LICENSE](LICENSE) for details.

## 🆘 Support

- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/feder-cr/Jobs_Applier_AI_Agent/issues)
- **Discussions**: Join community discussions on [GitHub Discussions](https://github.com/feder-cr/Jobs_Applier_AI_Agent/discussions)
- **Documentation**: Check the [docs](./docs) directory for additional documentation

## 🙏 Acknowledgments

- Built with [LangChain](https://langchain.com/) for LLM integration
- Uses [Selenium](https://selenium.dev/) for web scraping
- PDF generation powered by [ReportLab](https://www.reportlab.com/)

## ⚠️ Disclaimer

This tool is designed to assist in creating job application materials. Always review and customize generated content before submitting applications. The quality of output depends on the accuracy of your input data and the capabilities of the chosen LLM.

---

**Made with ❤️ by the Jobs Applier AI Agent team**
