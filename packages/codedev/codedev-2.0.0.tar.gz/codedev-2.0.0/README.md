# CodeDev - Advanced AI Coding Assistant

[![PyPI version](https://badge.fury.io/py/codedev.svg)](https://badge.fury.io/py/codedev)
[![Python Version](https://img.shields.io/pypi/pyversions/codedev.svg)](https://pypi.org/project/codedev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Repository](https://img.shields.io/badge/GitHub-ashokumar06%2Fcodedev-blue.svg)](https://github.com/ashokumar06/codedev)
[![GitHub Issues](https://img.shields.io/github/issues/ashokumar06/codedev.svg)](https://github.com/ashokumar06/codedev/issues)
[![GitHub Stars](https://img.shields.io/github/stars/ashokumar06/codedev.svg)](https://github.com/ashokumar06/codedev/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/ashokumar06/codedev.svg)](https://github.com/ashokumar06/codedev/network)

🚀 **CodeDev** is an advanced open-source AI-powered coding assistant with terminal integration, created by [Ashok Kumar](https://ashokumar.in).

## 🔗 Links & Resources

- 📦 **GitHub Repository**: [https://github.com/ashokumar06/codedev](https://github.com/ashokumar06/codedev)
- 🐍 **PyPI Package**: [https://pypi.org/project/codedev/](https://pypi.org/project/codedev/)
- 📚 **Documentation**: [GitHub Wiki](https://github.com/ashokumar06/codedev/wiki)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/ashokumar06/codedev/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/ashokumar06/codedev/discussions)
- 👤 **Author**: [Ashok Kumar](https://ashokumar.in)

## 🎯 Open Source

CodeDev is completely **open source** and free to use! We welcome contributions from the community.

- ⭐ **Star us on GitHub**: [github.com/ashokumar06/codedev](https://github.com/ashokumar06/codedev)
- 🍴 **Fork the project**: Create your own improvements
- 🐛 **Report bugs**: Help us improve the software
- 💡 **Suggest features**: Share your ideas
- 🤝 **Contribute code**: Submit pull requests

---

## 🚀 Installation Options

### Option 1: Install from PyPI (Recommended)

```bash
# Install the latest stable version
pip install codedev

# Use the commands
codedev --version
cdev --version

# Start using
codedev
```

### Option 2: Install from GitHub (Latest)

```bash
# Install directly from GitHub
pip install git+https://github.com/ashokumar06/codedev.git

# Or clone and install
git clone https://github.com/ashokumar06/codedev.git
cd codedev
pip install .
```

### Option 3: Build from Source (Development)

```bash
# Clone the repository
git clone https://github.com/ashokumar06/codedev.git
cd codedev

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Test installation
codedev --version
cdev --version
```

### Option 4: Direct Build and Install

```bash
# Clone and build wheel
git clone https://github.com/ashokumar06/codedev.git
cd codedev

# Install build tools
pip install build

# Build the package
python -m build

# Install the wheel
pip install dist/codedev-*.whl
```

## ✨ Key Features

### 🚀 Smart Initialization
- **Automatic Ollama Detection**: Checks for Ollama installation on startup
- **One-Click Linux Installation**: Auto-installs Ollama using `curl -fsSL https://ollama.com/install.sh | sh`
- **Cross-Platform Support**: Detects Linux, macOS, and Windows with appropriate instructions
- **Model Auto-Selection**: Automatically selects the best available coding model
- **Health Checks**: Verifies AI service connectivity before starting

### 🧠 AI-Powered Development
- **Natural Language Interface**: Talk naturally - "create a web server", "fix this error"
- **Context-Aware Responses**: Understands your project structure and coding patterns
- **Multiple AI Models**: Support for DeepSeek, Codellama, Qwen2.5-Coder, Llama3.2, and more
- **Smart Model Management**: Auto-detects and recommends optimal models for coding tasks
- **Improved Timeout Handling**: Better stability with slow AI responses

### 📁 Advanced File Management
- **File Operations**: Create, edit, refactor, move, copy, delete with full history
- **Project Management**: Generate complete projects with templates and AI assistance
- **Version Control**: Built-in undo/redo with automatic file versioning
- **Smart File Detection**: Auto-detects languages and applies appropriate coding standards

### 💬 Enhanced Natural Language Processing
- **File References**: Use `@filename` to reference specific files
- **Todo/Comments**: Add notes with `# todo add authentication`
- **Conversational Commands**: Casual interactions like "hi", "thanks", "what files do I have?"
- **Context Understanding**: Remembers previous conversations and file states

### 🛡️ Safety & Security
- **Safe Command Execution**: Whitelisted commands with sandboxing
- **Path Protection**: Prevents access to system directories
- **File Size Limits**: Configurable limits for file operations
- **Backup Creation**: Automatic backups before destructive operations

### 🎨 Rich Terminal Experience
- **Beautiful UI**: Rich terminal interface with colors, tables, and panels
- **Smart Completion**: Auto-complete for commands and file names
- **History Management**: Persistent command history across sessions
- **Interactive Prompts**: Intuitive prompts with context information

## 🔧 Setup & Usage

### Quick Start

1. **Install CodeDev**:
   ```bash
   pip install codedev
   ```

2. **Start using**:
   ```bash
   codedev                   # Start in current directory
   cdev                      # Short command
   ```

3. **AI will auto-setup Ollama** (Linux) or guide you through manual installation

### Usage Examples

#### Natural Language Commands
```bash
codedev> create a web server
codedev> fix @app.py
codedev> show my files  
codedev> # todo add authentication
codedev> refactor this code to use classes
```

#### Structured Commands
```bash
codedev> create server.py python "FastAPI web server with JWT auth"
codedev> edit @app.py python "add error handling"
codedev> models                    # Show available AI models
codedev> model deepseek-coder:6.7b # Switch to different model
codedev> help                      # Show all commands
```

#### Project Operations
```bash
codedev> create-project python myapi "REST API with FastAPI"
codedev> analyze-project
codedev> refactor-project "add type hints everywhere"
```

## 🤖 Model Management

The AI Coder automatically detects and manages AI models:

### Automatic Model Selection
The system prioritizes models in this order:
1. **DeepSeek R1**: `deepseek-r1:8b`, `deepseek-r1:1.5b`
2. **DeepSeek Coder**: `deepseek-coder:6.7b`, `deepseek-coder:1.3b`
3. **Llama 3.2**: `llama3.2:8b`, `llama3.2:3b`, `llama3.2:1b`
4. **Qwen2.5 Coder**: `qwen2.5-coder:7b`, `qwen2.5-coder:3b`
5. **CodeLlama**: `codellama:7b`, `codellama:13b`
6. **Phi3**: `phi3:3.8b`, `phi3:mini`

### Model Commands
```bash
ai-coder> models                    # Show detailed model information
ai-coder> model llama3.2:8b        # Switch to specific model
ai-coder> ollama pull deepseek-r1:8b # Install new model
```

## ⚙️ Configuration

### Config File Location
- **Linux/macOS**: `~/.config/ai-coder/config.yaml`
- **Windows**: `%APPDATA%/ai-coder/config.yaml`

### Key Settings
```yaml
ai:
  api_url: "http://127.0.0.1:11434"
  model: "deepseek-r1:8b"
  timeout: 120
  max_retries: 5
  temperature: 0.7

workspace:
  directory: "."
  history_dir: ".ai-coder-history"
  auto_save: true
  backup_on_edit: true

safety:
  allowed_commands: ["python", "node", "git", ...]
  blocked_paths: ["/etc", "/usr", "~/.ssh", ...]
  max_file_size: 10485760  # 10MB
```

## 🌐 Platform Support

| Platform | Installation | Status |
|----------|-------------|---------|
| **Linux** | ✅ Automatic | Fully Supported |
| **macOS** | 📋 Manual | Supported |
| **Windows** | 📋 Manual | Supported |

### Linux
- Auto-installs Ollama using official installer
- Auto-starts service via systemctl or direct command
- Full feature support

### macOS & Windows
- Manual installation required
- Download from https://ollama.com/download
- All features supported after manual setup

## 🔍 Troubleshooting

### Common Issues

**Ollama Not Found**
```bash
# Linux: AI Coder will offer to install automatically
# macOS/Windows: Download from https://ollama.com/download
```

**Connection Timeout**
```bash
# Check if Ollama is running
ollama serve

# Check service status (Linux)
systemctl status ollama
```

**No Models Available**
```bash
# AI Coder will automatically suggest and install recommended models
# Or manually: ollama pull deepseek-r1:8b
```

## 📚 Advanced Features

### File Versioning
- Every edit creates a timestamped backup
- Full undo/redo history per file
- Restore to any previous version

### Smart Context
- Understands project structure
- Maintains conversation history
- Learns from your coding patterns

### Cross-Platform CLI
- Works identically on Linux, macOS, Windows
- Rich terminal UI with colors and formatting
- Intelligent error handling and recovery

## 🤝 Contributing

We welcome contributions from the community! CodeDev is open source and thrives on community involvement.

### Ways to Contribute

1. **⭐ Star the Repository**: Show your support on [GitHub](https://github.com/ashokumar06/codedev)
2. **🐛 Report Bugs**: Submit issues on [GitHub Issues](https://github.com/ashokumar06/codedev/issues)
3. **💡 Feature Requests**: Suggest new features via [GitHub Discussions](https://github.com/ashokumar06/codedev/discussions)
4. **📖 Documentation**: Improve docs and examples
5. **🔧 Code Contributions**: Submit pull requests

### Development Setup

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/codedev.git
cd codedev

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Run tests
python test_installation.py

# Make your changes and submit a pull request!
```

### Project Structure

```
codedev/
├── ai_coder/           # Main package
│   ├── ai/            # AI client and prompt management
│   ├── core/          # Configuration and core utilities  
│   ├── operations/    # File and project operations
│   ├── safety/        # Security and sandboxing
│   ├── utils/         # Utilities and platform detection
│   └── cli.py         # Main CLI interface
├── config/            # Default configuration
├── tests/             # Test suite
├── .github/           # GitHub workflows
└── setup.py           # Package configuration
```

## 📄 License

CodeDev is released under the **MIT License** - see [LICENSE](https://github.com/ashokumar06/codedev/blob/main/LICENSE) file for details.

This means you can:
- ✅ Use it commercially
- ✅ Modify and distribute
- ✅ Private use
- ✅ Include in your projects

## � Support the Project

If you find CodeDev useful, please consider:

- ⭐ **Starring** the repository on [GitHub](https://github.com/ashokumar06/codedev)
- 🐛 **Reporting bugs** and suggesting features
- 🤝 **Contributing** code or documentation
- 💬 **Sharing** it with other developers

---

## 🎯 Get Started Now!

```bash
# Install and start using immediately
pip install codedev
codedev

# Or build from source
git clone https://github.com/ashokumar06/codedev.git
cd codedev && pip install -e .
codedev --version
```

**Ready to revolutionize your coding workflow with AI?** 🚀

---

<div align="center">

**Made with ❤️ by [Ashok Kumar](https://ashokumar.in)**

[GitHub](https://github.com/ashokumar06/codedev) • [PyPI](https://pypi.org/project/codedev/) • [Issues](https://github.com/ashokumar06/codedev/issues) • [Discussions](https://github.com/ashokumar06/codedev/discussions)

</div>
