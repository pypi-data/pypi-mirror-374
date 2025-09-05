"""
Created on Wed Sep  3 16:10:24 2025

@author: simon
"""

# tools/run_pytest.py
import os
import sys

import pytest

ARGS = [
    "-v",
    "--color=yes",
    "--cov=napari_omero_downloader_cci",
    "--cov-report=xml",
]

rc = pytest.main(ARGS)

# If tests failed, propagate real failure.
if rc != 0:
    sys.exit(rc)

# If tests succeeded, avoid Python/Qt/Ice teardown — exit immediately.
os._exit(0)
