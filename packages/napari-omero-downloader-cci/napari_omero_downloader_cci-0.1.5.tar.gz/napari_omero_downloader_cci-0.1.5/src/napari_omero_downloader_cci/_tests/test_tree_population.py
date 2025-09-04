"""
Created on Wed Sep  3 09:27:08 2025

@author: simon
"""

import sys
from unittest.mock import MagicMock

import pytest
from qtpy.QtCore import QTimer

from napari_omero_downloader_cci.omero_downloader_widget import (
    OmeroDownloaderWidget,
)

pytestmark = pytest.mark.skipif(
    sys.platform == "darwin", reason="flaky QTimer teardown on macOS CI"
)


@pytest.fixture(autouse=True)
def instant_single_shot(monkeypatch):
    """
    Replace QTimer.singleShot so it'll call the function immediately,
    effectively draining the generator in one go.
    """
    monkeypatch.setattr(QTimer, "singleShot", lambda interval, func: func())


def test_populate_full_tree_with_generator_and_timer(make_napari_viewer):
    # 1) Set up viewer and widget
    viewer = make_napari_viewer()
    widget = OmeroDownloaderWidget(viewer)

    # 2) Mock the connection and fake hierarchy
    mock_conn = MagicMock()
    widget.conn = mock_conn
    mock_conn.get_user_projects.return_value = {1: "P"}
    mock_conn.get_dataset_from_projectID.return_value = {10: "D"}
    mock_conn.get_images_from_datasetID.return_value = {100: "I1", 101: "I2"}

    # 3) Kick off the load; with singleShot patched this will run to completion
    widget.populate_full_tree()

    # 4) Verify the tree got populated
    assert widget.omero_tree.topLevelItemCount() == 1
    proj = widget.omero_tree.topLevelItem(0)
    assert proj.text(0) == "P"

    ds = proj.child(0)
    assert ds.text(0) == "D"

    images = sorted(ds.child(i).text(0) for i in range(ds.childCount()))
    assert images == ["I1", "I2"]
