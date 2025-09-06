"""
Project-level operations and management
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from ..utils.logger import get_logger, ActionLogger
from ..core.config import Config
from ..ai.ollama_client import OllamaClient
from .file_manager import FileManager


@dataclass
class ProjectInfo:
    """Project information structure"""
    name: str
    type: str
    description: str
    root_path: str
    files: List[str]
    directories: List[str]
    dependencies: List[str]
    scripts: Dict[str, str]
    metadata: Dict[str, Any]


class ProjectManager:
    """Advanced project management with AI integration"""
    
    def __init__(self, config: Config, file_manager: FileManager, ai_client: OllamaClient):
        self.config = config
        self.file_manager = file_manager
        self.ai_client = ai_client
        self.logger = get_logger(__name__)
        self.action_logger = ActionLogger()
        
        # Project templates
        self.templates = {
            "python": {
                "files": {
                    "main.py": "#!/usr/bin/env python3\n\ndef main():\n    print(\"Hello, World!\")\n\nif __name__ == \"__main__\":\n    main()\n",
                    "requirements.txt": "",
                    "README.md": "# {name}\n\n{description}\n\n## Installation\n\n```bash\npip install -r requirements.txt\n```\n\n## Usage\n\n```bash\npython main.py\n```\n",
                    ".gitignore": "__pycache__/\n*.pyc\n*.pyo\n*.pyd\n.Python\nenv/\nvenv/\n.venv/\n.env\n*.egg-info/\ndist/\nbuild/\n",
                },
                "directories": ["tests", "docs"]
            },
            "javascript": {
                "files": {
                    "index.js": "console.log('Hello, World!');\n",
                    "package.json": "{\n  \"name\": \"{name}\",\n  \"version\": \"1.0.0\",\n  \"description\": \"{description}\",\n  \"main\": \"index.js\",\n  \"scripts\": {\n    \"start\": \"node index.js\",\n    \"test\": \"echo \\\"Error: no test specified\\\" && exit 1\"\n  },\n  \"keywords\": [],\n  \"author\": \"\",\n  \"license\": \"MIT\"\n}\n",
                    "README.md": "# {name}\n\n{description}\n\n## Installation\n\n```bash\nnpm install\n```\n\n## Usage\n\n```bash\nnpm start\n```\n",
                    ".gitignore": "node_modules/\nnpm-debug.log*\nyarn-debug.log*\nyarn-error.log*\n.env\n.env.local\n.env.development.local\n.env.test.local\n.env.production.local\n"
                },
                "directories": ["src", "tests", "docs"]
            }
        }
    
    def create_project(self, project_type: str, name: str, description: str, 
                      use_ai: bool = True) -> bool:
        """Create a new project"""
        try:
            self.logger.info(f"Creating {project_type} project: {name}")
            
            # Create project directory
            project_path = Path(name)
            if project_path.exists():
                self.logger.error(f"Project directory already exists: {name}")
                return False
            
            project_path.mkdir(parents=True)
            
            if use_ai and project_type not in self.templates:
                # Use AI to generate project structure
                return self._create_ai_project(project_type, name, description, str(project_path))
            else:
                # Use template
                return self._create_template_project(project_type, name, description, str(project_path))
                
        except Exception as e:
            self.logger.error(f"Failed to create project {name}: {e}")
            return False
    
    def _create_template_project(self, project_type: str, name: str, 
                                description: str, project_path: str) -> bool:
        """Create project from template"""
        try:
            template = self.templates.get(project_type)
            if not template:
                self.logger.error(f"Unknown project type: {project_type}")
                return False
            
            # Create directories
            for directory in template["directories"]:
                dir_path = os.path.join(project_path, directory.format(name=name))
                os.makedirs(dir_path, exist_ok=True)
            
            # Create files
            for file_path, content in template["files"].items():
                full_path = os.path.join(project_path, file_path)
                formatted_content = content.format(name=name, description=description)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                # Write file
                self.file_manager.write_file(full_path, formatted_content, create_backup=False)
            
            self.logger.info(f"Template project created: {project_path}")
            self.action_logger.log_action("CREATE_PROJECT", {
                "type": project_type,
                "name": name,
                "path": project_path,
                "method": "template"
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create template project: {e}")
            return False
    
    def _create_ai_project(self, project_type: str, name: str, 
                          description: str, project_path: str) -> bool:
        """Create project using AI"""
        try:
            # Build project generation prompt
            prompt = f"""Create a {project_type} project named '{name}' with the following description: {description}

Please generate a complete project structure with all necessary files and content. Return the result as JSON with this structure:
{{
    "files": {{
        "filename1": "file content...",
        "filename2": "file content...",
        ...
    }},
    "directories": ["dir1", "dir2", ...],
    "success": true
}}

