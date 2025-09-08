"""Basic tests for kepler-downloader-dr25"""

import os
import sys

# Add the parent directory to the path to import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_import():
    """Test that the package can be imported"""
    import kepler_downloader_dr25

    assert kepler_downloader_dr25.__version__


def test_version_format():
    """Test that version follows semantic versioning"""
    from kepler_downloader_dr25 import __version__

    parts = __version__.split(".")
    assert len(parts) == 3  # Major.Minor.Patch
    for part in parts:
        assert part.isdigit()  # Each part should be a number
