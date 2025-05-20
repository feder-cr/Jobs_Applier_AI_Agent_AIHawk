"""
Storage Handler Module

This module handles file storage and organization for resume versions.
"""

import os
import shutil
import yaml
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from .version_metadata import VersionMetadata, VersionStatus
from src.logging import logger


class StorageHandler:
    """
    Handles file storage and organization for resume versions.
    
    This class manages the file system structure for storing resume versions,
    their metadata, and provides utilities for backup and organization.
    """
    
    def __init__(self, base_path: str = "data_folder/resume_versions"):
        """
        Initialize the storage handler.
        
        Args:
            base_path: Base directory for storing resume versions
        """
        self.base_path = Path(base_path)
        self.versions_dir = self.base_path / "versions"
        self.metadata_dir = self.base_path / "metadata"
        self.backups_dir = self.base_path / "backups"
        self.templates_dir = self.base_path / "templates"
        
        # Create directory structure
        self._create_directory_structure()
    
    def _create_directory_structure(self):
        """Create the necessary directory structure."""
        directories = [
            self.base_path,
            self.versions_dir,
            self.metadata_dir,
            self.backups_dir,
            self.templates_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created directory: {directory}")
    
    def save_version(self, metadata: VersionMetadata, resume_content: str) -> bool:
        """
        Save a resume version with its metadata.
        
        Args:
            metadata: Version metadata
            resume_content: Content of the resume
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create version-specific directory
            version_dir = self.versions_dir / metadata.version_id
            version_dir.mkdir(exist_ok=True)
            
            # Save resume content
            resume_file = version_dir / f"{metadata.name.replace(' ', '_')}.txt"
            with open(resume_file, 'w', encoding='utf-8') as f:
                f.write(resume_content)
            
            # Update file paths in metadata
            metadata.file_path = str(resume_file)
            metadata.metadata_path = str(self.metadata_dir / f"{metadata.version_id}.yaml")
            
            # Save metadata
            self.save_metadata(metadata)
            
            logger.info(f"Saved resume version: {metadata.name} ({metadata.version_id})")
            return True
            
        except Exception as e:
            logger.error(f"Error saving resume version: {e}")
            return False
    
    def save_metadata(self, metadata: VersionMetadata) -> bool:
        """
        Save metadata to a YAML file.
        
        Args:
            metadata: Version metadata to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            metadata_file = self.metadata_dir / f"{metadata.version_id}.yaml"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                yaml.dump(metadata.to_dict(), f, default_flow_style=False, sort_keys=False)
            
            logger.debug(f"Saved metadata for version: {metadata.version_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
            return False
    
    def load_metadata(self, version_id: str) -> Optional[VersionMetadata]:
        """
        Load metadata for a specific version.
        
        Args:
            version_id: ID of the version to load
            
        Returns:
            VersionMetadata or None if not found
        """
        try:
            metadata_file = self.metadata_dir / f"{version_id}.yaml"
            if not metadata_file.exists():
                logger.warning(f"Metadata file not found: {metadata_file}")
                return None
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            return VersionMetadata.from_dict(data)
            
        except Exception as e:
            logger.error(f"Error loading metadata for version {version_id}: {e}")
            return None
    
    def load_resume_content(self, version_id: str) -> Optional[str]:
        """
        Load resume content for a specific version.
        
        Args:
            version_id: ID of the version to load
            
        Returns:
            Resume content as string or None if not found
        """
        try:
            metadata = self.load_metadata(version_id)
            if not metadata or not metadata.file_path:
                return None
            
            file_path = Path(metadata.file_path)
            if not file_path.exists():
                logger.warning(f"Resume file not found: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
                
        except Exception as e:
            logger.error(f"Error loading resume content for version {version_id}: {e}")
            return None
    
    def list_all_versions(self) -> List[VersionMetadata]:
        """
        List all available resume versions.
        
        Returns:
            List of VersionMetadata objects
        """
        versions = []
        
        try:
            for metadata_file in self.metadata_dir.glob("*.yaml"):
                version_id = metadata_file.stem
                metadata = self.load_metadata(version_id)
                if metadata:
                    versions.append(metadata)
            
            # Sort by modified date (newest first)
            versions.sort(key=lambda x: x.modified_date, reverse=True)
            
        except Exception as e:
            logger.error(f"Error listing versions: {e}")
        
        return versions
    
    def delete_version(self, version_id: str) -> bool:
        """
        Delete a resume version and its metadata.
        
        Args:
            version_id: ID of the version to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Load metadata to get file paths
            metadata = self.load_metadata(version_id)
            if not metadata:
                logger.warning(f"Version {version_id} not found")
                return False
            
            # Delete resume file
            if metadata.file_path and Path(metadata.file_path).exists():
                os.remove(metadata.file_path)
            
            # Delete version directory if empty
            version_dir = self.versions_dir / version_id
            if version_dir.exists():
                shutil.rmtree(version_dir)
            
            # Delete metadata file
            metadata_file = self.metadata_dir / f"{version_id}.yaml"
            if metadata_file.exists():
                os.remove(metadata_file)
            
            logger.info(f"Deleted version: {metadata.name} ({version_id})")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting version {version_id}: {e}")
            return False
    
    def create_backup(self, version_id: str) -> bool:
        """
        Create a backup of a specific version.
        
        Args:
            version_id: ID of the version to backup
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            metadata = self.load_metadata(version_id)
            if not metadata:
                return False
            
            # Create backup directory with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.backups_dir / f"{version_id}_{timestamp}"
            backup_dir.mkdir(exist_ok=True)
            
            # Copy resume file
            if metadata.file_path and Path(metadata.file_path).exists():
                shutil.copy2(metadata.file_path, backup_dir)
            
            # Copy metadata file
            metadata_file = self.metadata_dir / f"{version_id}.yaml"
            if metadata_file.exists():
                shutil.copy2(metadata_file, backup_dir)
            
            logger.info(f"Created backup for version: {version_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating backup for version {version_id}: {e}")
            return False
