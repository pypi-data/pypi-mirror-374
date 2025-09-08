#!/usr/bin/env python3
"""
Setup script for Capability Statement Form Generator
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="capability-statement-generator",
    version="1.0.0",
    author="Capability Statement Generator Team",
    author_email="developer@pharmatech.com",
    description="Automated form creation and data population for company capability statements",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/capability-statement-generator",
    packages=find_packages(),
    py_modules=["capability_statement_generator"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "capability-statement=capability_statement_generator:main",
        ],
    },
    keywords="capability statement, business documents, form generator, automation, json export",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/capability-statement-generator/issues",
        "Source": "https://github.com/yourusername/capability-statement-generator",
        "Documentation": "https://github.com/yourusername/capability-statement-generator#readme",
    },
)
