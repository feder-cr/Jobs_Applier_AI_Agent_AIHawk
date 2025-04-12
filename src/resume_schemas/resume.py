from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
import yaml
from pydantic import BaseModel, EmailStr, HttpUrl, Field



class PersonalInformation(BaseModel):
    name: Optional[str]
    surname: Optional[str]
    date_of_birth: Optional[str]
    country: Optional[str]
    city: Optional[str]
    address: Optional[str]
    zip_code: Optional[str] = Field(None, min_length=5, max_length=10)
    phone_prefix: Optional[str]
    phone: Optional[str]
    email: Optional[EmailStr]
    github: Optional[HttpUrl] = None
    linkedin: Optional[HttpUrl] = None


class EducationDetails(BaseModel):
    education_level: Optional[str]
    institution: Optional[str]
    field_of_study: Optional[str]
    final_evaluation_grade: Optional[str]
    start_date: Optional[str]
    year_of_completion: Optional[int]
    exam: Optional[Union[List[Dict[str, str]], Dict[str, str]]] = None


class ExperienceDetails(BaseModel):
    position: Optional[str]
    company: Optional[str]
    employment_period: Optional[str]
    location: Optional[str]
    industry: Optional[str]
    key_responsibilities: Optional[List[Dict[str, str]]] = None
    skills_acquired: Optional[List[str]] = None


class Project(BaseModel):
    name: Optional[str]
    description: Optional[str]
    link: Optional[HttpUrl] = None


class Achievement(BaseModel):
    name: Optional[str]
    description: Optional[str]


class Certifications(BaseModel):
    name: Optional[str]
    description: Optional[str]


class Language(BaseModel):
    language: Optional[str]
    proficiency: Optional[str]


class Availability(BaseModel):
    notice_period: Optional[str]


class SalaryExpectations(BaseModel):
    salary_range_usd: Optional[str]


class SelfIdentification(BaseModel):
    gender: Optional[str]
    pronouns: Optional[str]
    veteran: Optional[str]
    disability: Optional[str]
    ethnicity: Optional[str]


class LegalAuthorization(BaseModel):
    eu_work_authorization: Optional[str]
    us_work_authorization: Optional[str]
    requires_us_visa: Optional[str]
    requires_us_sponsorship: Optional[str]
    requires_eu_visa: Optional[str]
    legally_allowed_to_work_in_eu: Optional[str]
    legally_allowed_to_work_in_us: Optional[str]
    requires_eu_sponsorship: Optional[str]


