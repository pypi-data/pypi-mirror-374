"""
Configuration management for AI Coder
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class AIConfig:
    """AI model configuration"""
    api_url: str = "http://127.0.0.1:11434"
    model: str = "deepseek-r1:8b"
    timeout: int = 120
    max_retries: int = 5
    temperature: float = 0.7
    retry_delay: int = 2
    health_check_timeout: int = 10
    connection_timeout: int = 15


@dataclass
class WorkspaceConfig:
    """Workspace configuration"""
    directory: str = "."
    history_dir: str = ".ai-coder-history"
    max_history_files: int = 100
    auto_save: bool = True
    backup_on_edit: bool = True


@dataclass
class SafetyConfig:
    """Safety and security configuration"""
    allowed_commands: list = None
    blocked_paths: list = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    enable_shell: bool = True
    
    def __post_init__(self):
        if self.allowed_commands is None:
            self.allowed_commands = [
                "python", "python3", "node", "npm", "yarn", "pip", "pip3",
                "pytest", "jest", "mocha", "cargo", "go", "rustc",
                "black", "flake8", "eslint", "prettier", "mypy",
                "git status", "git diff", "git log", "git branch"
            ]
        
        if self.blocked_paths is None:
            self.blocked_paths = [
                "/etc", "/usr", "/var", "/sys", "/proc", "/dev",
                "~/.ssh", "~/.aws", "~/.config"
            ]


@dataclass
class UIConfig:
    """User interface configuration"""
    theme: str = "dark"
    prompt: str = "ai-coder"
    show_file_tree: bool = True
    syntax_highlighting: bool = True
    auto_complete: bool = True
    history_size: int = 1000


@dataclass
class ProjectConfig:
    """Project management configuration"""
    templates_dir: str = "templates"
    default_license: str = "MIT"
    auto_git_init: bool = True
    auto_requirements: bool = True


class Config:
    """Main configuration manager"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or self._default_config_file()
        self.ai = AIConfig()
        self.workspace = WorkspaceConfig()
        self.safety = SafetyConfig()
        self.ui = UIConfig()
        self.project = ProjectConfig()
        
        # Load configuration if file exists
        if os.path.exists(self.config_file):
            self.load()
    
    def _default_config_file(self) -> str:
        """Get default config file path"""
        config_dir = os.path.expanduser("~/.config/ai-coder")
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, "config.yaml")
    
    def load(self) -> None:
        """Load configuration from file"""
        try:
            with open(self.config_file, 'r') as f:
                data = yaml.safe_load(f) or {}
            
            # Update configurations
            if 'ai' in data:
                self.ai = AIConfig(**data['ai'])
            if 'workspace' in data:
                self.workspace = WorkspaceConfig(**data['workspace'])
            if 'safety' in data:
                self.safety = SafetyConfig(**data['safety'])
            if 'ui' in data:
                self.ui = UIConfig(**data['ui'])
            if 'project' in data:
                self.project = ProjectConfig(**data['project'])
                
        except Exception as e:
            print(f"⚠️ Warning: Could not load config from {self.config_file}: {e}")
    
    def save(self) -> None:
        """Save configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            data = {
                'ai': asdict(self.ai),
                'workspace': asdict(self.workspace),
                'safety': asdict(self.safety),
                'ui': asdict(self.ui),
                'project': asdict(self.project)
            }
            
            with open(self.config_file, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, indent=2)
                
        except Exception as e:
            print(f"❌ Error saving config to {self.config_file}: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        try:
            parts = key.split('.')
            obj = self
            
            for part in parts:
                obj = getattr(obj, part)
            
            return obj
        except AttributeError:
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation"""
        try:
            parts = key.split('.')
            obj = self
            
            # Navigate to parent object
            for part in parts[:-1]:
                obj = getattr(obj, part)
            
            # Set the final value
            setattr(obj, parts[-1], value)
            
        except AttributeError as e:
            raise ValueError(f"Invalid config key: {key}") from e
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'ai': asdict(self.ai),
            'workspace': asdict(self.workspace),
            'safety': asdict(self.safety),
            'ui': asdict(self.ui),
            'project': asdict(self.project)
        }
    
    def __str__(self) -> str:
        """String representation of configuration"""
        return yaml.dump(self.to_dict(), default_flow_style=False, indent=2)