Focus on:
- Best practices for {project_type} development
- Complete, functional code
- Proper project structure
- Necessary configuration files
- Clear documentation"""
            
            # Get AI response
            response = self.ai_client.chat(prompt)
            
            if not response.success:
                self.logger.error(f"AI project generation failed: {response.error}")
                return False
            
            # Parse AI response (expecting JSON)
            try:
                project_data = json.loads(response.content)
            except json.JSONDecodeError:
                # Fallback: extract JSON from response
                start = response.content.find('{')
                end = response.content.rfind('}') + 1
                if start != -1 and end != 0:
                    project_data = json.loads(response.content[start:end])
                else:
                    self.logger.error("Could not parse AI response as JSON")
                    return False
            
            # Create directories
            for directory in project_data.get("directories", []):
                dir_path = os.path.join(project_path, directory)
                os.makedirs(dir_path, exist_ok=True)
            
            # Create files
            for file_path, content in project_data.get("files", {}).items():
                full_path = os.path.join(project_path, file_path)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                # Write file
                self.file_manager.write_file(full_path, content, create_backup=False)
            
            # Execute setup commands if provided
            setup_commands = project_data.get("commands", [])
            if setup_commands:
                self._execute_setup_commands(setup_commands, project_path)
            
            self.logger.info(f"AI project created: {project_path}")
            self.action_logger.log_action("CREATE_PROJECT", {
                "type": project_type,
                "name": name,
                "path": project_path,
                "method": "ai"
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create AI project: {e}")
            return False
    
    def _execute_setup_commands(self, commands: List[str], project_path: str) -> None:
        """Execute project setup commands"""
        original_cwd = os.getcwd()
        try:
            os.chdir(project_path)
            
            for command in commands:
                try:
                    self.logger.info(f"Executing setup command: {command}")
                    result = subprocess.run(
                        command, shell=True, capture_output=True, text=True, timeout=60
                    )
                    
                    if result.returncode != 0:
                        self.logger.warning(f"Setup command failed: {command}. Error: {result.stderr}")
                    else:
                        self.logger.debug(f"Setup command succeeded: {command}")
                        
                except subprocess.TimeoutExpired:
                    self.logger.warning(f"Setup command timed out: {command}")
                except Exception as e:
                    self.logger.warning(f"Error executing setup command {command}: {e}")
                    
        finally:
            os.chdir(original_cwd)
    
    def analyze_project(self, project_path: str = ".") -> ProjectInfo:
        """Analyze project structure and generate insights"""
        try:
            project_path = Path(project_path).resolve()
            
            # Gather project information
            files = []
            directories = []
            dependencies = []
            scripts = {}
            
            # Walk through project directory
            for root, dirs, filenames in os.walk(project_path):
                # Skip hidden directories and common ignore patterns
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', '.git']]
                
                rel_root = os.path.relpath(root, project_path)
                if rel_root != '.':
                    directories.append(rel_root)
                
                for filename in filenames:
                    if not filename.startswith('.'):
                        rel_path = os.path.relpath(os.path.join(root, filename), project_path)
                        files.append(rel_path)
            
            # Extract dependencies and scripts
            self._extract_project_metadata(project_path, dependencies, scripts)
            
            # Determine project type
            project_type = self._detect_project_type(files)
            
            project_info = ProjectInfo(
                name=project_path.name,
                type=project_type,
                description="",
                root_path=str(project_path),
                files=files,
                directories=directories,
                dependencies=dependencies,
                scripts=scripts,
                metadata={}
            )
            
            self.logger.info(f"Project analyzed: {len(files)} files, {len(directories)} directories")
            return project_info
            
        except Exception as e:
            self.logger.error(f"Failed to analyze project: {e}")
            return ProjectInfo("", "unknown", "", ".", [], [], [], {}, {})
    
    def _extract_project_metadata(self, project_path: Path, 
                                 dependencies: List[str], scripts: Dict[str, str]) -> None:
        """Extract dependencies and scripts from project files"""
        try:
            # Python projects
            requirements_file = project_path / "requirements.txt"
            if requirements_file.exists():
                content = self.file_manager.read_file(str(requirements_file))
                dependencies.extend(line.strip() for line in content.split('\n') if line.strip())
            
            setup_py = project_path / "setup.py"
            if setup_py.exists():
                scripts["install"] = "pip install -e ."
                scripts["test"] = "python -m pytest"
            
            # JavaScript/Node.js projects
            package_json = project_path / "package.json"
            if package_json.exists():
                try:
                    content = self.file_manager.read_file(str(package_json))
                    data = json.loads(content)
                    
                    # Extract dependencies
                    deps = data.get("dependencies", {})
                    dev_deps = data.get("devDependencies", {})
                    dependencies.extend(list(deps.keys()) + list(dev_deps.keys()))
                    
                    # Extract scripts
                    project_scripts = data.get("scripts", {})
                    scripts.update(project_scripts)
                    
                except json.JSONDecodeError:
                    pass
            
        except Exception as e:
            self.logger.warning(f"Error extracting project metadata: {e}")
    
    def _detect_project_type(self, files: List[str]) -> str:
        """Detect project type based on files"""
        file_set = set(files)
        
        # Check for specific project indicators
        if "package.json" in file_set:
            if any("react" in f.lower() for f in files):
                return "react"
            elif any("vue" in f.lower() for f in files):
                return "vue"
            else:
                return "javascript"
        
        elif "requirements.txt" in file_set or "setup.py" in file_set or "pyproject.toml" in file_set:
            return "python"
        
        elif "Cargo.toml" in file_set:
            return "rust"
        
        elif "go.mod" in file_set:
            return "go"
        
        else:
            # Detect by file extensions
            extensions = set()
            for f in files:
                ext = Path(f).suffix.lower()
                if ext:
                    extensions.add(ext)
            
            if ".py" in extensions:
                return "python"
            elif ".js" in extensions or ".ts" in extensions:
                return "javascript"
            elif ".rs" in extensions:
                return "rust"
            elif ".go" in extensions:
                return "go"
            else:
                return "unknown"
