"""
Kepler-Downloader-DR25
A comprehensive toolkit for downloading and filtering Kepler DR25 FITS files from NASA's MAST archive.
"""

from ._version import __version__

__author__ = "akira921x"
__email__ = "noreply@use-github-issues.com"

from .downloader import main as download_main
from .filter import main as filter_main

__all__ = ["__version__", "download_main", "filter_main"]