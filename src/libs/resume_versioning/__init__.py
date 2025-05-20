"""
Resume Versioning Module

This module provides functionality to manage different versions of user resumes,
allowing users to save, organize, compare, and restore resume versions.

Features:
- Version creation and management
- Tagging system for categorization
- Version comparison
- Export/Import functionality
- Integration with existing resume generation
"""

from .version_manager import ResumeVersionManager
from .models import ResumeVersion, VersionMetadata
from .storage import VersionStorage
from .utils import compare_versions, export_version, import_version

__version__ = "1.0.0"
__all__ = [
    "ResumeVersionManager",
    "ResumeVersion", 
    "VersionMetadata",
    "VersionStorage",
    "compare_versions",
    "export_version", 
    "import_version"
]