class Resume(BaseModel):
    personal_information: Optional[PersonalInformation]
    education_details: Optional[List[EducationDetails]] = None
    experience_details: Optional[List[ExperienceDetails]] = None
    projects: Optional[List[Project]] = None
    achievements: Optional[List[Achievement]] = None
    certifications: Optional[List[Certifications]] = None
    languages: Optional[List[Language]] = None
    interests: Optional[List[str]] = None

    @staticmethod
    def normalize_exam_format(exam):
        if isinstance(exam, dict):
            return [{k: v} for k, v in exam.items()]
        return exam

    def __init__(self, yaml_str: str):
        try:
            # Parse the YAML string
            data = yaml.safe_load(yaml_str)

            if 'education_details' in data:
                for ed in data['education_details']:
                    if 'exam' in ed:
                        ed['exam'] = self.normalize_exam_format(ed['exam'])

            # Create an instance of Resume from the parsed data
            super().__init__(**data)
        except yaml.YAMLError as e:
            raise ValueError("Error parsing YAML file.") from e
        except Exception as e:
            raise Exception(f"Unexpected error while parsing YAML: {e}") from e

    def to_text(self) -> str:
        """
        Convert the resume to a plain text format.
        
        Returns:
            str: A plain text representation of the resume
        """
        lines = []
        
        # Personal Information
        if self.personal_information:
            personal_info = self.personal_information
            name_parts = []
            if hasattr(personal_info, 'first_name') and personal_info.first_name:
                name_parts.append(personal_info.first_name)
            if hasattr(personal_info, 'last_name') and personal_info.last_name:
                name_parts.append(personal_info.last_name)
            
            if not name_parts and hasattr(personal_info, 'name') and personal_info.name:
                name_parts.append(personal_info.name)
                if hasattr(personal_info, 'surname') and personal_info.surname:
                    name_parts.append(personal_info.surname)
                    
            if name_parts:
                lines.append(' '.join(name_parts))
            
            contact_info = []
            if hasattr(personal_info, 'email') and personal_info.email:
                contact_info.append(f"Email: {personal_info.email}")
            if hasattr(personal_info, 'phone') and personal_info.phone:
                phone_str = personal_info.phone
                if hasattr(personal_info, 'phone_prefix') and personal_info.phone_prefix:
                    phone_str = f"{personal_info.phone_prefix} {phone_str}"
                contact_info.append(f"Phone: {phone_str}")
            if hasattr(personal_info, 'address') and personal_info.address:
                contact_info.append(f"Address: {personal_info.address}")
            if hasattr(personal_info, 'city') and personal_info.city:
                city_country = personal_info.city
                if hasattr(personal_info, 'country') and personal_info.country:
                    city_country = f"{city_country}, {personal_info.country}"
                contact_info.append(f"Location: {city_country}")
            
            if contact_info:
                lines.extend(contact_info)
                lines.append("")  # Add a blank line
            
            if hasattr(personal_info, 'summary') and personal_info.summary:
                lines.append("SUMMARY")
                lines.append(personal_info.summary)
                lines.append("")
        
        # Education
        if self.education_details:
            lines.append("EDUCATION")
            for edu in self.education_details:
                if edu.institution:
                    lines.append(edu.institution)
                if edu.education_level:
                    lines.append(f"{edu.education_level}{' in ' + edu.field_of_study if edu.field_of_study else ''}")
                if edu.start_date or edu.year_of_completion:
                    date_range = ""
                    if edu.start_date:
                        date_range += edu.start_date
                    if edu.year_of_completion:
                        date_range += f" - {edu.year_of_completion}"
                    lines.append(date_range)
                if edu.final_evaluation_grade:
                    lines.append(f"Grade: {edu.final_evaluation_grade}")
                lines.append("")
        
        # Experience
        if self.experience_details:
            lines.append("EXPERIENCE")
            for exp in self.experience_details:
                if exp.position and exp.company:
                    lines.append(f"{exp.position} at {exp.company}")
                elif exp.position:
                    lines.append(exp.position)
                elif exp.company:
                    lines.append(exp.company)
                    
                if exp.employment_period:
                    lines.append(exp.employment_period)
                if exp.location:
                    lines.append(f"Location: {exp.location}")
                    
                if exp.key_responsibilities:
                    lines.append("Responsibilities:")
                    for resp in exp.key_responsibilities:
                        if isinstance(resp, dict) and 'description' in resp:
                            lines.append(f"- {resp['description']}")
                        elif isinstance(resp, str):
                            lines.append(f"- {resp}")
                
                if exp.skills_acquired:
                    lines.append("Skills:")
                    for skill in exp.skills_acquired:
                        lines.append(f"- {skill}")
                        
                lines.append("")
        
        # Projects
        if self.projects:
            lines.append("PROJECTS")
            for project in self.projects:
                if project.name:
                    lines.append(project.name)
                if project.description:
                    lines.append(project.description)
                if project.link:
                    lines.append(f"Link: {project.link}")
                lines.append("")
        
        # Languages
        if self.languages:
            lines.append("LANGUAGES")
            for lang in self.languages:
                if lang.language:
                    lang_str = lang.language
                    if lang.proficiency:
                        lang_str += f" ({lang.proficiency})"
                    lines.append(lang_str)
            lines.append("")
        
        # Interests
        if self.interests:
            lines.append("INTERESTS")
            for interest in self.interests:
                lines.append(f"- {interest}")
            lines.append("")
            
        return "\n".join(lines)

    def _process_personal_information(self, data: Dict[str, Any]) -> PersonalInformation:
        try:
            return PersonalInformation(**data)
        except TypeError as e:
            raise TypeError(f"Invalid data for PersonalInformation: {e}") from e
        except AttributeError as e:
            raise AttributeError(f"AttributeError in PersonalInformation: {e}") from e
        except Exception as e:
            raise Exception(f"Unexpected error in PersonalInformation processing: {e}") from e

    def _process_education_details(self, data: List[Dict[str, Any]]) -> List[EducationDetails]:
        education_list = []
        for edu in data:
            try:
                exams = [Exam(name=k, grade=v) for k, v in edu.get('exam', {}).items()]
                education = EducationDetails(
                    education_level=edu.get('education_level'),
                    institution=edu.get('institution'),
                    field_of_study=edu.get('field_of_study'),
                    final_evaluation_grade=edu.get('final_evaluation_grade'),
                    start_date=edu.get('start_date'),
                    year_of_completion=edu.get('year_of_completion'),
                    exam=exams
                )
                education_list.append(education)
            except KeyError as e:
                raise KeyError(f"Missing field in education details: {e}") from e
            except TypeError as e:
                raise TypeError(f"Invalid data for Education: {e}") from e
            except AttributeError as e:
                raise AttributeError(f"AttributeError in Education: {e}") from e
            except Exception as e:
                raise Exception(f"Unexpected error in Education processing: {e}") from e
        return education_list

    def _process_experience_details(self, data: List[Dict[str, Any]]) -> List[ExperienceDetails]:
        experience_list = []
        for exp in data:
            try:
                key_responsibilities = [
                    Responsibility(description=list(resp.values())[0])
                    for resp in exp.get('key_responsibilities', [])
                ]
                skills_acquired = [str(skill) for skill in exp.get('skills_acquired', [])]
                experience = ExperienceDetails(
                    position=exp['position'],
                    company=exp['company'],
                    employment_period=exp['employment_period'],
                    location=exp['location'],
                    industry=exp['industry'],
                    key_responsibilities=key_responsibilities,
                    skills_acquired=skills_acquired
                )
                experience_list.append(experience)
            except KeyError as e:
                raise KeyError(f"Missing field in experience details: {e}") from e
            except TypeError as e:
                raise TypeError(f"Invalid data for Experience: {e}") from e
            except AttributeError as e:
                raise AttributeError(f"AttributeError in Experience: {e}") from e
            except Exception as e:
                raise Exception(f"Unexpected error in Experience processing: {e}") from e
        return experience_list


@dataclass
class Exam:
    name: str
    grade: str

@dataclass
class Responsibility:
    description: str