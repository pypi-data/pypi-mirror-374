#!/usr/bin/env python3
"""
Setup script for PromptLifter - LLM-powered contextual expansion.
"""

import os

from setuptools import find_packages, setup


# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()


# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [
            line.strip() for line in fh if line.strip() and not line.startswith("#")
        ]


setup(
    name="promptlifter",
    version="0.4.0",
    author="PromptLifter Team",
    author_email="promptlifter@thinkata.com",
    description="LLM-powered conversation interface with intelligent context management, real-time search integration, and seamless conversation flow",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Thinkata/promptlifter",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.9",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "promptlifter=promptlifter.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "promptlifter": ["*.yaml", "*.yml", "*.json"],
    },
    keywords="llm, conversation, ai, machine-learning, context-management, search, vector-search, chatbot, tavily, pinecone, ollama, openai, anthropic, real-time-search, conversation-flow",
    project_urls={
        "Bug Reports": "https://github.com/Thinkata/promptlifter/issues",
        "Source": "https://github.com/Thinkata/promptlifter",
        "Documentation": "https://github.com/Thinkata/promptlifter#readme",
    },
)
