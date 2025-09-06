"""
AI Coder Package
Advanced CLI REPL Agent for AI-powered coding
"""

__version__ = "1.0.0"
__author__ = "AI Coder Team"
__description__ = "Advanced CLI REPL Agent for AI-powered coding"

from .cli import AiCoderCLI
from .core.config import Config

__all__ = ['AiCoderCLI', 'Config']
