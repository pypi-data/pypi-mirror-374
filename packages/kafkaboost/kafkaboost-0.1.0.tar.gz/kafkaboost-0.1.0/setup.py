#!/usr/bin/env python3
"""
Setup script for KafkaBoost package.
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements from requirements.txt if it exists
def read_requirements():
    requirements = []
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    return requirements

setup(
    name="kafkaboost",
    version="0.1.0",
    author="KafkaBoost Team",
    author_email="support@kafkaboost.com",
    description="Enhanced Apache Kafka library with priority-based message processing",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/kafkaboost",
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
        "Topic :: System :: Distributed Computing",
        "Topic :: System :: Networking",
    ],
    python_requires=">=3.7",
    install_requires=[
        "kafka-python>=2.0.0",
        "boto3>=1.26.0",
        "botocore>=1.29.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "pytest-cov>=3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "kafkaboost-test=kafkaboost.tests.test_priority_boost_kafka:main",
        ],
    },
    include_package_data=True,
    package_data={
        "kafkaboost": [
            "*.json",
            "tests/*.json",
        ],
    },
    keywords="kafka, priority, messaging, distributed, streaming, async",
    project_urls={
        "Bug Reports": "https://github.com/your-org/kafkaboost/issues",
        "Source": "https://github.com/your-org/kafkaboost",
        "Documentation": "https://kafkaboost.readthedocs.io/",
    },
)
