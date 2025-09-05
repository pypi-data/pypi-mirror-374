#!/usr/bin/env python3
"""
Setup script for HashID - Comprehensive Hash and Token Analyzer
"""

from setuptools import setup, find_packages
import os

# Read the README file for the long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# Read requirements from requirements.txt if it exists
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return ['requests>=2.25.0']

setup(
    name="hashid-analyzer",
    version="2.0.0",
    author="XPAlchemnist",
    author_email="xpalchemnist@gmail.com",
    description="Comprehensive hash and token analyzer with persistent mode for security professionals",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/ninxp07/hash-id",
    project_urls={
        "Bug Tracker": "https://github.com/ninxp07/hash-id/issues",
        "Source Code": "https://github.com/ninxp07/hash-id",
        "Documentation": "https://github.com/ninxp07/hash-id#readme",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Topic :: Security",
        "Topic :: Security :: Cryptography",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'black>=21.0',
            'flake8>=3.8',
            'mypy>=0.812',
        ],
        'full': [
            'bcrypt>=3.2.0',
            'PyJWT>=2.0.0',
        ]
    },
    entry_points={
        'console_scripts': [
            'hashid=hashid.cli.main:main',
            'hash-analyzer=hashid.cli.main:main',
            'hash-id=hashid.cli.main:main',
        ],
    },
    keywords=[
        'hash', 'analyzer', 'identification', 'security', 'cryptography',
        'md5', 'sha1', 'sha256', 'sha512', 'ntlm', 'jwt', 'token',
        'bcrypt', 'scrypt', 'pbkdf2', 'cryptocurrency', 'bitcoin',
        'ethereum', 'penetration-testing', 'red-team', 'blue-team',
        'cybersecurity', 'forensics', 'malware-analysis'
    ],
    include_package_data=True,
    zip_safe=False,
)