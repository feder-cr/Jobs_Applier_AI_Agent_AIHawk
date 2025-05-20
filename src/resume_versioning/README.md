# Resume Versioning Module

This module provides comprehensive functionality to manage different versions of user resumes, allowing users to organize, track, and manage multiple resume variants for different job applications and purposes.

## Features

### Core Functionality
- **Version Management**: Create, update, and organize multiple resume versions
- **Metadata Tracking**: Store detailed information about each version including purpose, target companies, and roles
- **Version Comparison**: Compare different versions to see changes and differences
- **Default Version**: Set and manage a default resume version
- **Status Management**: Track version status (active, archived, draft, template)

### Organization Features
- **Categorization**: Organize resumes by type (tech, management, sales, etc.)
- **Tagging System**: Add custom tags for easy filtering and searching
- **Target Tracking**: Associate versions with specific companies and roles
- **Parent-Child Relationships**: Track version lineage and derivatives

### Storage & Backup
- **Organized Storage**: Automatic file organization with metadata
- **Backup System**: Create backups before deletion or major changes
- **YAML Metadata**: Human-readable metadata storage
- **Version History**: Track creation and modification dates

## Module Structure

```
src/resume_versioning/
├── __init__.py                 # Module initialization
├── resume_version_manager.py   # Main management class
├── version_metadata.py         # Data classes and enums
├── storage_handler.py          # File storage and organization
├── templates/
│   └── version_template.yaml   # Template for version metadata
└── README.md                   # This file
```

## Usage

### Basic Usage

```python
from src.resume_versioning import ResumeVersionManager, VersionType

# Initialize the manager
manager = ResumeVersionManager()

# Create a new version
version_id = manager.create_version(
    name="Tech Resume - Software Engineer",
    resume_content=resume_text,
    version_type=VersionType.TECH,
    description="Tailored for software engineering positions",
    tags=["python", "web-development", "backend"],
    target_companies=["Google", "Microsoft", "Amazon"],
    target_roles=["Software Engineer", "Backend Developer"]
)

# List all versions
versions = manager.list_versions()

# Set as default
manager.set_default_version(version_id)

# Compare versions
comparison = manager.compare_versions(version_id1, version_id2)
```

### Integration with Main Application

The module is integrated into the main AIHawk application through the "Manage Resume Versions" menu option, providing a user-friendly interface for all versioning operations.

## Data Classes

### VersionType Enum
- `GENERAL`: General purpose resume
- `TECH`: Technology-focused resume
- `MANAGEMENT`: Management and leadership roles
- `SALES`: Sales and business development
- `MARKETING`: Marketing and communications
- `FINANCE`: Finance and accounting
- `HEALTHCARE`: Healthcare and medical
- `EDUCATION`: Education and academic
- `CUSTOM`: Custom category

### VersionStatus Enum
- `ACTIVE`: Currently active version
- `ARCHIVED`: Archived version
- `DRAFT`: Work in progress
- `TEMPLATE`: Template for creating new versions

### VersionMetadata Class
Stores comprehensive metadata for each version including:
- Unique identifier and name
- Type and status
- Creation and modification dates
- Tags and target information
- File paths and relationships
- Additional notes

## Storage Structure

The module creates the following directory structure:

```
data_folder/resume_versions/
├── versions/           # Resume content files
│   └── {version_id}/
│       └── resume.txt
├── metadata/           # Version metadata files
│   └── {version_id}.yaml
├── backups/           # Backup files
│   └── {version_id}_{timestamp}/
└── templates/         # Template files
```

## Error Handling

The module includes comprehensive error handling and logging:
- File system errors are caught and logged
- Invalid operations are prevented with user-friendly messages
- Backup creation before destructive operations
- Graceful degradation when files are missing

## Future Enhancements

Potential future improvements:
- Integration with version control systems
- Automated resume optimization suggestions
- Export to different formats (PDF, Word, etc.)
- Cloud storage integration
- Collaborative editing features
- AI-powered resume analysis and recommendations

## Dependencies

- `pathlib`: File path handling
- `yaml`: Metadata serialization
- `datetime`: Timestamp management
- `uuid`: Unique identifier generation
- `difflib`: Version comparison
- `dataclasses`: Data structure definitions
- `enum`: Enumeration types
- `typing`: Type hints

## Contributing

When contributing to this module:
1. Follow the existing code style and patterns
2. Add comprehensive error handling
3. Include logging for important operations
4. Update tests for new functionality
5. Document new features in this README
