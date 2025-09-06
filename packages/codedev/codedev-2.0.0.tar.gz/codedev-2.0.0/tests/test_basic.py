"""
Basic tests for AI Coder components
"""

import unittest
import tempfile
import os
from pathlib import Path

from ai_coder.core.config import Config
from ai_coder.operations.file_manager import FileManager


class TestConfig(unittest.TestCase):
    """Test configuration management"""
    
    def test_default_config(self):
        """Test default configuration creation"""
        config = Config()
        
        # Test default values
        self.assertEqual(config.ai.model, "deepseek-r1:8b")
        self.assertEqual(config.ai.api_url, "http://127.0.0.1:11434/api/generate")
        self.assertTrue(config.workspace.auto_save)
        self.assertTrue(config.safety.enable_shell)
    
    def test_config_get_set(self):
        """Test configuration get/set"""
        config = Config()
        
        # Test get
        self.assertEqual(config.get('ai.model'), config.ai.model)
        
        # Test set
        config.set('ai.model', 'test-model')
        self.assertEqual(config.ai.model, 'test-model')


class TestFileManager(unittest.TestCase):
    """Test file manager functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = Config()
        self.config.workspace.history_dir = os.path.join(self.temp_dir, '.history')
        self.file_manager = FileManager(self.config)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_write_read_file(self):
        """Test file write and read operations"""
        file_path = os.path.join(self.temp_dir, 'test.txt')
        content = "Hello, World!"
        
        # Write file
        success = self.file_manager.write_file(file_path, content, create_backup=False)
        self.assertTrue(success)
        
        # Read file
        read_content = self.file_manager.read_file(file_path)
        self.assertEqual(read_content, content)
    
    def test_file_history(self):
        """Test file history functionality"""
        file_path = os.path.join(self.temp_dir, 'test.txt')
        
        # Create initial file
        self.file_manager.write_file(file_path, "Version 1", create_backup=False)
        
        # Update file (this should create backup)
        self.file_manager.write_file(file_path, "Version 2")
        
        # Check history
        history = self.file_manager.get_file_history(file_path)
        self.assertEqual(len(history), 1)  # One backup created
    
    def test_undo_redo(self):
        """Test undo/redo functionality"""
        file_path = os.path.join(self.temp_dir, 'test.txt')
        
        # Create initial file
        self.file_manager.write_file(file_path, "Version 1", create_backup=False)
        
        # Update file
        self.file_manager.write_file(file_path, "Version 2")
        
        # Update again
        self.file_manager.write_file(file_path, "Version 3")
        
        # Undo should go back to Version 2
        success = self.file_manager.undo_last_change(file_path)
        self.assertTrue(success)
        
        content = self.file_manager.read_file(file_path)
        self.assertEqual(content, "Version 2")
        
        # Redo should go back to Version 3
        success = self.file_manager.redo_last_undo(file_path)
        self.assertTrue(success)
        
        content = self.file_manager.read_file(file_path)
        self.assertEqual(content, "Version 3")


if __name__ == '__main__':
    unittest.main()
