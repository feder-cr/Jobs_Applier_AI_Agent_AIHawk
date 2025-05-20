"""
Main manager class for resume versioning functionality.
"""

import yaml
from pathlib import Path
from typing import List, Optional, Dict, Any
from loguru import logger

from .models import ResumeVersion, VersionMetadata, VersionComparison
from .storage import VersionStorage
from .utils import compare_versions, export_version, import_version, validate_resume_content


class ResumeVersionManager:
    """Main class for managing resume versions."""
    
    def __init__(self, storage_dir: Path = None):
        """Initialize the version manager."""
        self.storage = VersionStorage(storage_dir)
        logger.info("Resume Version Manager initialized")
    
    def create_version(self, 
                      content: Dict[str, Any], 
                      name: str, 
                      description: str = "",
                      tags: List[str] = None) -> Optional[ResumeVersion]:
        """Create a new resume version."""
        try:
            # Validate content
            is_valid, errors = validate_resume_content(content)
            if not is_valid:
                logger.error(f"Invalid resume content: {errors}")
                return None
            
            # Create metadata
            metadata = VersionMetadata(
                name=name,
                description=description,
                tags=tags or []
            )
            
            # Create version
            version = ResumeVersion(
                metadata=metadata,
                content=content
            )
            
            # Save to storage
            if self.storage.save_version(version):
                logger.info(f"Created new resume version: {name}")
                return version
            else:
                logger.error(f"Failed to save resume version: {name}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating version: {e}")
            return None
    
    def create_version_from_file(self, 
                                file_path: Path, 
                                name: str, 
                                description: str = "",
                                tags: List[str] = None) -> Optional[ResumeVersion]:
        """Create a version from a YAML file."""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
            
            return self.create_version(content, name, description, tags)
            
        except Exception as e:
            logger.error(f"Error creating version from file {file_path}: {e}")
            return None
    
    def get_version(self, version_id: str) -> Optional[ResumeVersion]:
        """Get a specific version by ID."""
        return self.storage.load_version(version_id)
    
    def list_versions(self, tags: List[str] = None) -> List[VersionMetadata]:
        """List all versions, optionally filtered by tags."""
        return self.storage.list_versions(tags)
    
    def delete_version(self, version_id: str) -> bool:
        """Delete a version."""
        version = self.storage.load_version(version_id)
        if not version:
            logger.error(f"Version not found: {version_id}")
            return False
        
        if version.metadata.is_active:
            logger.warning(f"Cannot delete active version: {version.metadata.name}")
            return False
        
        return self.storage.delete_version(version_id)
    
    def update_version(self, 
                      version_id: str, 
                      name: str = None, 
                      description: str = None, 
                      tags: List[str] = None) -> bool:
        """Update version metadata."""
        version = self.storage.load_version(version_id)
        if not version:
            logger.error(f"Version not found: {version_id}")
            return False
        
        # Update metadata
        if name is not None:
            version.metadata.name = name
        if description is not None:
            version.metadata.description = description
        if tags is not None:
            version.metadata.tags = tags
        
        return self.storage.save_version(version)
    
    def add_tag(self, version_id: str, tag: str) -> bool:
        """Add a tag to a version."""
        version = self.storage.load_version(version_id)
        if not version:
            logger.error(f"Version not found: {version_id}")
            return False
        
        version.metadata.add_tag(tag)
        return self.storage.save_version(version)
    
    def remove_tag(self, version_id: str, tag: str) -> bool:
        """Remove a tag from a version."""
        version = self.storage.load_version(version_id)
        if not version:
            logger.error(f"Version not found: {version_id}")
            return False
        
        version.metadata.remove_tag(tag)
        return self.storage.save_version(version)
    
    def compare_versions(self, version_id1: str, version_id2: str) -> Optional[VersionComparison]:
        """Compare two versions."""
        version1 = self.storage.load_version(version_id1)
        version2 = self.storage.load_version(version_id2)
        
        if not version1:
            logger.error(f"Version not found: {version_id1}")
            return None
        if not version2:
            logger.error(f"Version not found: {version_id2}")
            return None
        
        return compare_versions(version1, version2)
    
    def clone_version(self, version_id: str, new_name: str, new_description: str = "") -> Optional[ResumeVersion]:
        """Create a copy of an existing version."""
        original = self.storage.load_version(version_id)
        if not original:
            logger.error(f"Version not found: {version_id}")
            return None
        
        cloned = original.clone(new_name, new_description)
        
        if self.storage.save_version(cloned):
            logger.info(f"Cloned version {original.name} to {new_name}")
            return cloned
        else:
            logger.error(f"Failed to save cloned version: {new_name}")
            return None
    
    def get_active_version(self) -> Optional[ResumeVersion]:
        """Get the currently active version."""
        return self.storage.get_active_version()
    
    def set_active_version(self, version_id: str) -> bool:
        """Set a version as active."""
        return self.storage.set_active_version(version_id)
    
    def export_version(self, version_id: str, export_path: Path) -> bool:
        """Export a version to a file."""
        version = self.storage.load_version(version_id)
        if not version:
            logger.error(f"Version not found: {version_id}")
            return False
        
        return export_version(version, export_path)
    
    def import_version(self, import_path: Path, new_name: str = None) -> Optional[ResumeVersion]:
        """Import a version from a file."""
        try:
            version = import_version(import_path, new_name)
            
            if self.storage.save_version(version):
                logger.info(f"Imported version: {version.name}")
                return version
            else:
                logger.error(f"Failed to save imported version: {version.name}")
                return None
                
        except Exception as e:
            logger.error(f"Error importing version: {e}")
            return None
    
    def restore_version_to_main(self, version_id: str, main_resume_path: Path) -> bool:
        """Restore a version to the main resume file."""
        version = self.storage.load_version(version_id)
        if not version:
            logger.error(f"Version not found: {version_id}")
            return False
        
        try:
            main_resume_path = Path(main_resume_path)
            
            # Backup current main resume
            backup_path = main_resume_path.with_suffix('.backup.yaml')
            if main_resume_path.exists():
                main_resume_path.rename(backup_path)
                logger.info(f"Backed up current resume to {backup_path}")
            
            # Write version content to main resume
            with open(main_resume_path, 'w', encoding='utf-8') as f:
                yaml.dump(version.content, f, default_flow_style=False, allow_unicode=True)
            
            logger.info(f"Restored version {version.name} to {main_resume_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring version to main resume: {e}")
            return False
    
    def get_version_statistics(self) -> Dict[str, Any]:
        """Get statistics about all versions."""
        versions = [self.storage.load_version(vid) for vid in self.storage.index.keys()]
        versions = [v for v in versions if v is not None]
        
        if not versions:
            return {"total_versions": 0}
        
        # Collect statistics
        total_versions = len(versions)
        active_version = next((v for v in versions if v.metadata.is_active), None)
        
        # Tag statistics
        all_tags = []
        for version in versions:
            all_tags.extend(version.metadata.tags)
        
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Size statistics
        total_size = sum(v.metadata.file_size for v in versions)
        avg_size = total_size / total_versions if total_versions > 0 else 0
        
        return {
            "total_versions": total_versions,
            "active_version": active_version.name if active_version else None,
            "total_storage_size": total_size,
            "average_version_size": avg_size,
            "tag_counts": tag_counts,
            "oldest_version": min(versions, key=lambda v: v.metadata.created_at).metadata.created_at.isoformat(),
            "newest_version": max(versions, key=lambda v: v.metadata.created_at).metadata.created_at.isoformat()
        }
