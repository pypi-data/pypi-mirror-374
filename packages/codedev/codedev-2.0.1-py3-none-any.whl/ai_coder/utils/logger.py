"""
Logging utilities for AI Coder
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Colored log formatter"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    
    RESET = '\033[0m'
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(debug: bool = False, log_file: Optional[str] = None) -> None:
    """Setup logging configuration"""
    
    # Create logs directory
    log_dir = Path.home() / ".ai-coder" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Log file path
    if not log_file:
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = log_dir / f"ai-coder-{timestamp}.log"
    
    # Configure logging level
    level = logging.DEBUG if debug else logging.INFO
    
    # Create root logger
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = ColoredFormatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    try:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not setup file logging: {e}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)


class ActionLogger:
    """Logger for user actions and system events"""
    
    def __init__(self, log_file: Optional[str] = None):
        self.logger = get_logger('ai_coder.actions')
        
        if log_file:
            try:
                handler = logging.FileHandler(log_file)
                formatter = logging.Formatter(
                    '%(asctime)s [ACTION] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
            except Exception as e:
                self.logger.warning(f"Could not setup action logging: {e}")
    
    def log_action(self, action: str, details: dict = None):
        """Log a user action"""
        message = f"{action}"
        if details:
            details_str = ", ".join(f"{k}={v}" for k, v in details.items())
            message += f" | {details_str}"
        
        self.logger.info(message)
    
    def log_file_operation(self, operation: str, file_path: str, success: bool = True):
        """Log file operations"""
        status = "SUCCESS" if success else "FAILED"
        self.log_action(f"FILE_{operation.upper()}", {
            'file': file_path,
            'status': status
        })
    
    def log_command_execution(self, command: str, success: bool = True, output: str = ""):
        """Log command executions"""
        status = "SUCCESS" if success else "FAILED"
        self.log_action("COMMAND_EXEC", {
            'command': command,
            'status': status,
            'output_length': len(output)
        })
    
    def log_ai_interaction(self, prompt: str, model: str, success: bool = True):
        """Log AI interactions"""
        status = "SUCCESS" if success else "FAILED"
        self.log_action("AI_INTERACTION", {
            'model': model,
            'prompt_length': len(prompt),
            'status': status
        })
