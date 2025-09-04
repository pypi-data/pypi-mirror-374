#!/usr/bin/env python3
"""
Setup script for WebOasis - A browser automation framework.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="weboasis",
    version="0.1.0",
    author="Siyang Liu",
    author_email="lsiyang@umich.edu",
    description="A web agent framework for researchers to build and study web agents for real-world applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/weboasis",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
    ],
    python_requires=">=3.10",
    install_requires=[
        "selenium>=4.0.0",
        "playwright>=1.30.0",
        "pyyaml>=6.0",
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0",
        "lxml>=4.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
    },
)
