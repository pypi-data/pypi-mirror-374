#!/usr/bin/env python3
"""
SubForge - AI-Powered Subagent Factory for Claude Code
Setup configuration for pip installation

Created: 2025-09-02 19:55 UTC-3 São Paulo
"""

from pathlib import Path

from setuptools import find_packages, setup

# Read the README for long description
here = Path(__file__).parent.absolute()
long_description = (here / "README.md").read_text(encoding="utf-8")

# Read version from package
version_file = here / "subforge" / "__init__.py"
version = None
for line in version_file.read_text().splitlines():
    if line.startswith("__version__"):
        version = line.split('"')[1]
        break

if not version:
    raise RuntimeError("Unable to find version string")

setup(
    name="subforge",
    version=version,
    author="SubForge Contributors",
    author_email="",
    description="AI-powered subagent factory for Claude Code developers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FAL1989/subforge",
    project_urls={
        "Bug Reports": "https://github.com/FAL1989/subforge/issues",
        "Source": "https://github.com/FAL1989/subforge",
        "Documentation": "https://github.com/FAL1989/subforge#readme",
    },
    packages=find_packages(exclude=["tests*", "docs*", "subforge-dashboard*"]),
    package_data={
        "subforge": [
            "templates/*.md",
            "templates/**/*.md",
            "templates/**/**/*.md",
        ],
    },
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        # Core dependencies are all built-in to Python 3.8+
        # No required external dependencies for basic functionality
    ],
    extras_require={
        "rich": [
            "typer>=0.9.0",
            "rich>=13.0.0",
        ],
        "dev": [
            "flake8>=6.0.0",
            "black>=23.0.0",
            "autopep8>=2.0.0",
            "ruff>=0.1.0",
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "isort>=5.12.0",
            "autoflake>=2.0.0",
        ],
        "full": [
            "typer>=0.9.0",
            "rich>=13.0.0",
            "flake8>=6.0.0",
            "black>=23.0.0",
            "autopep8>=2.0.0",
            "ruff>=0.1.0",
            "isort>=5.12.0",
            "autoflake>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "subforge=subforge.simple_cli:main",
            "subforge-rich=subforge.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Framework :: AsyncIO",
    ],
    keywords="claude ai subagents automation development tools cli",
    zip_safe=False,
)