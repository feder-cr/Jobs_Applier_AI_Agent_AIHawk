"""
Storage management for resume versions.
"""

import json
import yaml
import hashlib
from pathlib import Path
from typing import List, Optional, Dict, Any
from loguru import logger

from .models import ResumeVersion, VersionMetadata


class VersionStorage:
    """Manages storage and retrieval of resume versions."""
    
    def __init__(self, storage_dir: Path = None):
        """Initialize storage manager."""
        self.storage_dir = storage_dir or Path("data_folder/resume_versions")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.versions_dir = self.storage_dir / "versions"
        self.metadata_dir = self.storage_dir / "metadata"
        self.exports_dir = self.storage_dir / "exports"
        
        for dir_path in [self.versions_dir, self.metadata_dir, self.exports_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.index_file = self.storage_dir / "index.json"
        self._load_index()
    
    def _load_index(self) -> None:
        """Load the version index."""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    self.index = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load index file: {e}")
                self.index = {}
        else:
            self.index = {}
    
    def _save_index(self) -> None:
        """Save the version index."""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save index file: {e}")
    
    def _calculate_checksum(self, content: Dict[str, Any]) -> str:
        """Calculate checksum for content."""
        content_str = json.dumps(content, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(content_str.encode('utf-8')).hexdigest()
    
    def save_version(self, version: ResumeVersion) -> bool:
        """Save a resume version to storage."""
        try:
            # Calculate checksum
            version.metadata.checksum = self._calculate_checksum(version.content)
            
            # Save content
            content_file = self.versions_dir / f"{version.version_id}.yaml"
            with open(content_file, 'w', encoding='utf-8') as f:
                yaml.dump(version.content, f, default_flow_style=False, allow_unicode=True)
            
            # Save metadata
            metadata_file = self.metadata_dir / f"{version.version_id}.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(version.metadata.to_dict(), f, indent=2, ensure_ascii=False)
            
            # Update index
            self.index[version.version_id] = {
                'name': version.metadata.name,
                'created_at': version.metadata.created_at.isoformat(),
                'tags': version.metadata.tags,
                'is_active': version.metadata.is_active
            }
            self._save_index()
            
            # Update file size
            version.metadata.file_size = content_file.stat().st_size
            
            logger.info(f"Saved resume version: {version.metadata.name} ({version.version_id})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save version {version.version_id}: {e}")
            return False
    
    def load_version(self, version_id: str) -> Optional[ResumeVersion]:
        """Load a resume version from storage."""
        try:
            # Load metadata
            metadata_file = self.metadata_dir / f"{version_id}.json"
            if not metadata_file.exists():
                logger.warning(f"Metadata file not found for version {version_id}")
                return None
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata_dict = json.load(f)
            metadata = VersionMetadata.from_dict(metadata_dict)
            
            # Load content
            content_file = self.versions_dir / f"{version_id}.yaml"
            if not content_file.exists():
                logger.warning(f"Content file not found for version {version_id}")
                return None
            
            with open(content_file, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
            
            version = ResumeVersion(
                metadata=metadata,
                content=content,
                file_path=content_file
            )
            
            return version
            
        except Exception as e:
            logger.error(f"Failed to load version {version_id}: {e}")
            return None
    
    def list_versions(self, tags: List[str] = None) -> List[VersionMetadata]:
        """List all versions, optionally filtered by tags."""
        versions = []
        
        for version_id in self.index.keys():
            version = self.load_version(version_id)
            if version:
                # Filter by tags if specified
                if tags:
                    if not any(tag in version.metadata.tags for tag in tags):
                        continue
                versions.append(version.metadata)
        
        # Sort by creation date (newest first)
        versions.sort(key=lambda v: v.created_at, reverse=True)
        return versions
    
    def delete_version(self, version_id: str) -> bool:
        """Delete a version from storage."""
        try:
            # Remove files
            content_file = self.versions_dir / f"{version_id}.yaml"
            metadata_file = self.metadata_dir / f"{version_id}.json"
            
            if content_file.exists():
                content_file.unlink()
            if metadata_file.exists():
                metadata_file.unlink()
            
            # Remove from index
            if version_id in self.index:
                del self.index[version_id]
                self._save_index()
            
            logger.info(f"Deleted version {version_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete version {version_id}: {e}")
            return False
    
    def get_active_version(self) -> Optional[ResumeVersion]:
        """Get the currently active version."""
        for version_id, info in self.index.items():
            if info.get('is_active', False):
                return self.load_version(version_id)
        return None
    
    def set_active_version(self, version_id: str) -> bool:
        """Set a version as the active one."""
        try:
            # Deactivate all versions
            for vid in self.index.keys():
                version = self.load_version(vid)
                if version:
                    version.metadata.is_active = False
                    self.save_version(version)
            
            # Activate the specified version
            version = self.load_version(version_id)
            if version:
                version.metadata.is_active = True
                return self.save_version(version)
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to set active version {version_id}: {e}")
            return False
