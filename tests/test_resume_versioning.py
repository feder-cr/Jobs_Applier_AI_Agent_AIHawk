"""
Unit tests for the resume versioning module.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from src.libs.resume_versioning import ResumeVersionManager
from src.libs.resume_versioning.models import ResumeVersion, VersionMetadata


class TestResumeVersioning(unittest.TestCase):
    """Test cases for resume versioning functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.manager = ResumeVersionManager(storage_dir=self.temp_dir)
        
        # Sample resume content
        self.sample_content = {
            'personal_information': {
                'name': 'John Doe',
                'email': 'john.doe@example.com',
                'phone': '+1-555-0123',
                'location': 'New York, NY'
            },
            'work_experience': [
                {
                    'company': 'Tech Corp',
                    'position': 'Software Engineer',
                    'start_date': '2020-01-01',
                    'end_date': '2023-12-31',
                    'description': 'Developed web applications'
                }
            ],
            'education': [
                {
                    'institution': 'University of Technology',
                    'degree': 'Bachelor of Science in Computer Science',
                    'graduation_date': '2019-05-15'
                }
            ]
        }
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_version(self):
        """Test creating a new version."""
        version = self.manager.create_version(
            content=self.sample_content,
            name="Test Version",
            description="A test version",
            tags=["test", "sample"]
        )
        
        self.assertIsNotNone(version)
        self.assertEqual(version.name, "Test Version")
        self.assertEqual(version.metadata.description, "A test version")
        self.assertIn("test", version.tags)
        self.assertIn("sample", version.tags)
    
    def test_list_versions(self):
        """Test listing versions."""
        # Create multiple versions
        version1 = self.manager.create_version(
            content=self.sample_content,
            name="Version 1",
            tags=["tech"]
        )
        version2 = self.manager.create_version(
            content=self.sample_content,
            name="Version 2",
            tags=["marketing"]
        )
        
        # List all versions
        all_versions = self.manager.list_versions()
        self.assertEqual(len(all_versions), 2)
        
        # List versions by tag
        tech_versions = self.manager.list_versions(tags=["tech"])
        self.assertEqual(len(tech_versions), 1)
        self.assertEqual(tech_versions[0].name, "Version 1")
    
    def test_update_version(self):
        """Test updating version metadata."""
        version = self.manager.create_version(
            content=self.sample_content,
            name="Original Name",
            description="Original description"
        )
        
        # Update the version
        success = self.manager.update_version(
            version_id=version.version_id,
            name="Updated Name",
            description="Updated description",
            tags=["updated"]
        )
        
        self.assertTrue(success)
        
        # Verify the update
        updated_version = self.manager.get_version(version.version_id)
        self.assertEqual(updated_version.name, "Updated Name")
        self.assertEqual(updated_version.metadata.description, "Updated description")
        self.assertIn("updated", updated_version.tags)
    
    def test_clone_version(self):
        """Test cloning a version."""
        original = self.manager.create_version(
            content=self.sample_content,
            name="Original Version",
            tags=["original"]
        )
        
        cloned = self.manager.clone_version(
            version_id=original.version_id,
            new_name="Cloned Version",
            new_description="A cloned version"
        )
        
        self.assertIsNotNone(cloned)
        self.assertEqual(cloned.name, "Cloned Version")
        self.assertEqual(cloned.metadata.description, "A cloned version")
        self.assertIn("original", cloned.tags)  # Tags should be copied
        self.assertNotEqual(cloned.version_id, original.version_id)  # Different IDs
    
    def test_active_version(self):
        """Test setting and getting active version."""
        version1 = self.manager.create_version(
            content=self.sample_content,
            name="Version 1"
        )
        version2 = self.manager.create_version(
            content=self.sample_content,
            name="Version 2"
        )
        
        # Set version1 as active
        success = self.manager.set_active_version(version1.version_id)
        self.assertTrue(success)
        
        # Get active version
        active = self.manager.get_active_version()
        self.assertIsNotNone(active)
        self.assertEqual(active.version_id, version1.version_id)
        
        # Set version2 as active
        success = self.manager.set_active_version(version2.version_id)
        self.assertTrue(success)
        
        # Verify version2 is now active
        active = self.manager.get_active_version()
        self.assertEqual(active.version_id, version2.version_id)
    
    def test_compare_versions(self):
        """Test comparing versions."""
        content1 = self.sample_content.copy()
        content2 = self.sample_content.copy()
        content2['personal_information']['name'] = 'Jane Doe'
        
        version1 = self.manager.create_version(content1, "Version 1")
        version2 = self.manager.create_version(content2, "Version 2")
        
        comparison = self.manager.compare_versions(version1.version_id, version2.version_id)
        
        self.assertIsNotNone(comparison)
        self.assertLess(comparison.similarity_score, 1.0)  # Should be different
        self.assertIn('personal_information.name', comparison.differences)
    
    def test_tag_management(self):
        """Test adding and removing tags."""
        version = self.manager.create_version(
            content=self.sample_content,
            name="Test Version",
            tags=["initial"]
        )
        
        # Add a tag
        success = self.manager.add_tag(version.version_id, "new_tag")
        self.assertTrue(success)
        
        # Verify tag was added
        updated_version = self.manager.get_version(version.version_id)
        self.assertIn("new_tag", updated_version.tags)
        self.assertIn("initial", updated_version.tags)
        
        # Remove a tag
        success = self.manager.remove_tag(version.version_id, "initial")
        self.assertTrue(success)
        
        # Verify tag was removed
        updated_version = self.manager.get_version(version.version_id)
        self.assertNotIn("initial", updated_version.tags)
        self.assertIn("new_tag", updated_version.tags)
    
    def test_statistics(self):
        """Test getting version statistics."""
        # Create some versions
        version1 = self.manager.create_version(
            content=self.sample_content,
            name="Version 1",
            tags=["tech", "senior"]
        )
        version2 = self.manager.create_version(
            content=self.sample_content,
            name="Version 2",
            tags=["tech", "junior"]
        )
        
        self.manager.set_active_version(version1.version_id)
        
        stats = self.manager.get_version_statistics()
        
        self.assertEqual(stats['total_versions'], 2)
        self.assertEqual(stats['active_version'], "Version 1")
        self.assertEqual(stats['tag_counts']['tech'], 2)
        self.assertEqual(stats['tag_counts']['senior'], 1)
        self.assertEqual(stats['tag_counts']['junior'], 1)


if __name__ == '__main__':
    unittest.main()
