#!/usr/bin/env python3

import os

from setuptools import find_packages, setup


# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="legacy-cobol-modernization",
    version="1.0.2",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python implementation of a COBOL accounting system with Golden Master testing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/math974/modernize-legacy-cobol-app",
    packages=find_packages(),
    py_modules=["main"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial :: Accounting",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies for the main application
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "ruff>=0.1.0",
            "black>=23.0.0",
            "mypy>=1.5.0",
        ],
        "test": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "legacy-accounting=main:main",
            "cobol-accounting=main:main",
        ],
    },
    keywords=[
        "cobol",
        "legacy",
        "modernization",
        "golden-master",
        "testing",
        "accounting",
        "migration",
        "python",
    ],
    project_urls={
        "Bug Reports": "https://github.com/math974/modernize-legacy-cobol-app/issues",
        "Source": "https://github.com/math974/modernize-legacy-cobol-app",
        "Documentation": "https://github.com/math974/modernize-legacy-cobol-app#readme",
    },
    include_package_data=True,
    zip_safe=False,
)
