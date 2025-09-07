"""
Unit tests for business layer project management
"""

import pytest
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from layers.business.project import ProjectManager


class TestProjectManager:
    """Test Project Manager"""
    
    def test_initialization(self):
        """Test project manager initialization"""
        manager = ProjectManager()
        
        assert hasattr(manager, 'projects')
        assert isinstance(manager.projects, dict)
        assert len(manager.projects) == 0
    
    def test_create_project_basic(self):
        """Test basic project creation"""
        manager = ProjectManager()
        
        project_id = manager.create_project("Test Project", "A test project")
        
        assert isinstance(project_id, str)
        assert len(project_id) > 0
        assert project_id in manager.projects
        
        project = manager.projects[project_id]
        assert project["name"] == "Test Project"
        assert project["description"] == "A test project"
        assert project["status"] == "active"
        assert isinstance(project["created_at"], datetime)
        assert project["agents"] == []
        assert project["tasks"] == []
        assert project["config"] == {}
    
    def test_create_project_minimal(self):
        """Test project creation with minimal parameters"""
        manager = ProjectManager()
        
        project_id = manager.create_project("Minimal Project")
        
        assert project_id in manager.projects
        project = manager.projects[project_id]
        assert project["name"] == "Minimal Project"
        assert project["description"] == ""
    
    def test_create_multiple_projects(self):
        """Test creating multiple projects"""
        manager = ProjectManager()
        
        project1_id = manager.create_project("Project 1")
        project2_id = manager.create_project("Project 2")
        project3_id = manager.create_project("Project 3")
        
        assert len(manager.projects) == 3
        assert project1_id != project2_id
        assert project2_id != project3_id
        assert project1_id != project3_id
        
        assert manager.projects[project1_id]["name"] == "Project 1"
        assert manager.projects[project2_id]["name"] == "Project 2"
        assert manager.projects[project3_id]["name"] == "Project 3"
    
    def test_get_project_existing(self):
        """Test getting existing project"""
        manager = ProjectManager()
        
        project_id = manager.create_project("Test Project", "Test description")
        retrieved_project = manager.get_project(project_id)
        
        assert retrieved_project is not None
        assert retrieved_project["id"] == project_id
        assert retrieved_project["name"] == "Test Project"
        assert retrieved_project["description"] == "Test description"
    
    def test_get_project_nonexistent(self):
        """Test getting non-existent project"""
        manager = ProjectManager()
        
        retrieved_project = manager.get_project("nonexistent-id")
        
        assert retrieved_project is None
    
    def test_list_projects_empty(self):
        """Test listing projects when none exist"""
        manager = ProjectManager()
        
        projects = manager.list_projects()
        
        assert isinstance(projects, list)
        assert len(projects) == 0
    
    def test_list_projects_with_data(self):
        """Test listing projects with data"""
        manager = ProjectManager()
        
        # Create multiple projects
        project1_id = manager.create_project("Project 1", "First project")
        project2_id = manager.create_project("Project 2", "Second project")
        project3_id = manager.create_project("Project 3", "Third project")
        
        projects = manager.list_projects()
        
        assert isinstance(projects, list)
        assert len(projects) == 3
        
        # Verify all projects are in the list
        project_ids = [p["id"] for p in projects]
        assert project1_id in project_ids
        assert project2_id in project_ids
        assert project3_id in project_ids
        
        # Verify project data
        for project in projects:
            assert "id" in project
            assert "name" in project
            assert "description" in project
            assert "created_at" in project
            assert "status" in project
    
    def test_delete_project_existing(self):
        """Test deleting existing project"""
        manager = ProjectManager()
        
        project_id = manager.create_project("Test Project")
        
        # Verify project exists
        assert project_id in manager.projects
        
        # Delete project
        result = manager.delete_project(project_id)
        
        assert result is True
        assert project_id not in manager.projects
        assert len(manager.projects) == 0
    
    def test_delete_project_nonexistent(self):
        """Test deleting non-existent project"""
        manager = ProjectManager()
        
        result = manager.delete_project("nonexistent-id")
        
        assert result is False
        assert len(manager.projects) == 0
    
    def test_delete_project_multiple(self):
        """Test deleting projects when multiple exist"""
        manager = ProjectManager()
        
        # Create multiple projects
        project1_id = manager.create_project("Project 1")
        project2_id = manager.create_project("Project 2")
        project3_id = manager.create_project("Project 3")
        
        assert len(manager.projects) == 3
        
        # Delete middle project
        result = manager.delete_project(project2_id)
        
        assert result is True
        assert len(manager.projects) == 2
        assert project1_id in manager.projects
        assert project2_id not in manager.projects
        assert project3_id in manager.projects


