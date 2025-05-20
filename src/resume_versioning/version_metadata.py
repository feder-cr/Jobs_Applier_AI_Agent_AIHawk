"""
Version Metadata Module

This module defines data classes and enums for managing resume version metadata.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
import uuid


class VersionType(Enum):
    """Enum for different types of resume versions."""
    GENERAL = "general"
    TECH = "tech"
    MANAGEMENT = "management"
    SALES = "sales"
    MARKETING = "marketing"
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    CUSTOM = "custom"


class VersionStatus(Enum):
    """Enum for version status."""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DRAFT = "draft"
    TEMPLATE = "template"


@dataclass
class VersionMetadata:
    """
    Data class to store metadata for a resume version.
    
    Attributes:
        version_id: Unique identifier for the version
        name: Human-readable name for the version
        version_type: Type of resume (tech, management, etc.)
        description: Detailed description of the version
        created_date: When the version was created
        modified_date: When the version was last modified
        status: Current status of the version
        tags: List of tags for categorization
        target_companies: List of companies this version targets
        target_roles: List of roles this version targets
        file_path: Path to the resume file
        metadata_path: Path to the metadata file
        is_default: Whether this is the default version
        parent_version_id: ID of the parent version (for derivatives)
        notes: Additional notes about the version
    """
    version_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    version_type: VersionType = VersionType.GENERAL
    description: str = ""
    created_date: datetime = field(default_factory=datetime.now)
    modified_date: datetime = field(default_factory=datetime.now)
    status: VersionStatus = VersionStatus.DRAFT
    tags: List[str] = field(default_factory=list)
    target_companies: List[str] = field(default_factory=list)
    target_roles: List[str] = field(default_factory=list)
    file_path: str = ""
    metadata_path: str = ""
    is_default: bool = False
    parent_version_id: Optional[str] = None
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the metadata to a dictionary for serialization."""
        return {
            'version_id': self.version_id,
            'name': self.name,
            'version_type': self.version_type.value,
            'description': self.description,
            'created_date': self.created_date.isoformat(),
            'modified_date': self.modified_date.isoformat(),
            'status': self.status.value,
            'tags': self.tags,
            'target_companies': self.target_companies,
            'target_roles': self.target_roles,
            'file_path': self.file_path,
            'metadata_path': self.metadata_path,
            'is_default': self.is_default,
            'parent_version_id': self.parent_version_id,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VersionMetadata':
        """Create a VersionMetadata instance from a dictionary."""
        # Convert string dates back to datetime objects
        created_date = datetime.fromisoformat(data.get('created_date', datetime.now().isoformat()))
        modified_date = datetime.fromisoformat(data.get('modified_date', datetime.now().isoformat()))
        
        # Convert string enums back to enum objects
        version_type = VersionType(data.get('version_type', VersionType.GENERAL.value))
        status = VersionStatus(data.get('status', VersionStatus.DRAFT.value))
        
        return cls(
            version_id=data.get('version_id', str(uuid.uuid4())),
            name=data.get('name', ''),
            version_type=version_type,
            description=data.get('description', ''),
            created_date=created_date,
            modified_date=modified_date,
            status=status,
            tags=data.get('tags', []),
            target_companies=data.get('target_companies', []),
            target_roles=data.get('target_roles', []),
            file_path=data.get('file_path', ''),
            metadata_path=data.get('metadata_path', ''),
            is_default=data.get('is_default', False),
            parent_version_id=data.get('parent_version_id'),
            notes=data.get('notes', '')
        )
    
    def update_modified_date(self):
        """Update the modified date to current time."""
        self.modified_date = datetime.now()
