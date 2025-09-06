#!/usr/bin/env python3
"""
SimpleLinks - Secure Network SDK
A lightweight network connectivity solution based on secure HTTPS connections
"""

from setuptools import setup, find_packages
import os
import re

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

setup(
    name="simplelinks",
    version="2.0.5",
    author="SimpleLinks Team",
    author_email="contact@simplelinks.cn",
    description="A lightweight network connectivity solution based on secure HTTPS connections",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://simplelinks.cn",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: Proxy Servers",
        "Topic :: System :: Networking",
        "Topic :: Security",
    ],
    python_requires=">=3.7",
    install_requires=[
        "websockets>=10.0",
        "asyncio",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black",
            "flake8",
        ],
    },
    entry_points={
        "console_scripts": [
            "slink-server=simplelinks.cli:server_cli",
            "slink-client=simplelinks.cli:client_cli",
        ],
    },
    include_package_data=True,
    package_data={
        "simplelinks": ["*.md", "*.txt"],
    },
    zip_safe=False,
)
