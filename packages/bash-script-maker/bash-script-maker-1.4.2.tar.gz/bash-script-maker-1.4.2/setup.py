#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for Bash-Script-Maker
"""

from setuptools import setup
import os


# Read version from VERSION file
def read_version():
    version_file = os.path.join(os.path.dirname(__file__), "VERSION")
    if os.path.exists(version_file):
        with open(version_file, "r", encoding="utf-8") as f:
            return f.read().strip()
    return "0.1.0"


# Read README for long description
def read_readme():
    readme_file = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_file):
        with open(readme_file, "r", encoding="utf-8") as f:
            return f.read()
    return ""


# Read requirements
def read_requirements():
    req_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(req_file):
        with open(req_file, "r", encoding="utf-8") as f:
            return [
                line.strip() for line in f if line.strip() and not line.startswith("#")
            ]
    return []


VERSION = read_version()
LONG_DESCRIPTION = read_readme()
REQUIREMENTS = read_requirements()

setup(
    name="bash-script-maker",
    version=VERSION,
    author="Marcel Dellmann",
    author_email="support@secure-bits.org",
    description="Ein GUI-Programm zur Erstellung von Bash-Scripts mit visueller Unterstützung",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/securebitsorg/bash-script-maker",
    packages=[],
    py_modules=["bash_script_maker", "syntax_highlighter", "localization", "custom_dialogs", "assets"],
    include_package_data=True,
    install_requires=REQUIREMENTS,
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "flake8>=3.8.0",
            "black>=21.0.0",
            "mypy>=0.800",
            "tox>=3.20.0",
            "twine>=3.0.0",
            "build>=0.7.0",
            "bandit>=1.7.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "bash-script-maker=bash_script_maker:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Utilities",
        "Topic :: Text Editors :: Integrated Development Environments (IDE)",
        "Topic :: Software Development :: Code Generators",
    ],
    keywords="bash script gui editor generator linux",
    python_requires=">=3.8",
    project_urls={
        "Bug Reports": "https://github.com/securebitsorg/bash-script-maker/issues",
        "Source": "https://github.com/securebitsorg/bash-script-maker",
        "Documentation": "https://github.com/securebitsorg/bash-script-maker#readme",
        "Changelog": "https://github.com/securebitsorg/bash-script-maker/blob/main/CHANGELOG.md",
    },
)
