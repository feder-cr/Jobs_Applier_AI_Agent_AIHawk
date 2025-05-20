"""
Resume Versioning Module

This module provides functionality to manage different versions of user resumes,
allowing users to organize, track, and manage multiple resume variants for
different job applications and purposes.

Classes:
    ResumeVersionManager: Main class for managing resume versions
    VersionMetadata: Data class for version metadata
    StorageHandler: Handles file storage and organization
"""

from .resume_version_manager import ResumeVersionManager
from .version_metadata import VersionMetadata, VersionType
from .storage_handler import StorageHandler

__all__ = [
    'ResumeVersionManager',
    'VersionMetadata', 
    'VersionType',
    'StorageHandler'
]

__version__ = '1.0.0'
__author__ = 'AIHawk Resume Versioning Team'
