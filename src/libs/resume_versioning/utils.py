"""
Utility functions for resume versioning.
"""

import json
import yaml
import zipfile
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime
from loguru import logger
import difflib

from .models import ResumeVersion, VersionComparison


def compare_versions(version1: ResumeVersion, version2: ResumeVersion) -> VersionComparison:
    """Compare two resume versions and return differences."""
    
    def _flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """Flatten nested dictionary for comparison."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(_flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                items.append((new_key, str(v)))
            else:
                items.append((new_key, str(v)))
        return dict(items)
    
    # Flatten both contents for comparison
    flat1 = _flatten_dict(version1.content)
    flat2 = _flatten_dict(version2.content)
    
    # Find differences
    differences = {}
    all_keys = set(flat1.keys()) | set(flat2.keys())
    
    for key in all_keys:
        val1 = flat1.get(key, "")
        val2 = flat2.get(key, "")
        
        if val1 != val2:
            differences[key] = {
                'version1': val1,
                'version2': val2,
                'diff': list(difflib.unified_diff(
                    val1.splitlines(keepends=True),
                    val2.splitlines(keepends=True),
                    fromfile=f"{version1.name}",
                    tofile=f"{version2.name}",
                    lineterm=""
                ))
            }
    
    # Calculate similarity score
    total_keys = len(all_keys)
    different_keys = len(differences)
    similarity_score = (total_keys - different_keys) / total_keys if total_keys > 0 else 1.0
    
    return VersionComparison(
        version1=version1,
        version2=version2,
        differences=differences,
        similarity_score=similarity_score
    )


def export_version(version: ResumeVersion, export_path: Path) -> bool:
    """Export a resume version to a zip file."""
    try:
        export_path = Path(export_path)
        export_path.parent.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add metadata
            metadata_json = json.dumps(version.metadata.to_dict(), indent=2, ensure_ascii=False)
            zipf.writestr("metadata.json", metadata_json)
            
            # Add content
            content_yaml = yaml.dump(version.content, default_flow_style=False, allow_unicode=True)
            zipf.writestr("content.yaml", content_yaml)
            
            # Add export info
            export_info = {
                'exported_at': datetime.now().isoformat(),
                'export_version': '1.0',
                'original_version_id': version.version_id
            }
            zipf.writestr("export_info.json", json.dumps(export_info, indent=2))
        
        logger.info(f"Exported version {version.name} to {export_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to export version {version.name}: {e}")
        return False


def import_version(import_path: Path, new_name: str = None) -> ResumeVersion:
    """Import a resume version from a zip file."""
    try:
        import_path = Path(import_path)
        
        if not import_path.exists():
            raise FileNotFoundError(f"Import file not found: {import_path}")
        
        with zipfile.ZipFile(import_path, 'r') as zipf:
            # Load metadata
            metadata_json = zipf.read("metadata.json").decode('utf-8')
            metadata_dict = json.loads(metadata_json)
            
            # Load content
            content_yaml = zipf.read("content.yaml").decode('utf-8')
            content = yaml.safe_load(content_yaml)
            
            # Load export info if available
            try:
                export_info_json = zipf.read("export_info.json").decode('utf-8')
                export_info = json.loads(export_info_json)
                logger.info(f"Importing version exported at {export_info.get('exported_at')}")
            except KeyError:
                logger.warning("No export info found in import file")
        
        # Create new version with updated metadata
        from .models import VersionMetadata
        metadata = VersionMetadata.from_dict(metadata_dict)
        
        # Update name if provided
        if new_name:
            metadata.name = new_name
        
        # Generate new ID to avoid conflicts
        import uuid
        metadata.version_id = str(uuid.uuid4())
        metadata.created_at = datetime.now()
        metadata.modified_at = datetime.now()
        
        version = ResumeVersion(
            metadata=metadata,
            content=content
        )
        
        logger.info(f"Imported version {version.name}")
        return version
        
    except Exception as e:
        logger.error(f"Failed to import version from {import_path}: {e}")
        raise


def generate_version_report(versions: List[ResumeVersion]) -> str:
    """Generate a text report of all versions."""
    if not versions:
        return "No resume versions found."
    
    report_lines = [
        "Resume Version Report",
        "=" * 50,
        f"Total versions: {len(versions)}",
        ""
    ]
    
    # Group by tags
    tag_groups = {}
    untagged = []
    
    for version in versions:
        if version.tags:
            for tag in version.tags:
                if tag not in tag_groups:
                    tag_groups[tag] = []
                tag_groups[tag].append(version)
        else:
            untagged.append(version)
    
    # Add tagged versions
    for tag, tag_versions in tag_groups.items():
        report_lines.extend([
            f"Tag: {tag} ({len(tag_versions)} versions)",
            "-" * 30
        ])
        
        for version in sorted(tag_versions, key=lambda v: v.metadata.created_at, reverse=True):
            status = " [ACTIVE]" if version.metadata.is_active else ""
            report_lines.append(
                f"  • {version.name}{status} - {version.metadata.created_at.strftime('%Y-%m-%d %H:%M')}"
            )
            if version.metadata.description:
                report_lines.append(f"    {version.metadata.description}")
        
        report_lines.append("")
    
    # Add untagged versions
    if untagged:
        report_lines.extend([
            "Untagged versions",
            "-" * 30
        ])
        
        for version in sorted(untagged, key=lambda v: v.metadata.created_at, reverse=True):
            status = " [ACTIVE]" if version.metadata.is_active else ""
            report_lines.append(
                f"  • {version.name}{status} - {version.metadata.created_at.strftime('%Y-%m-%d %H:%M')}"
            )
            if version.metadata.description:
                report_lines.append(f"    {version.metadata.description}")
    
    return "\n".join(report_lines)


def validate_resume_content(content: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate resume content structure."""
    errors = []
    required_sections = ['personal_information']
    
    for section in required_sections:
        if section not in content:
            errors.append(f"Missing required section: {section}")
    
    # Validate personal information
    if 'personal_information' in content:
        personal_info = content['personal_information']
        required_fields = ['name', 'email']
        
        for field in required_fields:
            if field not in personal_info or not personal_info[field]:
                errors.append(f"Missing required field in personal_information: {field}")
    
    return len(errors) == 0, errors
