# napari-omero-downloader-cci

[![License MIT](https://img.shields.io/pypi/l/napari-omero-downloader-cci.svg?color=green)](https://github.com/CCI-GU-Sweden/napari-omero-downloader-cci/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-omero-downloader-cci.svg?color=green)](https://pypi.org/project/napari-omero-downloader-cci)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-omero-downloader-cci.svg?color=green)](https://python.org)
[![tests](https://github.com/CCI-GU-Sweden/napari-omero-downloader-cci/workflows/tests/badge.svg)](https://github.com/CCI-GU-Sweden/napari-omero-downloader-cci/actions)
[![codecov](https://codecov.io/gh/CCI-GU-Sweden/napari-omero-downloader-cci/branch/main/graph/badge.svg)](https://codecov.io/gh/CCI-GU-Sweden/napari-omero-downloader-cci)
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/napari-omero-downloader-cci)](https://napari-hub.org/plugins/napari-omero-downloader-cci)
[![npe2](https://img.shields.io/badge/plugin-npe2-blue?link=https://napari.org/stable/plugins/index.html)](https://napari.org/stable/plugins/index.html)
[![Copier](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-purple.json)](https://github.com/copier-org/copier)

A plugin that allows napari to connect to the Omero CCI server to visualize and download image data

----------------------------------

This [napari] plugin was generated with [copier] using the [napari-plugin-template] (None).

## Installation

### First napari installation

First install miniconda from conda forge: [https://conda-forge.org/download/].

Recommanded, create an environment for napari, bundling both napari and omero

```
conda create -n napari -c conda-forge napari omero-py pyqt pyside2 --yes
conda activate napari
napari
```

### Already python installed napari

In this case, activate your environment and install Omero:

```
conda install -c conda-forge omero-py --yes
```

### Plugin installation

You can install `napari-omero-downloader-cci` via [pip]:

```
pip install napari-omero-downloader-cci
```

To install latest development version :

```
pip install git+https://github.com/CCI-GU-Sweden/napari-omero-downloader-cci.git
```

—or, during development—

```
pip install -e .
```

## Running the plugin after Installation

You will need to open the conda-forge preogram, then:

```
conda activate napari
napari
```

The plug will be in the plugin tab.

## Warning about standalone napari

A standalone version of napari is available, and the plugin will be available on the napari hub. However, installation through the standalone app is not recommanded, since it relies on pip which does not distribute system ready dependancy for Ice.


## Contributing

Contributions are very welcome. Tests can be run with [tox], please ensure
the coverage at least stays the same before you submit a pull request.

## License

Distributed under the terms of the [MIT] license,
"napari-omero-downloader-cci" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

[napari]: https://github.com/napari/napari
[copier]: https://copier.readthedocs.io/en/stable/
[@napari]: https://github.com/napari
[MIT]: http://opensource.org/licenses/MIT
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[GNU GPL v3.0]: http://www.gnu.org/licenses/gpl-3.0.txt
[GNU LGPL v3.0]: http://www.gnu.org/licenses/lgpl-3.0.txt
[Apache Software License 2.0]: http://www.apache.org/licenses/LICENSE-2.0
[Mozilla Public License 2.0]: https://www.mozilla.org/media/MPL/2.0/index.txt
[napari-plugin-template]: https://github.com/napari/napari-plugin-template

[file an issue]: https://github.com/CCI-GU-Sweden/napari-omero-downloader-cci/issues

[napari]: https://github.com/napari/napari
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/
