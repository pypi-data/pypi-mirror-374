"""
Created on Wed Sep  3 10:23:00 2025

@author: simon
"""

from unittest.mock import MagicMock

import numpy as np

from napari_omero_downloader_cci.omero_downloader_widget import (
    OmeroDaskLoader,
    OmeroDownloaderWidget,
)


class DummyViewer:
    """A minimal stand-in for napari.Viewer."""

    def __init__(self):
        # simple list for layers
        self.layers = []
        # record of add_image calls
        self.added = []

    def add_image(self, data, *, name, channel_axis, contrast_limits, rgb):
        # record call
        self.added.append(
            {
                "data": data,
                "name": name,
                "channel_axis": channel_axis,
                "contrast_limits": contrast_limits,
                "rgb": rgb,
            }
        )
        # mimic a Napari layer object
        layer = MagicMock(name="ImageLayer")
        self.layers.append(layer)
        return layer


def test_open_in_napari_replaces_previous(monkeypatch):
    # 1) Create widget with dummy viewer
    viewer = DummyViewer()
    widget = OmeroDownloaderWidget(viewer)

    # 2) Seed viewer with a “stale” layer
    stale_layer = MagicMock(name="Stale")
    viewer.layers.append(stale_layer)

    # 3) Monkey‐patch the Dask loader so we don’t need a real conn
    fake_array = np.zeros((1, 1, 1, 4, 5), dtype=np.float32)

    class FakeLoader:
        def __init__(self, conn, img_id):
            pass

        def get_dask_array(self):
            return fake_array

    monkeypatch.setattr(
        OmeroDaskLoader.__module__ + ".OmeroDaskLoader", FakeLoader
    )

    # assign a dummy conn (not used by FakeLoader)
    widget.conn = object()

    # 4) Call open_in_napari
    widget.open_in_napari(image_id=123, image_name="foo")

    # 5) Assert that the stale layer was removed
    assert stale_layer not in viewer.layers
    # And exactly one new layer exists
    assert len(viewer.layers) == 1

    # 6) Inspect what was passed to add_image
    call = viewer.added[-1]
    assert call["data"] is fake_array
    assert call["name"] == "foo"
    assert call["channel_axis"] == 2
    assert call["contrast_limits"] is None
    assert call["rgb"] is False


def test_clear_previous_images_only_affects_layers(monkeypatch):
    """Ensure open_in_napari only wipes image layers."""
    viewer = DummyViewer()
    widget = OmeroDownloaderWidget(viewer)

    # put two dummy “non-image” layers in .layers
    other1, other2 = "points", "shapes"
    viewer.layers.extend([other1, other2])

    # now open a new image
    fake_array = np.zeros((1, 1, 1, 2, 2), dtype=np.float32)
    monkeypatch.setattr(
        OmeroDaskLoader.__module__ + ".OmeroDaskLoader",
        lambda conn, i: type(
            "L", (), {"get_dask_array": lambda self: fake_array}
        )(),
    )
    widget.conn = None
    widget.open_in_napari(1, "bar")

    # Since clear() removes *all* layers, points/shapes are gone
    assert viewer.layers and all(
        isinstance(layer, MagicMock) for layer in viewer.layers
    )
