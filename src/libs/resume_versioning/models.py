"""
Data models for resume versioning system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
import uuid


@dataclass
class VersionMetadata:
    """Metadata for a resume version."""
    version_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    file_size: int = 0
    checksum: str = ""
    is_active: bool = False
    parent_version_id: Optional[str] = None
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to this version."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.modified_at = datetime.now()
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from this version."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.modified_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            'version_id': self.version_id,
            'name': self.name,
            'description': self.description,
            'tags': self.tags,
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat(),
            'file_size': self.file_size,
            'checksum': self.checksum,
            'is_active': self.is_active,
            'parent_version_id': self.parent_version_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VersionMetadata':
        """Create metadata from dictionary."""
        metadata = cls()
        metadata.version_id = data.get('version_id', metadata.version_id)
        metadata.name = data.get('name', '')
        metadata.description = data.get('description', '')
        metadata.tags = data.get('tags', [])
        metadata.created_at = datetime.fromisoformat(data.get('created_at', metadata.created_at.isoformat()))
        metadata.modified_at = datetime.fromisoformat(data.get('modified_at', metadata.modified_at.isoformat()))
        metadata.file_size = data.get('file_size', 0)
        metadata.checksum = data.get('checksum', '')
        metadata.is_active = data.get('is_active', False)
        metadata.parent_version_id = data.get('parent_version_id')
        return metadata


@dataclass
class ResumeVersion:
    """Represents a complete resume version with content and metadata."""
    metadata: VersionMetadata
    content: Dict[str, Any]  # Resume content in YAML format
    file_path: Optional[Path] = None
    
    def __post_init__(self):
        """Post-initialization processing."""
        if self.file_path:
            self.file_path = Path(self.file_path)
    
    @property
    def version_id(self) -> str:
        """Get the version ID."""
        return self.metadata.version_id
    
    @property
    def name(self) -> str:
        """Get the version name."""
        return self.metadata.name
    
    @property
    def tags(self) -> List[str]:
        """Get the version tags."""
        return self.metadata.tags
    
    def update_content(self, new_content: Dict[str, Any]) -> None:
        """Update the resume content."""
        self.content = new_content
        self.metadata.modified_at = datetime.now()
    
    def clone(self, new_name: str = "", new_description: str = "") -> 'ResumeVersion':
        """Create a copy of this version with new metadata."""
        new_metadata = VersionMetadata(
            name=new_name or f"{self.metadata.name}_copy",
            description=new_description or f"Copy of {self.metadata.name}",
            tags=self.metadata.tags.copy(),
            parent_version_id=self.metadata.version_id
        )
        
        return ResumeVersion(
            metadata=new_metadata,
            content=self.content.copy()
        )


@dataclass
class VersionComparison:
    """Result of comparing two resume versions."""
    version1: ResumeVersion
    version2: ResumeVersion
    differences: Dict[str, Any]
    similarity_score: float
    
    def get_summary(self) -> str:
        """Get a summary of the comparison."""
        return f"Versions '{self.version1.name}' and '{self.version2.name}' are {self.similarity_score:.1%} similar"
