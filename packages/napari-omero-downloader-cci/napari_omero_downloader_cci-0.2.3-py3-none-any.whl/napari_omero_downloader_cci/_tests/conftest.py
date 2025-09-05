"""
Created on Wed Sep  3 09:21:28 2025

@author: simon
"""

# src/napari_omero_downloader_cci/_tests/conftest.py
import sys
import types


def pytest_configure(config):
    """Provide fake omero + Ice modules if they aren't installed."""
    if "omero" not in sys.modules:
        fake_omero = types.ModuleType("omero")
        fake_omero.ApiUsageException = Exception  # stub
        sys.modules["omero"] = fake_omero

    if "Ice" not in sys.modules:
        fake_ice = types.ModuleType("Ice")
        sys.modules["Ice"] = fake_ice
