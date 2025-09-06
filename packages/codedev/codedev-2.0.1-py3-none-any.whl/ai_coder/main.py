#!/usr/bin/env python3
"""
CodeDev - Advanced AI Coding Assistant
Global entry point for the application
"""

import sys
import os
import argparse
from pathlib import Path

from .cli import AiCoderCLI
from .core.config import Config
from .utils.logger import setup_logging

def main():
    """Main entry point for CodeDev"""
    parser = argparse.ArgumentParser(
        description="CodeDev - Advanced AI Coding Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  codedev                   # Start in current directory
  codedev -w /path/to/code  # Start in specific workspace
  codedev -m codellama      # Use specific model
  cdev                      # Short command alias
  
Author: Ashok Kumar
Website: https://ashokumar.in
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Path to config file'
    )
    
    parser.add_argument(
        '--model', '-m',
        type=str,
        help='AI model to use (default: from config)'
    )
    
    parser.add_argument(
        '--workspace', '-w',
        type=str,
        default=os.getcwd(),
        help='Workspace directory (default: current directory)'
    )
    
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='Enable debug logging'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='CodeDev v2.0.0 - Advanced AI Coding Assistant\nAuthor: Ashok Kumar\nWebsite: https://ashokumar.in'
    )

    parser.add_argument(
        '--install-ollama',
        action='store_true',
        help='Install Ollama if not present'
    )

    args = parser.parse_args()
    
    try:
        # Setup logging
        setup_logging(debug=args.debug)
        
        # Handle Ollama installation
        if args.install_ollama:
            from .utils.ollama_installer import OllamaInstaller
            installer = OllamaInstaller()
            installer.install()
            return
        
        # Initialize configuration
        config = Config(config_file=args.config)
        
        # Override config with command line args
        if args.model:
            config.set('ai.model', args.model)
        
        if args.workspace:
            config.set('workspace.directory', args.workspace)
        
        # Print welcome message
        print("🚀 Welcome to CodeDev - Advanced AI Coding Assistant")
        print(f"📁 Workspace: {args.workspace}")
        print(f"🤖 Model: {config.get('ai.model', 'default')}")
        print("💡 Type 'help' for commands or 'exit' to quit\n")
        
        # Initialize and start CLI
        cli = AiCoderCLI(config)
        cli.run()
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye! Thanks for using CodeDev!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
