"""
Main CLI interface for AI Coder
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
import shlex

from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.syntax import Syntax
from rich.panel import Panel

from .core.config import Config
from .utils.logger import get_logger, ActionLogger
from .utils.ollama_installer import OllamaInstaller
from .ai.ollama_client import OllamaClient
from .operations.file_manager import FileManager
from .operations.project_manager import ProjectManager
from .safety.safe_executor import SafeCommandExecutor


class AiCoderCLI:
    """Advanced AI Coder CLI with rich interface"""
    
    def __init__(self, config: Config):
        self.config = config
        self.console = Console()
        self.logger = get_logger(__name__)
        self.action_logger = ActionLogger()
        
        # Initialize Ollama installer
        self.ollama_installer = OllamaInstaller()
        
        # Initialize components (will be set up after Ollama check)
        self.ai_client = None
        self.file_manager = FileManager(config)
        self.project_manager = None
        self.safe_executor = SafeCommandExecutor(config)
        
        # CLI state
        self.history = InMemoryHistory()
        self.current_directory = Path.cwd()
        self.ollama_ready = False
        
        # Command completions
        self.commands = [
            # File operations
            'create', 'edit', 'refactor', 'show', 'delete', 'move', 'copy',
            # Project operations
            'create-project', 'analyze-project', 'refactor-project',
            # Directory operations
            'ls', 'tree', 'mkdir', 'rmdir', 'cd', 'pwd',
            # History operations
            'undo', 'redo', 'history', 'restore',
            # Command execution
            'run', 'test', 'lint', 'format', 'build', 'install',
            # AI and Configuration
            'model', 'models', 'config', 'config-show',
            # Other
            'help', 'exit', 'quit', 'clear'
        ]
        
        self.completer = WordCompleter(self.commands, ignore_case=True)
    
    def initialize_system(self) -> bool:
        """Initialize and check system requirements"""
        self.console.print("\n[bold blue]🚀 Initializing AI Coder...[/bold blue]")
        
        # Check Ollama installation and setup
        success, message, setup_log = self.ollama_installer.setup_ollama()
        
        # Display setup log
        for log_entry in setup_log:
            self.console.print(f"  {log_entry}")
        
        if not success:
            self.console.print(f"\n[red]❌ Ollama Setup Failed: {message}[/red]")
            
            # Show installation instructions
            instructions = self.ollama_installer.get_installation_instructions()
            self.console.print(Panel(instructions, title="Installation Instructions"))
            
            # Ask user if they want to continue anyway
            try:
                continue_anyway = input("\nDo you want to continue without AI features? (y/N): ")
                return continue_anyway.lower().startswith('y')
            except KeyboardInterrupt:
                return False
        
        # Initialize AI client
        self.ai_client = OllamaClient(self.config)
        
        # Check for available models
        models = self.ai_client.get_available_models()
        if not models:
            self.console.print("\n[yellow]⚠️ No models found. Installing recommended model...[/yellow]")
            
            # Try to install a good coding model
            recommended_models = ['deepseek-r1:8b', 'deepseek-coder:6.7b', 'qwen2.5-coder:7b']
            model_installed = False
            
            for model in recommended_models:
                self.console.print(f"🔄 Trying to install {model}...")
                if self.ai_client.install_model(model):
                    self.config.ai.model = model
                    self.config.save()
                    model_installed = True
                    break
            
            if not model_installed:
                self.console.print("[red]❌ Failed to install any recommended models[/red]")
                return False
        else:
            # Select best available model
            best_model = self.ai_client.select_best_model()
            if best_model and best_model != self.config.ai.model:
                self.console.print(f"🎯 Auto-selected model: [green]{best_model}[/green]")
                self.config.ai.model = best_model
                self.config.save()
        
        # Test AI connection
        self.console.print("🔍 Testing AI connection...")
        if self.ai_client.health_check():
            self.console.print("[green]✅ AI connection successful[/green]")
            self.ollama_ready = True
        else:
            self.console.print("[red]❌ AI connection failed[/red]")
            return False
        
        # Initialize project manager (needs AI client)
        self.project_manager = ProjectManager(self.config, self.file_manager, self.ai_client)
        
        self.console.print("[green]✅ System initialization complete[/green]\n")
        return True
    
    def run(self) -> None:
        """Run the main CLI loop"""
        # Initialize system first
        if not self.initialize_system():
            self.console.print("[red]❌ System initialization failed. Exiting...[/red]")
            return
        
        self._show_welcome()
        
        while True:
            try:
                # Show current directory in prompt
                prompt_text = f"[bold cyan]{self.config.ui.prompt}[/bold cyan] {self.current_directory.name}> "
                
                # Get user input
                user_input = prompt(
                    prompt_text,
                    history=self.history,
                    auto_suggest=AutoSuggestFromHistory(),
                    completer=self.completer if self.config.ui.auto_complete else None
                ).strip()
                
                if not user_input:
                    continue
                
                # Parse and execute command
                self._execute_command(user_input)
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Use 'exit' or 'quit' to exit[/yellow]")
                continue
            except EOFError:
                break
        
        self.console.print("\n[green]👋 Goodbye![/green]")
    
    def _show_welcome(self) -> None:
        """Show welcome message"""
        # Get model and system info
        model_name = self.config.ai.model
        system_info = f"{self.ollama_installer.system.title()}"
        models_count = len(self.ai_client.get_available_models()) if self.ai_client else 0
        
        self.console.print()
        self.console.print(Panel.fit(
            "[bold green]🤖 AI Coder - Advanced CLI REPL Agent[/bold green]\n"
            f"[cyan]Model: {model_name}[/cyan] | [dim]System: {system_info}[/dim] | [dim]Available Models: {models_count}[/dim]\n"
            f"[dim]Working directory: {self.current_directory}[/dim]\n\n"
            "[yellow]💬 Talk naturally! Try:[/yellow]\n"
            "[dim]• 'create a web server'[/dim]\n"
            "[dim]• 'fix @app.py'[/dim]\n"
            "[dim]• 'show my files'[/dim]\n"
            "[dim]• '# todo add authentication'[/dim]\n"
            "[dim]• 'help' for all commands[/dim]\n"
            "[dim]• 'models' to see available AI models[/dim]",
            border_style="green"
        ))
        self.console.print()
    
    def _execute_command(self, user_input: str) -> None:
        """Execute user command - supports both structured and natural language"""
        try:
            # First check if it's a natural language command
            if self._handle_natural_language(user_input):
                return
            
            # Parse structured command
            parts = shlex.split(user_input)
            if not parts:
                return
            
            command = parts[0].lower()
            args = parts[1:]
            
            # Route to appropriate handler
            if command in ['exit', 'quit']:
                sys.exit(0)
            elif command == 'help':
                self._show_help()
            elif command == 'clear':
                os.system('clear' if os.name == 'posix' else 'cls')
            elif command == 'create':
                self._handle_create(args)
            elif command == 'edit':
                self._handle_edit(args)
            elif command == 'refactor':
                self._handle_refactor(args)
            elif command == 'show':
                self._handle_show(args)
            elif command == 'delete':
                self._handle_delete(args)
            elif command == 'move':
                self._handle_move(args)
            elif command == 'copy':
                self._handle_copy(args)
            elif command == 'create-project':
                self._handle_create_project(args)
            elif command == 'analyze-project':
                self._handle_analyze_project(args)
            elif command == 'refactor-project':
                self._handle_refactor_project(args)
            elif command == 'ls':
                self._handle_ls(args)
            elif command == 'tree':
                self._handle_tree(args)
            elif command == 'mkdir':
                self._handle_mkdir(args)
            elif command == 'rmdir':
                self._handle_rmdir(args)
            elif command == 'cd':
                self._handle_cd(args)
            elif command == 'pwd':
                self._handle_pwd()
            elif command == 'undo':
                self._handle_undo(args)
            elif command == 'redo':
                self._handle_redo(args)
            elif command == 'history':
                self._handle_history(args)
            elif command == 'restore':
                self._handle_restore(args)
            elif command == 'run':
                self._handle_run(args)
            elif command in ['test', 'lint', 'format', 'build', 'install']:
                self._handle_safe_command(command, args)
            elif command == 'model':
                self._handle_model(args)
            elif command == 'models':
                self._handle_models()
            elif command == 'config':
                self._handle_config(args)
            elif command == 'config-show':
                self._handle_config_show()
            else:
                # Try natural language as fallback
                if not self._handle_natural_language_fallback(user_input):
                    self.console.print(f"[yellow]🤔 I'm not sure what you mean by '{user_input}'[/yellow]")
                    self.console.print("[dim]Try commands like: 'create a web server', 'fix @app.py', 'help'[/dim]")
        
        except Exception as e:
            self.logger.error(f"Command execution failed: {e}")
            self.console.print(f"[red]❌ Error: {e}[/red]")
    
    def _show_help(self) -> None:
        """Show help information"""
        help_table = Table(title="AI Coder Commands")
        help_table.add_column("Command", style="cyan", no_wrap=True)
        help_table.add_column("Description", style="white")
        help_table.add_column("Example", style="dim")
        
        commands = [
            ("🗣️ Natural Language", "", ""),
            ("'create a web server'", "Create files naturally", "'make a React app'"),
            ("'fix @app.py'", "Fix specific file", "'update @server.js add cors'"),
            ("'show my files'", "List/show files", "'display @config.py'"),
            ("'# todo add auth'", "Add notes/todos", "'# reminder: test this'"),
            ("'hi' / 'thanks'", "Casual conversation", "'what files do I have?'"),
            ("", "", ""),
            ("📋 Structured Commands", "", ""),
            ("create <file> <lang> <prompt>", "Create new file with AI", "create app.py python 'web server with Flask'"),
            ("edit <file> <lang> <prompt>", "Edit existing file", "edit app.py python 'add error handling'"),
            ("refactor <file> <lang> <prompt>", "Refactor code", "refactor app.py python 'use classes'"),
            ("show <file>", "Display file contents", "show app.py"),
            ("delete <file>", "Delete file (with backup)", "delete old_file.py"),
            ("move <src> <dest>", "Move/rename file", "move old.py new.py"),
            ("copy <src> <dest>", "Copy file", "copy template.py app.py"),
            ("", "", ""),
            ("Project Operations", "", ""),
            ("create-project <type> <name> <desc>", "Generate full project", "create-project python myapp 'REST API'"),
            ("analyze-project", "Show project structure", "analyze-project"),
            ("refactor-project <instructions>", "Cross-file refactoring", "refactor-project 'add type hints'"),
            ("", "", ""),
            ("Directory Operations", "", ""),
            ("ls [path]", "List files/directories", "ls src/"),
            ("tree [depth]", "Show directory tree", "tree 2"),
            ("mkdir <path>", "Create directory", "mkdir src/components"),
            ("cd <path>", "Change directory", "cd src/"),
            ("pwd", "Show current directory", "pwd"),
            ("", "", ""),
            ("History & Undo", "", ""),
            ("undo <file>", "Undo last change", "undo app.py"),
            ("redo <file>", "Redo last undo", "redo app.py"),
            ("history <file>", "Show file history", "history app.py"),
            ("restore <file> <timestamp>", "Restore to version", "restore app.py 20240905_143022"),
            ("", "", ""),
            ("Safe Commands", "", ""),
            ("run <command>", "Execute safe command", "run python app.py"),
            ("test <framework>", "Run tests", "test pytest"),
            ("lint <file>", "Run linter", "lint app.py"),
            ("format <file>", "Format code", "format app.py"),
            ("build", "Build project", "build"),
            ("install [package]", "Install dependencies", "install requests"),
            ("", "", ""),
            ("Configuration", "", ""),
            ("model <name>", "Switch AI model", "model llama2"),
            ("models", "Show available AI models", "models"),
            ("config <key> <value>", "Set configuration", "config ai.temperature 0.8"),
            ("config-show", "Show configuration", "config-show"),
            ("", "", ""),
            ("Other", "", ""),
            ("help", "Show this help", "help"),
            ("clear", "Clear screen", "clear"),
            ("exit / quit", "Exit application", "exit"),
        ]
        
        for cmd, desc, example in commands:
            if not desc:  # Section header
                help_table.add_row(f"[bold yellow]{cmd}[/bold yellow]", "", "")
            else:
                help_table.add_row(cmd, desc, example)
        
        self.console.print(help_table)
    
    def _handle_create(self, args: List[str]) -> None:
        """Handle create command"""
        if len(args) < 3:
            self.console.print("[red]❌ Usage: create <file> <language> <description>[/red]")
            return
        
        file_path = args[0]
        language = args[1]
        description = ' '.join(args[2:])
        
        if os.path.exists(file_path):
            self.console.print(f"[red]❌ File already exists: {file_path}[/red]")
            self.console.print("[yellow]Use 'edit' to modify existing files[/yellow]")
            return
        
        self.console.print(f"[cyan]🤖 Creating {language} file: {file_path}[/cyan]")
        
        # Build prompt
        system_prompt, user_prompt = self.prompt_builder.build_create_prompt(
            language, description
        )
        
        # Get AI response
        with self.console.status("Generating code..."):
            response = self.ai_client.generate(user_prompt, system_prompt=system_prompt)
        
        if not response.success:
            self.console.print(f"[red]❌ AI generation failed: {response.error}[/red]")
            return
        
        # Clean response (remove markdown if present)
        content = response.content.strip()
        if content.startswith('```'):
            lines = content.split('\n')
            if len(lines) > 2:
                content = '\n'.join(lines[1:-1])
        
        # Write file
        success = self.file_manager.write_file(file_path, content)
        
        if success:
            self.console.print(f"[green]✅ Created: {file_path}[/green]")
            if self.config.ui.syntax_highlighting:
                self._show_file_with_syntax(file_path, content)
        else:
            self.console.print(f"[red]❌ Failed to create file: {file_path}[/red]")
    
    def _handle_edit(self, args: List[str]) -> None:
        """Handle edit command"""
        if len(args) < 3:
            self.console.print("[red]❌ Usage: edit <file> <language> <changes>[/red]")
            return
        
        file_path = args[0]
        language = args[1]
        changes = ' '.join(args[2:])
        
        if not os.path.exists(file_path):
            self.console.print(f"[red]❌ File not found: {file_path}[/red]")
            self.console.print("[yellow]Use 'create' to create new files[/yellow]")
            return
        
        # Read current content
        current_content = self.file_manager.read_file(file_path)
        if not current_content:
            self.console.print(f"[red]❌ Could not read file: {file_path}[/red]")
            return
        
        self.console.print(f"[cyan]🤖 Editing {language} file: {file_path}[/cyan]")
        
        # Build prompt
        system_prompt, user_prompt = self.prompt_builder.build_edit_prompt(
            language, current_content, changes
        )
        
        # Get AI response
        with self.console.status("Generating changes..."):
            response = self.ai_client.generate(user_prompt, system_prompt=system_prompt)
        
        if not response.success:
            self.console.print(f"[red]❌ AI editing failed: {response.error}[/red]")
            return
        
        # Clean response
        content = response.content.strip()
        if content.startswith('```'):
            lines = content.split('\n')
            if len(lines) > 2:
                content = '\n'.join(lines[1:-1])
        
        # Write file
        success = self.file_manager.write_file(file_path, content)
        
        if success:
            self.console.print(f"[green]✅ Updated: {file_path}[/green]")
        else:
            self.console.print(f"[red]❌ Failed to update file: {file_path}[/red]")
    
    def _handle_refactor(self, args: List[str]) -> None:
        """Handle refactor command"""
        if len(args) < 3:
            self.console.print("[red]❌ Usage: refactor <file> <language> <instructions>[/red]")
            return
        
        file_path = args[0]
        language = args[1]
        instructions = ' '.join(args[2:])
        
        if not os.path.exists(file_path):
            self.console.print(f"[red]❌ File not found: {file_path}[/red]")
            return
        
        # Read current content
        current_content = self.file_manager.read_file(file_path)
        if not current_content:
            self.console.print(f"[red]❌ Could not read file: {file_path}[/red]")
            return
        
        self.console.print(f"[cyan]🤖 Refactoring {language} file: {file_path}[/cyan]")
        
        # Build prompt
        system_prompt, user_prompt = self.prompt_builder.build_refactor_prompt(
            language, current_content, instructions
        )
        
        # Get AI response
        with self.console.status("Refactoring code..."):
            response = self.ai_client.generate(user_prompt, system_prompt=system_prompt)
        
        if not response.success:
            self.console.print(f"[red]❌ AI refactoring failed: {response.error}[/red]")
            return
        
        # Clean response
        content = response.content.strip()
        if content.startswith('```'):
            lines = content.split('\n')
            if len(lines) > 2:
                content = '\n'.join(lines[1:-1])
        
        # Write file
        success = self.file_manager.write_file(file_path, content)
        
        if success:
            self.console.print(f"[green]✅ Refactored: {file_path}[/green]")
        else:
            self.console.print(f"[red]❌ Failed to refactor file: {file_path}[/red]")
    
    def _handle_show(self, args: List[str]) -> None:
        """Handle show command"""
        if not args:
            self.console.print("[red]❌ Usage: show <file>[/red]")
            return
        
        file_path = args[0]
        
        if not os.path.exists(file_path):
            self.console.print(f"[red]❌ File not found: {file_path}[/red]")
            return
        
        content = self.file_manager.read_file(file_path)
        
        if content:
            self._show_file_with_syntax(file_path, content)
        else:
            self.console.print(f"[red]❌ Could not read file: {file_path}[/red]")
    
    def _show_file_with_syntax(self, file_path: str, content: str) -> None:
        """Show file with syntax highlighting"""
        if self.config.ui.syntax_highlighting:
            # Detect language from extension
            ext = Path(file_path).suffix.lower()
            language_map = {
                '.py': 'python',
                '.js': 'javascript',
                '.ts': 'typescript',
                '.jsx': 'javascript',
                '.tsx': 'typescript',
                '.html': 'html',
                '.css': 'css',
                '.json': 'json',
                '.yaml': 'yaml',
                '.yml': 'yaml',
                '.md': 'markdown',
                '.rs': 'rust',
                '.go': 'go',
                '.java': 'java',
                '.cpp': 'cpp',
                '.c': 'c',
                '.sh': 'bash',
            }
            
            language = language_map.get(ext, 'text')
            
            syntax = Syntax(content, language, theme="monokai", line_numbers=True)
            self.console.print(Panel(syntax, title=file_path, border_style="blue"))
        else:
            self.console.print(Panel(content, title=file_path, border_style="blue"))
    
    def _handle_ls(self, args: List[str]) -> None:
        """Handle ls command"""
        path = args[0] if args else "."
        
        try:
            path_obj = Path(path)
            if not path_obj.exists():
                self.console.print(f"[red]❌ Path not found: {path}[/red]")
                return
            
            if path_obj.is_file():
                self.console.print(f"[blue]{path}[/blue] (file)")
                return
            
            # List directory contents
            items = []
            for item in sorted(path_obj.iterdir()):
                if item.is_dir():
                    items.append(f"[blue]{item.name}/[/blue]")
                else:
                    items.append(item.name)
            
            if items:
                self.console.print(f"\n[bold]Contents of {path}:[/bold]")
                for item in items:
                    self.console.print(f"  {item}")
            else:
                self.console.print(f"[dim]Directory {path} is empty[/dim]")
        
        except Exception as e:
            self.console.print(f"[red]❌ Error listing directory: {e}[/red]")
    
    def _handle_pwd(self) -> None:
        """Handle pwd command"""
        self.console.print(f"[cyan]{self.current_directory}[/cyan]")
    
    def _handle_cd(self, args: List[str]) -> None:
        """Handle cd command"""
        if not args:
            self.console.print("[red]❌ Usage: cd <path>[/red]")
            return
        
        path = args[0]
        
        try:
            new_path = Path(path).resolve()
            
            if not new_path.exists():
                self.console.print(f"[red]❌ Path not found: {path}[/red]")
                return
            
            if not new_path.is_dir():
                self.console.print(f"[red]❌ Not a directory: {path}[/red]")
                return
            
            self.current_directory = new_path
            os.chdir(new_path)
            self.console.print(f"[green]📂 {new_path}[/green]")
        
        except Exception as e:
            self.console.print(f"[red]❌ Error changing directory: {e}[/red]")
    
    def _handle_run(self, args: List[str]) -> None:
        """Handle run command"""
        if not args:
            self.console.print("[red]❌ Usage: run <command>[/red]")
            return
        
        command = ' '.join(args)
        
        self.console.print(f"[cyan]🔧 Executing: {command}[/cyan]")
        
        with self.console.status("Running command..."):
            result = self.safe_executor.execute(command, str(self.current_directory))
        
        if result.success:
            self.console.print(f"[green]✅ Command completed[/green]")
            if result.stdout:
                self.console.print(Panel(result.stdout, title="Output", border_style="green"))
        else:
            self.console.print(f"[red]❌ Command failed[/red]")
            if result.stderr:
                self.console.print(Panel(result.stderr, title="Error", border_style="red"))
    
    def _handle_model(self, args: List[str]) -> None:
        """Handle model command"""
        if not args:
            # Show current model
            self.console.print(f"[cyan]Current model: {self.config.ai.model}[/cyan]")
            
            # List available models
            models = self.ai_client.get_available_models() if self.ai_client else []
            if models:
                self.console.print("\n[bold]Available models:[/bold]")
                for model in models:
                    marker = "→" if model['name'] == self.config.ai.model else " "
                    size_mb = model.get('size', 0) // (1024*1024)
                    self.console.print(f"  {marker} {model['name']} [dim]({size_mb}MB)[/dim]")
            return
        
        new_model = args[0]
        
        # Test model
        self.console.print(f"[cyan]Testing model: {new_model}[/cyan]")
        
        old_model = self.config.ai.model
        self.config.ai.model = new_model
        
        if self.ai_client and self.ai_client.health_check():
            self.console.print(f"[green]✅ Switched to model: {new_model}[/green]")
            self.config.save()
        else:
            self.config.ai.model = old_model
            self.console.print(f"[red]❌ Model not available: {new_model}[/red]")
    
    def _handle_models(self) -> None:
        """Handle models command - show detailed model information"""
        if not self.ai_client:
            self.console.print("[red]❌ AI client not available[/red]")
            return
        
        models = self.ai_client.get_available_models()
        
        if not models:
            self.console.print("[yellow]⚠️ No models available[/yellow]")
            self.console.print("\n[dim]Recommended models to install:[/dim]")
            recommended = ['deepseek-r1:8b', 'deepseek-coder:6.7b', 'qwen2.5-coder:7b', 'llama3.2:8b']
            for model in recommended:
                self.console.print(f"  • {model}")
            self.console.print(f"\n[dim]Install with: ollama pull <model_name>[/dim]")
            return
        
        # Create models table
        table = Table(title="🤖 Available AI Models")
        table.add_column("Model", style="cyan", no_wrap=True)
        table.add_column("Size", style="green", justify="right")
        table.add_column("Modified", style="dim")
        table.add_column("Status", style="bold")
        
        for model in models:
            # Format size
            size_bytes = model.get('size', 0)
            if size_bytes > 1024*1024*1024:
                size_str = f"{size_bytes / (1024*1024*1024):.1f}GB"
            else:
                size_str = f"{size_bytes / (1024*1024):.0f}MB"
            
            # Format date
            modified = model.get('modified_at', 'Unknown')
            if 'T' in str(modified):
                modified = str(modified).split('T')[0]
            
            # Status
            status = "🎯 ACTIVE" if model['name'] == self.config.ai.model else ""
            
            table.add_row(model['name'], size_str, str(modified), status)
        
        self.console.print(table)
        
        # Show current model info
        current_model = self.config.ai.model
        self.console.print(f"\n[bold]Current Model:[/bold] [cyan]{current_model}[/cyan]")
        
        # Show quick commands
        self.console.print("\n[dim]Commands:[/dim]")
        self.console.print("[dim]• model <name>  - Switch to a different model[/dim]")
        self.console.print("[dim]• ollama pull <name>  - Install a new model[/dim]")
    
    def _handle_config_show(self) -> None:
        """Handle config-show command"""
        config_text = str(self.config)
        self.console.print(Panel(config_text, title="Configuration", border_style="cyan"))
    
    def _handle_undo(self, args: List[str]) -> None:
        """Handle undo command"""
        if not args:
            self.console.print("[red]❌ Usage: undo <file>[/red]")
            return
        
        file_path = args[0]
        success = self.file_manager.undo_last_change(file_path)
        
        if success:
            self.console.print(f"[green]✅ Undo applied: {file_path}[/green]")
        else:
            self.console.print(f"[red]❌ Could not undo: {file_path}[/red]")
    
    def _handle_redo(self, args: List[str]) -> None:
        """Handle redo command"""
        if not args:
            self.console.print("[red]❌ Usage: redo <file>[/red]")
            return
        
        file_path = args[0]
        success = self.file_manager.redo_last_undo(file_path)
        
        if success:
            self.console.print(f"[green]✅ Redo applied: {file_path}[/green]")
        else:
            self.console.print(f"[red]❌ Could not redo: {file_path}[/red]")
    
    # Placeholder methods for other commands
    def _handle_delete(self, args: List[str]) -> None: pass
    def _handle_move(self, args: List[str]) -> None: pass
    def _handle_copy(self, args: List[str]) -> None: pass
    def _handle_create_project(self, args: List[str]) -> None: pass
    def _handle_analyze_project(self, args: List[str]) -> None: pass
    def _handle_refactor_project(self, args: List[str]) -> None: pass
    def _handle_tree(self, args: List[str]) -> None: pass
    def _handle_mkdir(self, args: List[str]) -> None: pass
    def _handle_rmdir(self, args: List[str]) -> None: pass
    def _handle_history(self, args: List[str]) -> None: pass
    def _handle_restore(self, args: List[str]) -> None: pass
    def _handle_safe_command(self, command: str, args: List[str]) -> None: pass
    def _handle_config(self, args: List[str]) -> None: pass
    
    def _handle_natural_language(self, user_input: str) -> bool:
        """Handle natural language commands"""
        input_lower = user_input.lower().strip()
        
        # Handle @ file references
        if '@' in user_input:
            return self._handle_file_reference(user_input)
        
        # Handle # comments/todos
        if user_input.startswith('#'):
            return self._handle_comment_todo(user_input)
        
        # Handle common natural language patterns
        patterns = [
            # Greetings and casual
            (r'^(hi|hello|hey)$', self._handle_greeting),
            (r'^(thanks?|thank you)$', self._handle_thanks),
            
            # File operations
            (r'create.*?(web server|api|app)', lambda m: self._natural_create_server()),
            (r'create.*?file', lambda m: self._natural_create_file(user_input)),
            (r'(show|display|view).*?(@\w+\.\w+|\w+\.\w+)', lambda m: self._natural_show_file(m.group(2))),
            
            # Error handling
            (r'(fix|solve|debug).*?(error|bug|issue)', lambda m: self._natural_fix_error()),
            (r'(update|modify|change).*?(@\w+\.\w+|\w+\.\w+)', lambda m: self._natural_update_file(m.group(2))),
            
            # Project operations
            (r'(analyze|check|examine).*?project', lambda m: self._natural_analyze_project()),
            (r'(list|show).*?(file|dir)', lambda m: self._natural_list_files()),
            
            # Questions
            (r'(what|how).*?', lambda m: self._handle_question(user_input)),
        ]
        
        import re
        for pattern, handler in patterns:
            match = re.search(pattern, input_lower)
            if match:
                try:
                    handler(match) if callable(handler) else handler()
                    return True
                except:
                    continue
        
        return False
    
    def _handle_natural_language_fallback(self, user_input: str) -> bool:
        """Fallback natural language handler"""
        # If AI is available, try to interpret the command
        if self.ai_client.test_connection():
            return self._ai_interpret_command(user_input)
        return False
    
    def _handle_file_reference(self, user_input: str) -> bool:
        """Handle @ file references like 'edit @app.py add logging'"""
        import re
        
        # Extract file reference
        file_match = re.search(r'@(\w+\.\w+)', user_input)
        if not file_match:
            return False
        
        filename = file_match.group(1)
        
        # Remove the @ reference to get the action
        action_text = user_input.replace(f'@{filename}', '').strip()
        
        # Determine action based on keywords
        if any(word in action_text.lower() for word in ['fix', 'debug', 'error', 'bug']):
            self._natural_fix_file(filename, action_text)
        elif any(word in action_text.lower() for word in ['edit', 'update', 'change', 'modify', 'add']):
            self._natural_edit_file(filename, action_text)
        elif any(word in action_text.lower() for word in ['show', 'display', 'view', 'cat']):
            self._handle_show([filename])
        elif any(word in action_text.lower() for word in ['refactor', 'improve', 'clean']):
            self._natural_refactor_file(filename, action_text)
        else:
            self.console.print(f"[cyan]📁 Working with file: {filename}[/cyan]")
            self.console.print(f"[yellow]Action: {action_text}[/yellow]")
            self._natural_edit_file(filename, action_text)
        
        return True
    
    def _handle_comment_todo(self, user_input: str) -> bool:
        """Handle # comments and todos"""
        comment = user_input[1:].strip()
        
        self.console.print(f"[dim]📝 Note: {comment}[/dim]")
        
        # If it contains TODO, track it
        if 'todo' in comment.lower():
            self.console.print("[yellow]✓ TODO noted! You can reference this later.[/yellow]")
        
        return True
    
    def _handle_greeting(self, match=None) -> None:
        """Handle greetings"""
        greetings = [
            "👋 Hello! I'm your AI coding assistant.",
            "🤖 Hi there! Ready to code?",
            "✨ Hey! What would you like to create today?",
            "🚀 Hello! Let's build something awesome!"
        ]
        import random
        self.console.print(f"[green]{random.choice(greetings)}[/green]")
        self.console.print("[dim]Try: 'create a web server', 'show @app.py', or 'help'[/dim]")
    
    def _handle_thanks(self, match=None) -> None:
        """Handle thanks"""
        responses = [
            "😊 You're welcome!",
            "🎉 Happy to help!",
            "✨ Anytime!",
            "🤖 Glad I could assist!"
        ]
        import random
        self.console.print(f"[green]{random.choice(responses)}[/green]")
    
    def _handle_question(self, question: str) -> None:
        """Handle questions"""
        self.console.print(f"[cyan]🤔 You asked: {question}[/cyan]")
        
        if 'file' in question.lower():
            self.console.print("[yellow]📁 For files, try: 'show filename.py' or 'ls'[/yellow]")
        elif 'create' in question.lower():
            self.console.print("[yellow]🔨 To create: 'create filename.py' or 'create a web server'[/yellow]")
        elif 'help' in question.lower():
            self._show_help()
        else:
            self.console.print("[yellow]💡 Try: 'help' for commands or describe what you want to do[/yellow]")
    
    def _natural_create_server(self) -> None:
        """Create a web server naturally"""
        self.console.print("[cyan]🌐 Creating a web server for you...[/cyan]")
        
        # Detect if we should create Python Flask or Node.js Express
        if os.path.exists('package.json'):
            self._handle_create(['server.js', 'javascript', 'Express web server with basic routes'])
        else:
            self._handle_create(['app.py', 'python', 'Flask web server with basic routes and error handling'])
    
    def _natural_create_file(self, user_input: str) -> None:
        """Create file from natural language"""
        # Extract filename if mentioned
        import re
        file_match = re.search(r'(\w+\.\w+)', user_input)
        
        if file_match:
            filename = file_match.group(1)
            # Detect language from extension
            ext = Path(filename).suffix.lower()
            lang_map = {'.py': 'python', '.js': 'javascript', '.ts': 'typescript', '.html': 'html', '.css': 'css'}
            language = lang_map.get(ext, 'text')
            
            # Extract description
            description = user_input.replace(filename, '').replace('create', '').strip()
            if not description:
                description = f"Basic {language} file"
            
            self._handle_create([filename, language, description])
        else:
            self.console.print("[yellow]💡 What file would you like to create? Try: 'create app.py'[/yellow]")
    
    def _natural_show_file(self, filename: str) -> None:
        """Show file naturally"""
        # Clean filename (remove @ if present)
        filename = filename.lstrip('@')
        self._handle_show([filename])
    
    def _natural_fix_error(self) -> None:
        """Handle error fixing"""
        self.console.print("[cyan]🔍 Looking for errors to fix...[/cyan]")
        
        # Check for common error files
        error_files = []
        for f in os.listdir('.'):
            if f.endswith(('.py', '.js', '.ts')) and os.path.isfile(f):
                error_files.append(f)
        
        if error_files:
            self.console.print(f"[yellow]📄 Found files: {', '.join(error_files[:3])}[/yellow]")
            self.console.print("[dim]💡 Try: 'fix @filename.py' to fix a specific file[/dim]")
        else:
            self.console.print("[yellow]No code files found in current directory[/yellow]")
    
    def _natural_update_file(self, filename: str) -> None:
        """Update file naturally"""
        filename = filename.lstrip('@')
        if os.path.exists(filename):
            self.console.print(f"[cyan]📝 What updates would you like to make to {filename}?[/cyan]")
            self.console.print("[dim]💡 Try: 'update @app.py add error handling'[/dim]")
        else:
            self.console.print(f"[red]❌ File not found: {filename}[/red]")
    
    def _natural_edit_file(self, filename: str, action: str) -> None:
        """Edit file with natural language"""
        if not os.path.exists(filename):
            self.console.print(f"[red]❌ File not found: {filename}[/red]")
            return
        
        # Detect language
        ext = Path(filename).suffix.lower()
        lang_map = {'.py': 'python', '.js': 'javascript', '.ts': 'typescript', '.html': 'html', '.css': 'css'}
        language = lang_map.get(ext, 'python')
        
        self.console.print(f"[cyan]📝 Editing {filename}: {action}[/cyan]")
        self._handle_edit([filename, language, action])
    
    def _natural_fix_file(self, filename: str, description: str) -> None:
        """Fix file errors naturally"""
        if not os.path.exists(filename):
            self.console.print(f"[red]❌ File not found: {filename}[/red]")
            return
        
        ext = Path(filename).suffix.lower()
        lang_map = {'.py': 'python', '.js': 'javascript', '.ts': 'typescript'}
        language = lang_map.get(ext, 'python')
        
        fix_instruction = f"fix errors and bugs, {description}"
        self.console.print(f"[cyan]🔧 Fixing {filename}...[/cyan]")
        self._handle_edit([filename, language, fix_instruction])
    
    def _natural_refactor_file(self, filename: str, description: str) -> None:
        """Refactor file naturally"""
        if not os.path.exists(filename):
            self.console.print(f"[red]❌ File not found: {filename}[/red]")
            return
        
        ext = Path(filename).suffix.lower()
        lang_map = {'.py': 'python', '.js': 'javascript', '.ts': 'typescript'}
        language = lang_map.get(ext, 'python')
        
        self.console.print(f"[cyan]♻️ Refactoring {filename}...[/cyan]")
        self._handle_refactor([filename, language, description])
    
    def _natural_analyze_project(self) -> None:
        """Analyze project naturally"""
        self.console.print("[cyan]🔍 Analyzing project structure...[/cyan]")
        self._handle_analyze_project([])
    
    def _natural_list_files(self) -> None:
        """List files naturally"""
        self._handle_ls([])
    
    def _ai_interpret_command(self, user_input: str) -> bool:
        """Use AI to interpret natural language command"""
        if not self.ai_client.test_connection():
            return False
        
        try:
            prompt = f"""
Interpret this natural language command for a coding assistant and suggest the appropriate action:

User input: "{user_input}"

Available commands:
- create <file> <language> <description>
- edit <file> <language> <changes>
- show <file>
- ls (list files)
- run <command>

Respond with just the command to execute, or "unknown" if unclear.
"""
            
            response = self.ai_client.generate(prompt)
            if response.success and response.content.strip().lower() != 'unknown':
                suggested_command = response.content.strip()
                self.console.print(f"[yellow]💡 I think you want: {suggested_command}[/yellow]")
                self.console.print("[dim]Press Enter to execute, or type a different command[/dim]")
                return True
        except:
            pass
        
        return False
