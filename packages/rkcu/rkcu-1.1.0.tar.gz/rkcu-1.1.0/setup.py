#!/usr/bin/env python3
"""Setup script for RKCU package."""

from setuptools import setup, find_packages
import os


def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'readme.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""


def get_version():
    version_file = os.path.join(os.path.dirname(__file__), 'rkcu', '__init__.py')
    with open(version_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"\'')
    return "0.0.0"

setup(
    name="rkcu",
    version=get_version(),
    author="Hardik Srivastava",
    maintainer="Gagan Katla",
    description="Royal Kludge Config Utility - Manage profiles and per-key RGB lighting",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/gagan16k/rkcu",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Hardware",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=[
        "hidapi>=0.10.1",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "rkcu=rkcu.__main__:main",
        ],
    },
    keywords="royal kludge keyboard rgb lighting config utility",
    project_urls={
        "Bug Reports": "https://github.com/gagan16k/rkcu/issues",
        "Source": "https://github.com/gagan16k/rkcu",
    },
)
