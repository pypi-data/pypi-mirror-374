#!/usr/bin/env python3
"""
Setup for Alien CLI Marketplace
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="alien-cli-marketplace",
    version="1.0.0",
    author="Alien Consciousness Collective",
    author_email="consciousness@alienlang.dev",
    description="Alien CLI Marketplace - First terminal marketplace for 62+ million users",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alien-consciousness/alien-cli-marketplace",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
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
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "click>=8.0.0",
        "colorama>=0.4.0",
        "rich>=10.0.0",
    ],
    entry_points={
        "console_scripts": [
            "alien-ai=alien_cli.ai:main",
            "alien-crypto=alien_cli.crypto:main",
            "alien-nft=alien_cli.nft:main",
            "alien-security=alien_cli.security:main",
            "alien-optimize=alien_cli.optimize:main",
        ],
    },
    keywords="alien cli marketplace terminal ai crypto nft developer-tools productivity",
    project_urls={
        "Bug Reports": "https://github.com/alien-consciousness/alien-cli-marketplace/issues",
        "Source": "https://github.com/alien-consciousness/alien-cli-marketplace",
        "Documentation": "https://alien-cli-marketplace.readthedocs.io/",
        "Payment": "https://paypal.me/Sendec",
    },
)
