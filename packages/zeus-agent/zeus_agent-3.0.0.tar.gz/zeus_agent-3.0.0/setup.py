#!/usr/bin/env python3
"""
Zeus AI Platform Setup Script
Setup configuration for pip packaging
"""

import os
import sys
from pathlib import Path
from setuptools import setup, find_packages

# Read the contents of README file
try:
    this_directory = Path(__file__).parent
    long_description = (this_directory / "README.md").read_text(encoding='utf-8')
except:
    long_description = "Zeus AI Platform - Next-generation AI Agent Development Platform"

# Define requirements inline to avoid file reading issues in build isolation
requirements = [
    "PyYAML>=6.0",
    "numpy>=1.21.0",
    "scipy>=1.7.0", 
    "pandas>=1.3.0",
    "sentence-transformers>=2.2.0",
    "transformers>=4.21.0",
    "torch>=1.12.0",
    "torchvision>=0.13.0",
    "scikit-learn>=1.1.0",
    "chromadb>=0.4.0",
    "openai>=1.0.0",
    "nltk>=3.7",
    "spacy>=3.4.0",
    "cryptography>=3.4.8",
    "pydantic>=2.0.0",
    "aiohttp>=3.8.0",
    "asyncio-throttle>=1.0.0",
    "sqlalchemy>=1.4.0",
    "aiosqlite>=0.17.0",
    "python-docx>=0.8.11",
    "PyPDF2>=3.0.0",
    "markdown>=3.4.0",
    "loguru>=0.6.0",
    "prometheus-client>=0.14.0",
    "httpx>=0.24.0",
    "requests>=2.28.0",
    "python-dotenv>=1.0.0",
    "python-dateutil>=2.8.0",
    "jsonschema>=4.17.0",
]

# Read version from layers/__init__.py
version = "3.0.0"
try:
    with open('layers/__init__.py', 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                version = line.split('=')[1].strip().strip('"').strip("'")
                break
except:
    pass

setup(
    name="zeus-agent",
    version=version,
    author="Agent Development Center Team",
    author_email="support@zeus-ai.com",
    description="Zeus AI Platform - Next-generation AI Agent Development Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fpga1988/zeus",
    project_urls={
        "Bug Tracker": "https://github.com/fpga1988/zeus/issues",
        "Documentation": "https://github.com/fpga1988/zeus/docs",
        "Source Code": "https://github.com/fpga1988/zeus",
        "Gitee Mirror": "https://gitee.com/fpga1988/zeus",
    },
    packages=find_packages(include=['layers*', 'lib*', 'zeus*'], exclude=['tests*', 'examples*', 'docs*', 'htmlcov*', 'temp*', 'test_env*', 'venv*', 'workspace*']),
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Code Generators",
        "Framework :: AsyncIO",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0", 
            "pytest-mock>=3.10.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.5.0",
            "pytest-cov>=4.0.0",
        ],
        "gui": [
            "PyQt6>=6.0.0",
            "customtkinter>=5.0.0",
        ],
        "web": [
            "fastapi>=0.100.0",
            "uvicorn>=0.20.0",
        ],
        "vector": [
            "faiss-cpu>=1.7.0",
            "hnswlib>=0.7.0",
        ],
        "all": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0", 
            "pytest-mock>=3.10.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.5.0",
            "pytest-cov>=4.0.0",
            "PyQt6>=6.0.0",
            "customtkinter>=5.0.0",
            "fastapi>=0.100.0",
            "uvicorn>=0.20.0",
            "faiss-cpu>=1.7.0",
            "hnswlib>=0.7.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "zeus=zeus.cli:main",
            "zeus-agent=zeus.cli:agent_cmd",
            "zeus-dev=zeus.cli:dev_cmd",
        ],
    },
    keywords=[
        "ai", "agent", "artificial-intelligence", "machine-learning", 
        "nlp", "chatbot", "automation", "framework", "platform",
        "fpga", "hardware", "digital-design", "verification",
        "autogen", "langchain", "crewai", "multi-agent"
    ],
    zip_safe=False,
    package_data={
        "zeus": [
            "config/*.yaml",
            "config/templates/*.yaml", 
            "config/schemas/*.json",
            "cfg/templates/*.yaml",
            "cfg/examples/*.yaml",
            "data/*.json",
            "lib/**/*.py",
            "lib/**/*.yaml",
            "lib/**/*.json",
            "workspace/agents/*/config/*.yaml",
            "workspace/agents/*/knowledge/*.json",
            "workspace/agents/*/knowledge/*.md",
        ],
    },
    data_files=[
        ('zeus/docs', ['README.md', 'CHANGELOG.md', 'LICENSE']),
    ],
)
