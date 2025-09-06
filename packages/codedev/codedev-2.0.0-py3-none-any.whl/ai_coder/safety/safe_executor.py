"""
Safe command execution with whitelisting and security controls
"""

import os
import subprocess
import shlex
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from ..utils.logger import get_logger, ActionLogger
from ..core.config import Config


@dataclass
class CommandResult:
    """Command execution result"""
    success: bool
    stdout: str
    stderr: str
    return_code: int
    execution_time: float


class SafeCommandExecutor:
    """Safe command executor with whitelisting and sandboxing"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = get_logger(__name__)
        self.action_logger = ActionLogger()
        
        # Command patterns that are always allowed
        self.safe_patterns = [
            # Language runtimes
            r'^python3?\s',
            r'^node\s',
            r'^npm\s',
            r'^yarn\s',
            r'^pip3?\s',
            r'^cargo\s',
            r'^go\s',
            r'^rustc\s',
            
            # Development tools
            r'^pytest\s',
            r'^jest\s',
            r'^mocha\s',
            r'^black\s',
            r'^flake8\s',
            r'^eslint\s',
            r'^prettier\s',
            r'^mypy\s',
            
            # Git commands (read-only)
            r'^git\s+(status|diff|log|branch|show)\s*',
            
            # File operations (limited)
            r'^ls\s',
            r'^cat\s',
            r'^head\s',
            r'^tail\s',
            r'^grep\s',
            r'^find\s',
            r'^wc\s',
        ]
        
        # Commands that require special handling
        self.special_commands = {
            'test': self._handle_test_command,
            'lint': self._handle_lint_command,
            'format': self._handle_format_command,
            'build': self._handle_build_command,
            'install': self._handle_install_command,
        }
    
    def execute(self, command: str, cwd: Optional[str] = None, 
                timeout: int = 30) -> CommandResult:
        """Execute command safely"""
        start_time = time.time()
        
        try:
            # Validate command
            if not self._is_command_safe(command):
                error_msg = f"Command not allowed: {command}"
                self.logger.warning(error_msg)
                self.action_logger.log_command_execution(command, False, error_msg)
                return CommandResult(False, "", error_msg, -1, 0.0)
            
            # Check if it's a special command
            cmd_parts = shlex.split(command)
            if cmd_parts and cmd_parts[0] in self.special_commands:
                return self.special_commands[cmd_parts[0]](cmd_parts[1:], cwd, timeout)
            
            # Execute regular command
            result = self._execute_command(command, cwd, timeout)
            
            execution_time = time.time() - start_time
            result.execution_time = execution_time
            
            self.action_logger.log_command_execution(
                command, result.success, f"stdout: {len(result.stdout)}, stderr: {len(result.stderr)}"
            )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Command execution failed: {e}"
            self.logger.error(error_msg)
            self.action_logger.log_command_execution(command, False, error_msg)
            
            return CommandResult(False, "", error_msg, -1, execution_time)
    
    def _is_command_safe(self, command: str) -> bool:
        """Check if command is safe to execute"""
        if not self.config.safety.enable_shell:
            return False
        
        # Check whitelist
        allowed_commands = self.config.safety.allowed_commands
        
        # Check if command starts with any allowed pattern
        cmd_lower = command.lower().strip()
        
        for allowed in allowed_commands:
            if cmd_lower.startswith(allowed.lower()):
                return True
        
        # Check against regex patterns
        import re
        for pattern in self.safe_patterns:
            if re.match(pattern, cmd_lower):
                return True
        
        # Check if it's a special command
        cmd_parts = shlex.split(command)
        if cmd_parts and cmd_parts[0] in self.special_commands:
            return True
        
        return False
    
    def _execute_command(self, command: str, cwd: Optional[str], 
                        timeout: int) -> CommandResult:
        """Execute command with security controls"""
        try:
            # Set working directory
            if cwd and not self._is_path_safe(cwd):
                raise ValueError(f"Unsafe working directory: {cwd}")
            
            # Execute command
            process = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=self._get_safe_environment()
            )
            
            return CommandResult(
                success=process.returncode == 0,
                stdout=process.stdout,
                stderr=process.stderr,
                return_code=process.returncode,
                execution_time=0.0  # Will be set by caller
            )
            
        except subprocess.TimeoutExpired:
            return CommandResult(
                success=False,
                stdout="",
                stderr=f"Command timed out after {timeout} seconds",
                return_code=-1,
                execution_time=0.0
            )
        except Exception as e:
            return CommandResult(
                success=False,
                stdout="",
                stderr=str(e),
                return_code=-1,
                execution_time=0.0
            )
    
    def _is_path_safe(self, path: str) -> bool:
        """Check if path is safe for operations"""
        try:
            resolved_path = Path(path).resolve()
            
            # Check against blocked paths
            for blocked in self.config.safety.blocked_paths:
                blocked_resolved = Path(blocked).expanduser().resolve()
                try:
                    resolved_path.relative_to(blocked_resolved)
                    return False  # Path is within blocked directory
                except ValueError:
                    continue  # Path is not within blocked directory
            
            return True
            
        except Exception:
            return False
    
    def _get_safe_environment(self) -> Dict[str, str]:
        """Get safe environment variables for command execution"""
        # Start with minimal environment
        safe_env = {
            'PATH': os.environ.get('PATH', ''),
            'HOME': os.environ.get('HOME', ''),
            'USER': os.environ.get('USER', ''),
            'LANG': os.environ.get('LANG', 'en_US.UTF-8'),
            'LC_ALL': os.environ.get('LC_ALL', 'en_US.UTF-8'),
        }
        
        # Add language-specific environment variables
        for key, value in os.environ.items():
            if any(key.startswith(prefix) for prefix in ['PYTHON', 'NODE', 'NPM', 'CARGO', 'RUST']):
                safe_env[key] = value
        
        return safe_env
    
    def _handle_test_command(self, args: List[str], cwd: Optional[str], 
                           timeout: int) -> CommandResult:
        """Handle test command"""
        if not args:
            return CommandResult(False, "", "No test framework specified", -1, 0.0)
        
        framework = args[0]
        test_args = args[1:]
        
        # Map framework to actual command
        framework_commands = {
            'pytest': ['python', '-m', 'pytest'] + test_args,
            'jest': ['npm', 'test'] + test_args,
            'mocha': ['npm', 'run', 'test'] + test_args,
            'cargo': ['cargo', 'test'] + test_args,
            'go': ['go', 'test'] + test_args,
        }
        
        if framework not in framework_commands:
            return CommandResult(False, "", f"Unknown test framework: {framework}", -1, 0.0)
        
        command = ' '.join(framework_commands[framework])
        return self._execute_command(command, cwd, timeout)
    
    def _handle_lint_command(self, args: List[str], cwd: Optional[str], 
                           timeout: int) -> CommandResult:
        """Handle lint command"""
        if not args:
            return CommandResult(False, "", "No file specified for linting", -1, 0.0)
        
        file_path = args[0]
        
        # Detect linter based on file extension
        ext = Path(file_path).suffix.lower()
        
        if ext == '.py':
            command = f"flake8 {file_path}"
        elif ext in ['.js', '.ts', '.jsx', '.tsx']:
            command = f"eslint {file_path}"
        elif ext == '.rs':
            command = f"cargo clippy -- {file_path}"
        else:
            return CommandResult(False, "", f"No linter available for {ext} files", -1, 0.0)
        
        return self._execute_command(command, cwd, timeout)
    
    def _handle_format_command(self, args: List[str], cwd: Optional[str], 
                             timeout: int) -> CommandResult:
        """Handle format command"""
        if not args:
            return CommandResult(False, "", "No file specified for formatting", -1, 0.0)
        
        file_path = args[0]
        
        # Detect formatter based on file extension
        ext = Path(file_path).suffix.lower()
        
        if ext == '.py':
            command = f"black {file_path}"
        elif ext in ['.js', '.ts', '.jsx', '.tsx']:
            command = f"prettier --write {file_path}"
        elif ext == '.rs':
            command = f"cargo fmt -- {file_path}"
        else:
            return CommandResult(False, "", f"No formatter available for {ext} files", -1, 0.0)
        
        return self._execute_command(command, cwd, timeout)
    
    def _handle_build_command(self, args: List[str], cwd: Optional[str], 
                            timeout: int) -> CommandResult:
        """Handle build command"""
        # Detect project type and use appropriate build command
        if Path("package.json").exists():
            command = "npm run build"
        elif Path("Cargo.toml").exists():
            command = "cargo build"
        elif Path("go.mod").exists():
            command = "go build"
        elif Path("setup.py").exists():
            command = "python setup.py build"
        else:
            return CommandResult(False, "", "No build system detected", -1, 0.0)
        
        return self._execute_command(command, cwd, timeout)
    
    def _handle_install_command(self, args: List[str], cwd: Optional[str], 
                              timeout: int) -> CommandResult:
        """Handle install command"""
        if not args:
            # Auto-detect and install dependencies
            if Path("package.json").exists():
                command = "npm install"
            elif Path("requirements.txt").exists():
                command = "pip install -r requirements.txt"
            elif Path("Cargo.toml").exists():
                command = "cargo build"  # Cargo automatically downloads dependencies
            else:
                return CommandResult(False, "", "No dependency file found", -1, 0.0)
        else:
            # Install specific package
            package = args[0]
            
            # Detect package manager
            if Path("package.json").exists():
                command = f"npm install {package}"
            elif any(Path(f).exists() for f in ["requirements.txt", "setup.py"]):
                command = f"pip install {package}"
            else:
                return CommandResult(False, "", "Cannot determine package manager", -1, 0.0)
        
        return self._execute_command(command, cwd, timeout)


# Add missing import
import time
