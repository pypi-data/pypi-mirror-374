"""
Fixed Setup.py for PyGenAI Security Framework
Corrects the version comparison bug and other potential issues.
"""

import os
import sys
from pathlib import Path
from setuptools import setup, find_packages

# Ensure minimum Python version - FIXED: Use tuple (3, 8) instead of float (3.8)
if sys.version_info < (3, 8):
    sys.exit('Python 3.8 or later is required.')

# Read README file
def read_readme():
    readme_path = Path(__file__).parent / "README.md"
    if readme_path.exists():
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "PyGenAI Security Framework - Comprehensive Python and GenAI security scanning"

# Read requirements
def get_requirements():
    requirements = []
    requirements_path = Path(__file__).parent / "requirements.txt"
    
    if requirements_path.exists():
        with open(requirements_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    requirements.append(line)
    
    # Fallback requirements if file doesn't exist
    if not requirements:
        requirements = [
            "click>=8.0.0",
            "pyyaml>=6.0",
            "requests>=2.28.0",
            "colorama>=0.4.4",
            "rich>=12.0.0",
            "jinja2>=3.0.0",
        ]
    
    return requirements

setup(
    name="pygenai-security",
    version="0.0.3",
    author="RiteshGenAI",
    author_email="riteshpatilgenaiofficial@gmail.com",
    description="Comprehensive Python and GenAI security scanning framework",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/RiteshGenAI/pygenai-security",
    project_urls={
        "Bug Reports": "https://github.com/RiteshGenAI/pygenai-security/issues",
        "Documentation": "https://pygenai-security.readthedocs.io/",
        "Source": "https://github.com/RiteshGenAI/pygenai-security",
        "Funding": "https://github.com/sponsors/RiteshGenAI",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "docs"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Environment :: Console",
        "Environment :: Web Environment",
    ],
    keywords=[
        "security", "vulnerability", "scanning", "python", "genai", "llm", 
        "static-analysis", "code-analysis", "cybersecurity", "devsecops",
        "ai-security", "prompt-injection", "enterprise", "compliance"
    ],
    python_requires=">=3.8",
    install_requires=get_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "pre-commit>=2.20.0",
            "tox>=3.25.0",
        ],
        "enterprise": [
            "pygls>=1.0.0",
            "lsprotocol>=2023.0.0",
            "fastapi>=0.100.0",
            "uvicorn>=0.20.0",
            "sqlalchemy>=2.0.0",
            "alembic>=1.12.0",
        ],
        "docs": [
            "mkdocs>=1.4.0",
            "mkdocs-material>=8.0.0",
            "mkdocs-mermaid2-plugin>=0.6.0",
        ],
        "all": [
            # Include all extras
            "pytest>=7.0.0", "pytest-cov>=4.0.0", "pytest-asyncio>=0.21.0",
            "black>=22.0.0", "flake8>=5.0.0", "mypy>=1.0.0", 
            "pygls>=1.0.0", "lsprotocol>=2023.0.0",
            "fastapi>=0.100.0", "uvicorn>=0.20.0",
            "mkdocs>=1.4.0", "mkdocs-material>=8.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "pygenai-security=pygenai_security.cli.cli:cli",
            "pygenai=pygenai_security.cli.cli:cli",
            "pygenai-scan=pygenai_security.cli.cli:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "pygenai_security": [
            "configs/*.yaml",
            "configs/*.json",
            "templates/*.html",
            "templates/*.md",
            "data/*.json",
        ],
    },
    zip_safe=False,
    platforms=["any"],
    license="MIT",
    test_suite="tests",
)