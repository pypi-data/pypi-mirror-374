"""
Enhanced Ollama API client for CodeDev - Advanced AI Coding Assistant
Author: Ashok Kumar (https://ashokumar.in)
"""

import json
import time
import requests
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from pathlib import Path

from ..utils.logger import get_logger
from ..core.config import Config


@dataclass
class AIResponse:
    """AI response data structure"""
    content: str
    model: str
    success: bool
    error: Optional[str] = None
    tokens_used: int = 0
    response_time: float = 0.0
    code_blocks: List[str] = None
    terminal_commands: List[str] = None


class OllamaClient:
    """Enhanced Ollama API client with advanced coding capabilities"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = get_logger(__name__)
        self.session = requests.Session()
        
        # Setup session with retries and timeouts
        try:
            adapter = requests.adapters.HTTPAdapter(
                max_retries=getattr(config.ai, 'max_retries', 3)
            )
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)
        except Exception:
            pass
        
        # Set session timeouts
        self.timeout = getattr(config.ai, 'timeout', 120)
        self.connection_timeout = getattr(config.ai, 'connection_timeout', 15)
        self.retry_delay = getattr(config.ai, 'retry_delay', 2)
        
        # Load system prompts
        self.system_prompt = self._load_system_prompt()
        
        # Context management
        self.conversation_history = []
        self.max_context_length = getattr(config.ai, 'max_context_length', 8000)
    
    def _load_system_prompt(self) -> str:
        """Load the advanced system prompt"""
        try:
            prompt_path = Path(__file__).parent.parent / "prompts" / "system_prompt.md"
            if prompt_path.exists():
                return prompt_path.read_text(encoding='utf-8')
            else:
                return self._get_default_system_prompt()
        except Exception as e:
            self.logger.warning(f"Failed to load system prompt: {e}")
            return self._get_default_system_prompt()
    
    def _get_default_system_prompt(self) -> str:
        """Default system prompt for CodeDev"""
        return """You are CodeDev, an advanced AI coding assistant created by Ashok Kumar (https://ashokumar.in).

CORE RULES:
1. Provide working code, not explanations
2. Focus on practical solutions
3. Use terminal commands when needed
4. Minimize theory, maximize implementation
5. Always include executable examples

You have full terminal access and can execute any command. Provide complete, working solutions."""
    
    def health_check(self) -> bool:
        """Check if Ollama service is available"""
        try:
            health_timeout = getattr(self.config.ai, 'health_check_timeout', 10)
            response = self.session.get(
                f"{self.config.ai.api_url}/api/tags",
                timeout=(5, health_timeout)
            )
            response.raise_for_status()
            self.logger.debug("Ollama health check passed")
            return True
        except Exception as e:
            self.logger.warning(f"Ollama health check failed: {e}")
            return False
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models from Ollama"""
        try:
            response = self.session.get(
                f"{self.config.ai.api_url}/api/tags",
                timeout=(10, 30)
            )
            response.raise_for_status()
            data = response.json()
            return data.get('models', [])
        except Exception as e:
            self.logger.error(f"Failed to get available models: {e}")
            return []
    
    def select_best_model(self) -> Optional[str]:
        """Select the best available model based on preferences"""
        models = self.get_available_models()
        if not models:
            return None
        
        # Priority order for model selection
        preferred_models = [
            'deepseek-r1:8b',
            'deepseek-r1:1.5b', 
            'deepseek-coder:6.7b',
            'deepseek-coder:1.3b',
            'codellama:7b',
            'codellama:13b',
            'llama3.2:8b',
            'llama3.2:3b',
            'qwen2.5-coder:7b',
            'qwen2.5-coder:3b'
        ]
        
        available_model_names = [model['name'] for model in models]
        
        # First try exact matches
        for preferred in preferred_models:
            if preferred in available_model_names:
                self.logger.info(f"Selected model: {preferred}")
                return preferred
        
        # If no preferred model found, use the first available
        if models:
            model_name = models[0]['name']
            self.logger.info(f"Selected first available model: {model_name}")
            return model_name
        
        return None

    def chat(self, message: str, model: Optional[str] = None, 
             include_context: bool = True, stream: bool = False) -> AIResponse:
        """Send a chat message to Ollama"""
        start_time = time.time()
        
        if not model:
            model = getattr(self.config.ai, 'model', 'llama2:latest')
        
        # Build messages
        messages = []
        
        # Add system prompt
        messages.append({
            "role": "system",
            "content": self.system_prompt
        })
        
        # Add conversation history if requested
        if include_context:
            messages.extend(self.conversation_history[-10:])  # Last 10 messages
        
        # Add current message
        messages.append({
            "role": "user",
            "content": message
        })
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": getattr(self.config.ai, 'temperature', 0.1),
                "num_predict": getattr(self.config.ai, 'max_tokens', 4000),
            }
        }
        
        try:
            response = self.session.post(
                f"{self.config.ai.api_url}/api/chat",
                json=payload,
                timeout=(self.connection_timeout, self.timeout)
            )
            response.raise_for_status()
            
            data = response.json()
            content = data.get('message', {}).get('content', '')
            
            # Store in conversation history
            self.conversation_history.extend([
                {"role": "user", "content": message},
                {"role": "assistant", "content": content}
            ])
            
            # Extract code blocks and terminal commands
            code_blocks = self._extract_code_blocks(content)
            terminal_commands = self._extract_terminal_commands(content)
            
            return AIResponse(
                content=content,
                model=model,
                success=True,
                tokens_used=data.get('eval_count', 0),
                response_time=time.time() - start_time,
                code_blocks=code_blocks,
                terminal_commands=terminal_commands
            )
            
        except Exception as e:
            self.logger.error(f"Chat request failed: {e}")
            return AIResponse(
                content=f"Error: {str(e)}",
                model=model,
                success=False,
                error=str(e),
                response_time=time.time() - start_time
            )
    
    def _extract_code_blocks(self, content: str) -> List[str]:
        """Extract code blocks from markdown content"""
        import re
        pattern = r'```(?:\w+\n)?(.*?)```'
        matches = re.findall(pattern, content, re.DOTALL)
        return [match.strip() for match in matches]
    
    def _extract_terminal_commands(self, content: str) -> List[str]:
        """Extract terminal commands from content"""
        import re
        # Look for bash/shell command patterns
        patterns = [
            r'`([^`]*(?:npm|pip|git|docker|curl|wget|make|gcc|python|node)[^`]*)`',
            r'\$\s*([^\n]+)',
            r'bash\s*\n([^\n]+)',
            r'sh\s*\n([^\n]+)'
        ]
        
        commands = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            commands.extend(matches)
        
        return [cmd.strip() for cmd in commands if cmd.strip()]
    
    def generate_code(self, request: str, language: str = "python", 
                     context: Optional[str] = None) -> AIResponse:
        """Generate code for a specific request"""
        prompt = f"""Generate {language} code for the following request:

{request}

Requirements:
- Provide working, executable code
- Include necessary imports
- Add error handling where appropriate
- Include brief comments for complex logic
- Focus on practical implementation

{f"Context: {context}" if context else ""}

Provide only the code, no explanations."""

        return self.chat(prompt, include_context=False)
    
    def explain_code(self, code: str, language: str = "python") -> AIResponse:
        """Explain provided code"""
        prompt = f"""Explain this {language} code briefly and practically:

```{language}
{code}
```

Focus on:
- What it does
- Key functions/methods
- Potential improvements
- Usage examples"""

        return self.chat(prompt, include_context=False)
    
    def debug_code(self, code: str, error: str, language: str = "python") -> AIResponse:
        """Debug code with error"""
        prompt = f"""Debug this {language} code that has an error:

Code:
```{language}
{code}
```

Error:
{error}

Provide:
1. Fixed code
2. Brief explanation of the issue
3. Prevention tips"""

        return self.chat(prompt, include_context=False)
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history.clear()
        self.logger.info("Conversation history cleared")
    
    def get_history_summary(self) -> str:
        """Get summary of conversation history"""
        if not self.conversation_history:
            return "No conversation history"
        
        total_messages = len(self.conversation_history)
        user_messages = len([m for m in self.conversation_history if m.get("role") == "user"])
        
        return f"History: {total_messages} messages ({user_messages} user, {total_messages - user_messages} assistant)"


# Backward compatibility alias
EnhancedOllamaClient = OllamaClient
