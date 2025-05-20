from src.logging import logger
import os
import json
import shutil
import re

from dataclasses import asdict

from config import JOB_APPLICATIONS_DIR
from job import Job
from job_application import JobApplication

# Base directory where all applications will be saved
BASE_DIR = JOB_APPLICATIONS_DIR
APPLICATION_DETAILS_FILENAME = "job_application.json"


class ApplicationSaver:

    def __init__(self, job_application: JobApplication):
        self.job_application = job_application
        # Path to the directory where the job application files will be saved
        self.job_application_files_path = None

    def generate_dir_name(self, job: Job) -> str:
        return f"{job.id} - {job.company} {job.title}"

    def create_application_directory(self) -> str:
        """
        Create a unique directory for the job application.

        Returns:
            str: The path of the created directory.
        """
        job = self.job_application.job

        # Create a unique directory name using the application ID, job title and company name
        dir_name = self.generate_dir_name(job)
        dir_path = os.path.join(BASE_DIR, dir_name)
        if not os.path.exists(dir_path):
            logger.debug(f"Creating directory: {dir_path}")
            # Create the directory if it doesn't exist
            os.makedirs(dir_path, mode=0o777, exist_ok=True)
        self.job_application_files_path = dir_path
        return dir_path

    # Function to save the job application details as a JSON file
    def save_application_details(self):

        if self.job_application_files_path is None:
            raise ValueError(
                "Job application file path is not set. Please create the application directory first."
            )

        json_file_path = os.path.join(
            self.job_application_files_path, APPLICATION_DETAILS_FILENAME
        )
        try:
            with open(json_file_path, "w") as json_file:
                json.dump(self.job_application.application, json_file, indent=4)
        except FileNotFoundError as e:
            logger.error(f"File {json_file_path} not found: {e}")
        except PermissionError as e:
            logger.error(f"Permission error: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON encoding error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

    def save_file(self, dir_path: str, file_path: str, new_filename: str) -> None:
        """Save a file to the specified directory with a new name."""
        # Check if the directory path is valid
        if dir_path is None or dir_path == "":
            raise ValueError("dir path cannot be None")
        safe_filename = re.sub(r'[<>:"/\\|?*]', "", new_filename)
        # Construct the full path for the new file in the destination directory
        destination = os.path.join(dir_path, safe_filename)
        # Copy the file to the application directory with a new name
        shutil.copy(file_path, destination)

    def save_job_description(self) -> None:
        """
        Save the job description as a JSON file.

        This method writes the job description of the current job application to a 
        JSON file named 'job_description.json' in the job application directory.

        Raises:
            ValueError: If the job application file path is not set.
        """
        if self.job_application_files_path is None:
            raise ValueError(
                f"Job application file path is not set for job ID {self.job_application.job.id}. "
                f"Please create the application directory first."
            )
        # Get the job associated with the current job application
        job: Job = self.job_application.job

        json_file_path = os.path.join(
            self.job_application_files_path, "job_description.json"
        )
        with open(json_file_path, "w") as json_file:
            json.dump(job.to_dict(), json_file, indent=4)

    @staticmethod
    def save(job_application: JobApplication):
        saver = ApplicationSaver(job_application)
        saver.create_application_directory()
        saver.save_application_details()
        saver.save_job_description()
        # todo: tempory fix, to rely on resume and cv path from job object instead of job application object
        if job_application.resume_path:
            saver.save_file(
                saver.job_application_files_path,
                job_application.job.resume_path,
                "resume.pdf",
            )
        logger.debug(f"Saving cover letter to path: {job_application.cover_letter_path}")
        if job_application.cover_letter_path:
            saver.save_file(
                saver.job_application_files_path,
                job_application.job.cover_letter_path,
                "cover_letter.pdf"
            )
