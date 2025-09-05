import napari

# Import your widget
from napari_omero_downloader_cci.omero_downloader_widget import (
    OmeroDownloaderWidget,
)


def test_widget_instantiates():
    """The widget should build without crashing."""
    viewer = napari.Viewer()
    widget = OmeroDownloaderWidget(viewer)
    assert widget is not None
    assert hasattr(widget, "connect_to_omero")  # basic API presence


def test_widget_added_to_viewer():
    """The widget can be docked into napari."""
    viewer = napari.Viewer()
    widget = OmeroDownloaderWidget(viewer)
    dock_widget = viewer.window.add_dock_widget(widget)
    assert dock_widget is not None
    assert widget in dock_widget.parent().findChildren(OmeroDownloaderWidget)


def test_download_path_empty(tmp_path):
    """Widget should start with no download path set."""
    viewer = napari.Viewer()
    widget = OmeroDownloaderWidget(viewer)
    assert widget.get_download_path() == ""
    # Set a path manually
    widget.path_edit.setText(str(tmp_path))
    assert widget.get_download_path() == str(tmp_path)
