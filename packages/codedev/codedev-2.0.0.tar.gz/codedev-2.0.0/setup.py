#!/usr/bin/env python3
"""
Setup script for CodeDev - Advanced AI Coding Assistant
"""

from setuptools import setup, find_packages
import os

def read_file(filename):
    """Read file contents"""
    with open(filename, "r", encoding="utf-8") as fh:
        return fh.read()

def get_requirements():
    """Get requirements from requirements.txt"""
    requirements = []
    if os.path.exists("requirements.txt"):
        requirements = [line.strip() for line in read_file("requirements.txt").splitlines() 
                      if line.strip() and not line.startswith("#")]
    return requirements

# Get long description
long_description = read_file("README.md") if os.path.exists("README.md") else "Advanced AI Coding Assistant"

setup(
    name="codedev",
    version="2.0.0",
    author="Ashok Kumar",
    author_email="contact@ashokumar.in",
    description="Advanced AI Coding Assistant with Terminal Integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://ashokumar.in",
    project_urls={
        "Homepage": "https://ashokumar.in",
        "Source": "https://github.com/ashokumar06/codedev",
        "Bug Reports": "https://github.com/ashokumar06/codedev/issues",
        "Documentation": "https://ashokumar.in/codedev",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
        "Environment :: Console",
        "Natural Language :: English",
    ],
    keywords="ai coding assistant terminal automation ollama code-generation",
    python_requires=">=3.8",
    install_requires=get_requirements(),
    entry_points={
        "console_scripts": [
            "codedev=ai_coder.main:main",
            "cdev=ai_coder.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "ai_coder": [
            "config/*.yaml",
            "templates/*.txt",
            "prompts/*.md",
        ],
    },
    data_files=[
        ('share/codedev/config', ['config/default.yaml']),
    ],
    zip_safe=False,
)
