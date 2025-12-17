# Data Models & Schemas

The application uses rigorous data validation to ensure that resume data and job application profiles are well-structured.

## Resume Schema (`src/resume_schemas/resume.py`)

The `Resume` class is defined using `Pydantic` models, ensuring type safety and validation for user-provided data.

### Key Classes
- **`Resume`**: The root model containing all sections.
- **`PersonalInformation`**: Name, email, phone, location, links.
- **`EducationDetails`**: List of education records.
- **`ExperienceDetails`**: List of work experience records.
- **`Project`**, **`Achievement`**, **`Certifications`**, **`Language`**.

**Validation Features:**
- Email format validation (`EmailStr`).
- URL validation for links (`HttpUrl`).
- `normalize_exam_format`: Helper to handle inconsistent data formats in YAML.

## Job Application Profile (`src/resume_schemas/job_application_profile.py`)

Defined as a Python `dataclass`, this model holds user preferences and legal/demographic information often required by job boards.

### Sections
- **`SelfIdentification`**: Gender, veteran status, disability, ethnicity.
- **`LegalAuthorization`**: Work authorization status for US, EU, Canada, UK.
- **`WorkPreferences`**: Remote/hybrid preferences, relocation.
- **`SalaryExpectations`**: Desired salary range.
- **`Availability`**: Notice period.

## Data Loading
The `Resume` and `JobApplicationProfile` classes both include `__init__` methods that accept a YAML string, parsing it into the object structure and raising detailed errors (`ValueError`, `TypeError`) if the input validation fails.
