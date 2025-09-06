"""
Ollama installation and system management utilities
"""

import os
import platform
import subprocess
import time
import requests
from pathlib import Path
from typing import Optional, Tuple, List

from .logger import get_logger


class OllamaInstaller:
    """Manages Ollama installation and service"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.system = platform.system().lower()
        self.is_linux = self.system == 'linux'
        self.is_macos = self.system == 'darwin'
        self.is_windows = self.system == 'windows'
    
    def is_ollama_installed(self) -> bool:
        """Check if Ollama is installed"""
        try:
            result = subprocess.run(['ollama', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def is_ollama_running(self) -> bool:
        """Check if Ollama service is running"""
        try:
            response = requests.get('http://127.0.0.1:11434/api/tags', timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def install_ollama_linux(self) -> Tuple[bool, str]:
        """Install Ollama on Linux using the official installer"""
        if not self.is_linux:
            return False, "This method only works on Linux"
        
        try:
            self.logger.info("Installing Ollama on Linux...")
            
            # Download and run the official installer
            install_cmd = "curl -fsSL https://ollama.com/install.sh | sh"
            result = subprocess.run(install_cmd, shell=True, capture_output=True, 
                                  text=True, timeout=300)
            
            if result.returncode == 0:
                self.logger.info("Ollama installation completed successfully")
                return True, "Installation successful"
            else:
                error_msg = f"Installation failed: {result.stderr}"
                self.logger.error(error_msg)
                return False, error_msg
                
        except subprocess.TimeoutExpired:
            error_msg = "Installation timed out"
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Installation error: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def start_ollama_service(self) -> Tuple[bool, str]:
        """Start Ollama service"""
        try:
            if self.is_linux:
                # Try systemctl first
                try:
                    result = subprocess.run(['sudo', 'systemctl', 'start', 'ollama'], 
                                          capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        time.sleep(3)  # Give service time to start
                        if self.is_ollama_running():
                            return True, "Ollama service started via systemctl"
                except:
                    pass
                
                # Fallback to direct command
                try:
                    subprocess.Popen(['ollama', 'serve'], 
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL)
                    time.sleep(5)  # Give service time to start
                    if self.is_ollama_running():
                        return True, "Ollama service started directly"
                except:
                    pass
            
            elif self.is_macos or self.is_windows:
                # For macOS and Windows, try direct command
                try:
                    subprocess.Popen(['ollama', 'serve'],
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
                    time.sleep(5)
                    if self.is_ollama_running():
                        return True, "Ollama service started"
                except:
                    pass
            
            return False, "Failed to start Ollama service"
            
        except Exception as e:
            return False, f"Error starting service: {e}"
    
    def setup_ollama(self) -> Tuple[bool, str, List[str]]:
        """Complete Ollama setup process"""
        setup_log = []
        
        # Check if already installed and running
        if self.is_ollama_installed():
            setup_log.append("✅ Ollama is already installed")
            if self.is_ollama_running():
                setup_log.append("✅ Ollama service is running")
                return True, "Ollama is ready", setup_log
            else:
                setup_log.append("⚠️ Ollama is installed but not running")
                success, msg = self.start_ollama_service()
                setup_log.append(f"{'✅' if success else '❌'} {msg}")
                return success, msg, setup_log
        
        # Install Ollama
        setup_log.append("❌ Ollama is not installed")
        
        if self.is_linux:
            setup_log.append("🔄 Installing Ollama on Linux...")
            success, msg = self.install_ollama_linux()
            setup_log.append(f"{'✅' if success else '❌'} {msg}")
            
            if success:
                # Start service after installation
                setup_log.append("🔄 Starting Ollama service...")
                success, msg = self.start_ollama_service()
                setup_log.append(f"{'✅' if success else '❌'} {msg}")
                return success, msg, setup_log
            else:
                return False, msg, setup_log
        
        elif self.is_macos:
            msg = "Please install Ollama manually on macOS:\n" \
                  "1. Download from https://ollama.com/download\n" \
                  "2. Install the .dmg file\n" \
                  "3. Run 'ollama serve' in terminal"
            setup_log.append(f"ℹ️ {msg}")
            return False, msg, setup_log
        
        elif self.is_windows:
            msg = "Please install Ollama manually on Windows:\n" \
                  "1. Download from https://ollama.com/download\n" \
                  "2. Install the .exe file\n" \
                  "3. Run 'ollama serve' in command prompt"
            setup_log.append(f"ℹ️ {msg}")
            return False, msg, setup_log
        
        else:
            msg = f"Unsupported operating system: {self.system}"
            setup_log.append(f"❌ {msg}")
            return False, msg, setup_log
    
    def get_installation_instructions(self) -> str:
        """Get platform-specific installation instructions"""
        if self.is_linux:
            return """
🐧 Linux Installation:
Run: curl -fsSL https://ollama.com/install.sh | sh

Or the AI Coder can install it automatically for you.
"""
        elif self.is_macos:
            return """
🍎 macOS Installation:
1. Download Ollama from: https://ollama.com/download
2. Open the downloaded .dmg file
3. Drag Ollama to Applications folder
4. Run 'ollama serve' in Terminal
"""
        elif self.is_windows:
            return """
🪟 Windows Installation:
1. Download Ollama from: https://ollama.com/download
2. Run the downloaded .exe installer
3. Open Command Prompt or PowerShell
4. Run 'ollama serve'
"""
        else:
            return f"❌ Unsupported operating system: {self.system}"