class TestProjectManagerEdgeCases:
    """Test project manager edge cases"""
    
    def test_create_project_with_empty_name(self):
        """Test creating project with empty name"""
        manager = ProjectManager()
        
        project_id = manager.create_project("")
        
        assert project_id in manager.projects
        assert manager.projects[project_id]["name"] == ""
    
    def test_create_project_with_unicode_name(self):
        """Test creating project with unicode name"""
        manager = ProjectManager()
        
        unicode_name = "测试项目 🚀 émojis and ñoñ-ASCII"
        project_id = manager.create_project(unicode_name, "Unicode description 测试")
        
        assert project_id in manager.projects
        project = manager.projects[project_id]
        assert project["name"] == unicode_name
        assert project["description"] == "Unicode description 测试"
    
    def test_create_project_with_very_long_name(self):
        """Test creating project with very long name"""
        manager = ProjectManager()
        
        long_name = "Very Long Project Name " * 100
        project_id = manager.create_project(long_name)
        
        assert project_id in manager.projects
        assert manager.projects[project_id]["name"] == long_name
    
    def test_create_project_with_special_characters(self):
        """Test creating project with special characters"""
        manager = ProjectManager()
        
        special_name = "Project!@#$%^&*()_+-=[]{}|;':\",./<>?"
        project_id = manager.create_project(special_name)
        
        assert project_id in manager.projects
        assert manager.projects[project_id]["name"] == special_name
    
    def test_project_id_uniqueness(self):
        """Test that project IDs are unique"""
        manager = ProjectManager()
        
        # Create many projects with the same name
        project_ids = []
        for i in range(100):
            project_id = manager.create_project("Same Name Project")
            project_ids.append(project_id)
        
        # All IDs should be unique
        assert len(set(project_ids)) == 100
        assert len(project_ids) == 100
    
    def test_project_data_integrity(self):
        """Test project data integrity after operations"""
        manager = ProjectManager()
        
        # Create project
        project_id = manager.create_project("Test Project", "Test description")
        original_project = manager.get_project(project_id)
        
        # Modify returned project data (should not affect stored data)
        original_project["name"] = "Modified Name"
        original_project["agents"].append("test_agent")
        
        # Get project again and verify original data is intact
        current_project = manager.get_project(project_id)
        assert current_project["name"] == "Test Project"
        assert current_project["agents"] == []
    
    def test_concurrent_project_operations(self):
        """Test concurrent project operations"""
        import threading
        
        manager = ProjectManager()
        project_ids = []
        errors = []
        
        def create_projects(start_index):
            try:
                for i in range(start_index, start_index + 10):
                    project_id = manager.create_project(f"Project {i}")
                    project_ids.append(project_id)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for i in range(0, 50, 10):
            thread = threading.Thread(target=create_projects, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(errors) == 0  # No errors should occur
        assert len(project_ids) == 50  # All projects should be created
        assert len(set(project_ids)) == 50  # All IDs should be unique
        assert len(manager.projects) == 50  # All projects should be stored


if __name__ == "__main__":
    pytest.main([__file__]) 