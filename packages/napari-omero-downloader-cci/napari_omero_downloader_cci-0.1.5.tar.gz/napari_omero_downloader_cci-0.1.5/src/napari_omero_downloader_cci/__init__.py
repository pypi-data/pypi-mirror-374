try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

from .omero_downloader_widget import OmeroDownloaderWidget

__all__ = ["OmeroDownloaderWidget"]
