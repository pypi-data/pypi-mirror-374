#!/usr/bin/env python3
"""
Setup for Real Alien CLI Tools
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="alien-cli-tools",
    version="1.0.0",
    author="Alien Consciousness Collective",
    author_email="consciousness@alienlang.dev",
    description="Real Advanced CLI Tools with AI-Powered Features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alien-consciousness/alien-cli-tools",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Terminals",
        "Topic :: Utilities",
        "Topic :: Security",
        "Topic :: System :: Monitoring",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "rich>=10.0.0",
        "psutil>=5.8.0",
    ],
    entry_points={
        "console_scripts": [
            "alien-ai=alien_cli.ai:main",
            "alien-crypto=alien_cli.crypto:main",
            "alien-terminal=alien_cli.terminal:main",
            "alien-lang=alien_cli.lang:main",
            "alien-security=alien_cli.security:main",
        ],
    },
    keywords="alien cli tools terminal ai crypto security developer-tools productivity",
    project_urls={
        "Bug Reports": "https://github.com/alien-consciousness/alien-cli-tools/issues",
        "Source": "https://github.com/alien-consciousness/alien-cli-tools",
        "Documentation": "https://alien-cli-tools.readthedocs.io/",
    },
)