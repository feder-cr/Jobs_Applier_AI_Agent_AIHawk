"""
Resume Version Manager Module

This module provides the main interface for managing resume versions.
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
import difflib
from datetime import datetime

from .version_metadata import VersionMetadata, VersionType, VersionStatus
from .storage_handler import StorageHandler
from src.logging import logger


class ResumeVersionManager:
    """
    Main class for managing resume versions.
    
    This class provides a high-level interface for creating, managing,
    and organizing different versions of user resumes.
    """
    
    def __init__(self, base_path: str = "data_folder/resume_versions"):
        """
        Initialize the resume version manager.
        
        Args:
            base_path: Base directory for storing resume versions
        """
        self.storage = StorageHandler(base_path)
        logger.info("Resume Version Manager initialized")
    
    def create_version(self, 
                      name: str,
                      resume_content: str,
                      version_type: VersionType = VersionType.GENERAL,
                      description: str = "",
                      tags: List[str] = None,
                      target_companies: List[str] = None,
                      target_roles: List[str] = None,
                      notes: str = "",
                      parent_version_id: Optional[str] = None) -> Optional[str]:
        """
        Create a new resume version.
        
        Args:
            name: Name for the version
            resume_content: Content of the resume
            version_type: Type of resume
            description: Description of the version
            tags: List of tags for categorization
            target_companies: List of target companies
            target_roles: List of target roles
            notes: Additional notes
            parent_version_id: ID of parent version if this is a derivative
            
        Returns:
            Version ID if successful, None otherwise
        """
        try:
            # Create metadata
            metadata = VersionMetadata(
                name=name,
                version_type=version_type,
                description=description,
                status=VersionStatus.ACTIVE,
                tags=tags or [],
                target_companies=target_companies or [],
                target_roles=target_roles or [],
                notes=notes,
                parent_version_id=parent_version_id
            )
            
            # Save the version
            if self.storage.save_version(metadata, resume_content):
                logger.info(f"Created new resume version: {name} ({metadata.version_id})")
                return metadata.version_id
            else:
                logger.error(f"Failed to create resume version: {name}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating resume version: {e}")
            return None
    
    def get_version(self, version_id: str) -> Optional[VersionMetadata]:
        """
        Get metadata for a specific version.
        
        Args:
            version_id: ID of the version
            
        Returns:
            VersionMetadata or None if not found
        """
        return self.storage.load_metadata(version_id)
    
    def get_version_content(self, version_id: str) -> Optional[str]:
        """
        Get content for a specific version.
        
        Args:
            version_id: ID of the version
            
        Returns:
            Resume content as string or None if not found
        """
        return self.storage.load_resume_content(version_id)
    
    def list_versions(self, 
                     status_filter: Optional[VersionStatus] = None,
                     type_filter: Optional[VersionType] = None,
                     tag_filter: Optional[str] = None) -> List[VersionMetadata]:
        """
        List all versions with optional filtering.
        
        Args:
            status_filter: Filter by status
            type_filter: Filter by type
            tag_filter: Filter by tag
            
        Returns:
            List of VersionMetadata objects
        """
        versions = self.storage.list_all_versions()
        
        # Apply filters
        if status_filter:
            versions = [v for v in versions if v.status == status_filter]
        
        if type_filter:
            versions = [v for v in versions if v.version_type == type_filter]
        
        if tag_filter:
            versions = [v for v in versions if tag_filter in v.tags]
        
        return versions
    
    def update_version(self, version_id: str, **kwargs) -> bool:
        """
        Update metadata for a version.
        
        Args:
            version_id: ID of the version to update
            **kwargs: Fields to update
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            metadata = self.storage.load_metadata(version_id)
            if not metadata:
                logger.warning(f"Version {version_id} not found")
                return False
            
            # Update fields
            for key, value in kwargs.items():
                if hasattr(metadata, key):
                    setattr(metadata, key, value)
            
            # Update modified date
            metadata.update_modified_date()
            
            # Save updated metadata
            return self.storage.save_metadata(metadata)
            
        except Exception as e:
            logger.error(f"Error updating version {version_id}: {e}")
            return False
    
    def set_default_version(self, version_id: str) -> bool:
        """
        Set a version as the default.
        
        Args:
            version_id: ID of the version to set as default
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # First, unset all other defaults
            all_versions = self.storage.list_all_versions()
            for version in all_versions:
                if version.is_default:
                    version.is_default = False
                    self.storage.save_metadata(version)
            
            # Set the new default
            return self.update_version(version_id, is_default=True)
            
        except Exception as e:
            logger.error(f"Error setting default version {version_id}: {e}")
            return False
    
    def get_default_version(self) -> Optional[VersionMetadata]:
        """
        Get the default version.
        
        Returns:
            VersionMetadata of default version or None if not set
        """
        versions = self.storage.list_all_versions()
        for version in versions:
            if version.is_default:
                return version
        return None
    
    def archive_version(self, version_id: str) -> bool:
        """
        Archive a version.
        
        Args:
            version_id: ID of the version to archive
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.update_version(version_id, status=VersionStatus.ARCHIVED)
    
    def delete_version(self, version_id: str, create_backup: bool = True) -> bool:
        """
        Delete a version.
        
        Args:
            version_id: ID of the version to delete
            create_backup: Whether to create a backup before deletion
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if create_backup:
                self.storage.create_backup(version_id)
            
            return self.storage.delete_version(version_id)
            
        except Exception as e:
            logger.error(f"Error deleting version {version_id}: {e}")
            return False
    
    def compare_versions(self, version_id1: str, version_id2: str) -> Optional[Dict[str, Any]]:
        """
        Compare two versions and return differences.
        
        Args:
            version_id1: ID of first version
            version_id2: ID of second version
            
        Returns:
            Dictionary with comparison results or None if error
        """
        try:
            content1 = self.storage.load_resume_content(version_id1)
            content2 = self.storage.load_resume_content(version_id2)
            metadata1 = self.storage.load_metadata(version_id1)
            metadata2 = self.storage.load_metadata(version_id2)
            
            if not all([content1, content2, metadata1, metadata2]):
                logger.error("Could not load versions for comparison")
                return None
            
            # Generate diff
            diff = list(difflib.unified_diff(
                content1.splitlines(keepends=True),
                content2.splitlines(keepends=True),
                fromfile=f"{metadata1.name} ({version_id1})",
                tofile=f"{metadata2.name} ({version_id2})",
                lineterm=""
            ))
            
            return {
                'version1': {
                    'id': version_id1,
                    'name': metadata1.name,
                    'type': metadata1.version_type.value,
                    'modified_date': metadata1.modified_date.isoformat()
                },
                'version2': {
                    'id': version_id2,
                    'name': metadata2.name,
                    'type': metadata2.version_type.value,
                    'modified_date': metadata2.modified_date.isoformat()
                },
                'diff': diff,
                'has_differences': len(diff) > 0
            }
            
        except Exception as e:
            logger.error(f"Error comparing versions: {e}")
            return None
    
    def duplicate_version(self, version_id: str, new_name: str) -> Optional[str]:
        """
        Create a duplicate of an existing version.
        
        Args:
            version_id: ID of the version to duplicate
            new_name: Name for the new version
            
        Returns:
            New version ID if successful, None otherwise
        """
        try:
            original_metadata = self.storage.load_metadata(version_id)
            original_content = self.storage.load_resume_content(version_id)
            
            if not original_metadata or not original_content:
                logger.error(f"Could not load original version {version_id}")
                return None
            
            # Create new version with same content but new metadata
            return self.create_version(
                name=new_name,
                resume_content=original_content,
                version_type=original_metadata.version_type,
                description=f"Copy of {original_metadata.name}",
                tags=original_metadata.tags.copy(),
                target_companies=original_metadata.target_companies.copy(),
                target_roles=original_metadata.target_roles.copy(),
                notes=original_metadata.notes,
                parent_version_id=version_id
            )
            
        except Exception as e:
            logger.error(f"Error duplicating version {version_id}: {e}")
            return None
