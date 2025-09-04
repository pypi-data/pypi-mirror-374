"""
Created on Wed Sep  3 10:20:57 2025

@author: simon
"""

from unittest.mock import MagicMock, call

import dask.array as da
import numpy as np
import pytest

from napari_omero_downloader_cci.omero_downloader_widget import OmeroDaskLoader


@pytest.fixture
def fake_plane():
    # produce a reproducible 2×3 plane
    return np.arange(2 * 3, dtype=np.float32).reshape(2, 3)


@pytest.fixture
def mock_conn(fake_plane):
    conn = MagicMock()
    # define image dimensions: T=2, Z=1, C=1, Y=2, X=3
    conn.get_image_dims.return_value = {"T": 2, "Z": 1, "C": 1, "Y": 2, "X": 3}
    # load_plane… returns our 2×3 plane regardless of indices
    conn.load_plane_from_img_id.return_value = fake_plane
    return conn


def test_daskarray_shape_and_dtype(mock_conn):
    loader = OmeroDaskLoader(mock_conn, image_id=42)
    darr = loader.get_dask_array()

    # It should be a dask Array with the right shape and dtype
    assert isinstance(darr, da.Array)
    assert darr.shape == (2, 1, 1, 2, 3)
    assert darr.dtype == np.float32


def test_daskarray_triggers_loads(mock_conn):
    loader = OmeroDaskLoader(mock_conn, image_id=99)
    darr = loader.get_dask_array()

    # Compute just the first timepoint, Z=0, C=0 slice
    # Result shape should collapse the leading singleton dims to (1,1,1,2,3)
    sub = darr[0, 0, 0, :, :].compute()
    # Dask will tile our fake_plane along the requested axes
    expected = mock_conn.load_plane_from_img_id.return_value
    assert np.array_equal(sub, expected)

    # Verify load_plane was called exactly for (t=0,z=0,c=0)
    # and for (t=1,z=0,c=0) if we compute the second timepoint
    # Let’s trigger the second slice to force the second load
    _ = darr[1, 0, 0, :, :].compute()

    # We expect two calls in total
    assert mock_conn.load_plane_from_img_id.call_count == 2
    # Check that the calls had the correct parameters
    mock_conn.load_plane_from_img_id.assert_has_calls(
        [
            call(99, {"theT": 0, "theZ": 0, "theC": 0}),
            call(99, {"theT": 1, "theZ": 0, "theC": 0}),
        ],
        any_order=False,
    )
