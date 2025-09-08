#!/usr/bin/env python3
"""
Setup script for Kepler-Downloader-DR25
"""

import os
import sys

from setuptools import find_packages, setup

# Add the package directory to path to import version
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "kepler_downloader_dr25"))
from _version import __version__

# Read the README file
with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="kepler-downloader-dr25",
    version=__version__,
    author="akira921x",
    author_email="noreply@use-github-issues.com",
    description="A comprehensive toolkit for downloading and filtering Kepler DR25 FITS files from NASA's MAST archive",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/akira921x/Kepler-Downloader-DR25",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Astronomy",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "kepler-download=kepler_downloader_dr25.downloader:main",
            "kepler-filter=kepler_downloader_dr25.filter:main",
            "kepler-rebuild-db=kepler_downloader_dr25.utils.rebuild_database:main",
            "kepler-check-missing=kepler_downloader_dr25.utils.check_missing_kics:main",
            "kepler-stats=kepler_downloader_dr25.utils.generate_stats:main",
        ],
    },
    include_package_data=True,
    package_data={
        "kepler_downloader_dr25": ["*.md", "*.txt"],
    },
    project_urls={
        "Bug Reports": "https://github.com/akira921x/Kepler-Downloader-DR25/issues",
        "Source": "https://github.com/akira921x/Kepler-Downloader-DR25",
        "Documentation": "https://github.com/akira921x/Kepler-Downloader-DR25/blob/main/README.md",
    },
    keywords="kepler nasa astronomy exoplanet fits mast telescope space data download",
)
