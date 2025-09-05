"""
Created on Mon Sep  1 14:54:11 2025

@author: simon
"""

# omero_downloader_widget.py

import dask.array as da
import napari
import numpy as np
from dask import delayed
from qtpy.QtCore import Qt, QTimer
from qtpy.QtGui import QBrush, QColor, QPixmap
from qtpy.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .gui import (
    DownloadManager,
    DownloadProgressDialog,
    DownloadQueueTree,
    OmeroExplorerTree,
)

OMERO_TOKEN_URL = "https://omero-cci-users.gu.se/oauth/sessiontoken"
DEFAULT_HOST = "omero-cci-cli.gu.se"
DEFAULT_PORT = "4064"
FULL_SELECTION = QColor("#66CC66")
PARTIAL_SELECTION = QColor("#FF9566")


class OmeroDownloaderWidget(QWidget):
    def __init__(self, viewer: napari.Viewer):
        super().__init__()
        self.viewer = viewer
        self.conn = None
        self.connected = False
        self.busy = False

        # Initialize a timer for connection checks
        self.connection_timer = QTimer()
        self.connection_timer.setInterval(
            5000
        )  # Check every 5 seconds (adjust as needed)
        self.connection_timer.timeout.connect(self.check_connection)
        self.connection_timer.start()

        # Status icon
        self.status_icon = QLabel()

        # === Main layout ===
        main_layout = QVBoxLayout(self)

        # --- Login row ---
        login_layout = QHBoxLayout()

        link_label = QLabel(
            f'<a href="{OMERO_TOKEN_URL}">Get your key from OMERO</a>'
        )
        link_label.setOpenExternalLinks(True)
        login_layout.addWidget(link_label)

        login_layout.addWidget(QLabel("Key:"))
        self.key_edit = QLineEdit()
        self.key_edit.setFixedWidth(200)
        login_layout.addWidget(self.key_edit)

        self.login_btn = QPushButton("Connect")
        self.login_btn.clicked.connect(self.toggle_connection)
        login_layout.addWidget(self.login_btn)

        login_layout.addWidget(self.status_icon)

        main_layout.addLayout(login_layout)

        # --- Group and user selection ---
        self.group_toolbar = QHBoxLayout()

        self.group_combo = QComboBox()
        self.group_combo.setEnabled(False)
        self.group_combo.currentIndexChanged.connect(self._on_group_changed)
        self.group_toolbar.addWidget(QLabel("Group:"))
        self.group_toolbar.addWidget(self.group_combo)

        self.user_label = QLabel()
        self.group_toolbar.addWidget(self.user_label)

        self.user_combo = QComboBox()
        self.user_combo.setEnabled(False)
        self.user_combo.currentIndexChanged.connect(
            self._on_experimentor_changed
        )
        self.group_toolbar.addWidget(QLabel("  Data of:"))
        self.group_toolbar.addWidget(self.user_combo)

        self.fresh_btn = QPushButton("Refresh")
        self.fresh_btn.clicked.connect(self.refresh)
        self.group_toolbar.addWidget(self.fresh_btn)

        main_layout.addLayout(self.group_toolbar)

        # --- Tree views ---
        splitter = QSplitter(Qt.Horizontal)
        self.omero_tree = OmeroExplorerTree()
        self.download_tree = DownloadQueueTree()
        splitter.addWidget(self.omero_tree)
        splitter.addWidget(self.download_tree)
        main_layout.addWidget(splitter)

        # --- Bottom path + download ---
        bottom_layout = QHBoxLayout()
        self.visu_btn = QPushButton("Visualize")
        self.visu_btn.clicked.connect(self.on_visualize_clicked)
        self.visu_btn.setEnabled(False)
        bottom_layout.addWidget(self.visu_btn)

        bottom_layout.addWidget(QLabel("Download to:"))

        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Select download directory...")
        bottom_layout.addWidget(self.path_edit)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_download_path)
        bottom_layout.addWidget(browse_btn)

        bottom_layout.addStretch()

        self.download_btn = QPushButton("Download")
        self.download_btn.clicked.connect(self.download_files)
        self.download_btn.setEnabled(False)
        bottom_layout.addWidget(self.download_btn)

        main_layout.addLayout(bottom_layout)

        # --- Connect tree signals ---
        self.omero_tree.itemDoubleClickedToTransfer.connect(
            self.download_tree.add_omerohierarchy
        )
        self.omero_tree.itemDoubleClickedToTransfer.connect(
            self.update_omero_tree_highlight
        )
        self.download_tree.itemDoubleClickedToTransfer.connect(
            lambda item: QTimer.singleShot(0, self.update_omero_tree_highlight)
        )
        self.download_tree.model().rowsRemoved.connect(
            lambda parent, start, end: QTimer.singleShot(
                0, self.update_omero_tree_highlight
            )
        )
        # self.omero_tree.itemDoubleClicked.connect(self.on_tree_item_open)

        self.update_status_icon()

    # === Connection handling ===
    def toggle_connection(self):
        if not self.connected:
            self.connect_to_omero()
        else:
            self.disconnect_from_omero()

    def connect_to_omero(self):
        import Ice

        from . import omero_connection

        key = self.key_edit.text().strip()

        if not key:
            QMessageBox.warning(
                self, "Missing Info", "Please fill the key field."
            )
            return

        try:
            self.conn = omero_connection.OmeroConnection(
                DEFAULT_HOST, DEFAULT_PORT, key
            )
            self.download_tree.conn = self.conn
            self.connected = True
            self.login_btn.setText("Disconnect")
            self.visu_btn.setEnabled(True)
            self.download_btn.setEnabled(True)
            # QMessageBox.information(self, "Connected", "Successfully connected to OMERO.")
            self.update_status_icon()
            # self.user_name = self.conn.get_logged_in_user_name()
            self._update_groups_and_user()
            self.refresh()

        except Ice.Exception as e:
            QMessageBox.critical(self, "Connection Error", str(e))
            self.connected = False
            self.update_status_icon()

    def disconnect_from_omero(self):
        if self.conn:
            self.conn.kill_session()
        self.conn = None
        self.connected = False
        self.login_btn.setText("Connect")
        self.download_btn.setEnabled(False)
        self.visu_btn.setEnabled(False)
        self.update_status_icon()
        self.omero_tree.clear()
        self.download_tree.clear()
        self.download_tree._existing_projects = {}
        QMessageBox.information(
            self, "Disconnected", "Disconnected from OMERO."
        )

    def check_connection(self):
        import Ice

        try:
            if (
                not self.conn.is_connected()
                and not self.busy
                and not self.connected
            ):
                self.connected = False
                self.update_status_icon()
                QMessageBox.critical(
                    self, "Error", "Lost the connection to the Omero server."
                )
        except Ice.Exception as e:
            QMessageBox.critical(self, "Connection Error", str(e))
            self.connected = False
            self.update_status_icon()
        except AttributeError:  # in case that self.conn is None
            self.connected = False
            self.update_status_icon()

    def update_status_icon(self):
        if self.connected and not self.busy:
            pixmap = QPixmap(16, 16)
            pixmap.fill(Qt.green)
            self.status_icon.setPixmap(pixmap)
            self.status_icon.setToolTip("Connected")
        elif self.connected and self.busy:
            pixmap = QPixmap(16, 16)
            pixmap.fill(Qt.yellow)
            self.status_icon.setPixmap(pixmap)
            self.status_icon.setToolTip("Busy")
        else:
            pixmap = QPixmap(16, 16)
            pixmap.fill(Qt.red)
            self.status_icon.setPixmap(pixmap)
            self.status_icon.setToolTip("Disconnected")
            self.login_btn.setText("Connect")

    # === Populate tree ===
    def populate_full_tree(self):
        self.set_loading(True)
        self.tree_loader = self.populate_full_tree_generator()
        self.step_tree_loader()

    def populate_full_tree_generator(self):
        projects = self.conn.get_user_projects()
        for proj_id, proj_name in projects.items():
            proj_item = self._add_tree_item(
                self.omero_tree, "project", proj_id, proj_name
            )
            yield

            datasets = self.conn.get_dataset_from_projectID(proj_id)
            for ds_id, ds_name in datasets.items():
                ds_item = self._add_tree_item(
                    proj_item, "dataset", ds_id, ds_name
                )
                yield

                images = self.conn.get_images_from_datasetID(ds_id)
                for img_id, img_name in images.items():
                    self._add_tree_item(ds_item, "image", img_id, img_name)
                    yield

        # TODO. orphaned image
        # TODO - screen assay?

    def _add_tree_item(self, parent, node_type, node_id, text):
        item = QTreeWidgetItem(parent)
        item.setText(0, text)
        item.setData(0, 1, (node_type, node_id))
        return item

    def step_tree_loader(self):  # allows UI update
        try:
            next(self.tree_loader)
            QTimer.singleShot(0, self.step_tree_loader)
        except StopIteration:
            self.set_loading(False)

    def set_loading(self, is_loading):
        self.busy = is_loading
        self.update_status_icon()

    # === File browser ===
    def browse_download_path(self):
        directory = QFileDialog.getExistingDirectory(
            self, "Select Download Directory"
        )
        if directory:
            self.path_edit.setText(directory)

    def get_download_path(self):
        return self.path_edit.text()

    # === Download ===
    def download_files(self):
        download_path = self.get_download_path()
        if not download_path:
            QMessageBox.warning(
                self, "No Download Path", "Please select a download directory."
            )
            return

        self.progress_dialog = DownloadProgressDialog(self)
        self.progress_dialog.show()

        self.dm = DownloadManager(self.download_tree, self.conn, download_path)
        self.dm.progress_signals = self.progress_dialog

        self.generator = self.dm.download_files_generator()
        self.busy = True
        self.update_status_icon()
        self.step_download()

    def step_download(self):
        try:
            next(self.generator)
            QTimer.singleShot(0, self.step_download)
        except StopIteration:
            self.progress_dialog.close()
            self.download_tree.clear()
            self.download_tree._existing_projects = {}
            self.update_omero_tree_highlight()
            self.busy = False
            self.update_status_icon()

    # === Tree highlighting ===
    def update_omero_tree_highlight(self):
        # 1) gather all ids currently present in download_tree
        present = self._collect_download_ids()

        # 2) recurse the OMERO tree using the set
        for i in range(self.omero_tree.topLevelItemCount()):
            proj_item = self.omero_tree.topLevelItem(i)
            self._update_item_highlight_recursive(proj_item, present)

    def _collect_download_ids(self):
        """Return a set of all (type, id) pairs in the download tree."""
        seen = set()

        def gather(node):
            data = node.data(0, 1)
            if isinstance(data, tuple) and len(data) == 2:
                # normalize to strings to avoid int/str mismatches
                d_type, d_id = data
                seen.add((str(d_type), str(d_id)))
            for i in range(node.childCount()):
                gather(node.child(i))

        for i in range(self.download_tree.topLevelItemCount()):
            gather(self.download_tree.topLevelItem(i))
        return seen

    def _update_item_highlight_recursive(self, item, present):
        # leaf
        if item.childCount() == 0:
            o_type, o_id = item.data(0, 1) or (None, None)
            included = (str(o_type), str(o_id)) in present
            item.setBackground(0, FULL_SELECTION if included else QBrush())
            return _Tri.FULL if included else _Tri.NONE

        # internal: aggregate child states
        saw_full = saw_none = saw_partial = False
        for i in range(item.childCount()):
            st = self._update_item_highlight_recursive(item.child(i), present)
            if st == _Tri.FULL:
                saw_full = True
            elif st == _Tri.PARTIAL:
                saw_partial = True
            else:
                saw_none = True

        if saw_partial or (saw_full and saw_none):
            item.setBackground(0, PARTIAL_SELECTION)
            return _Tri.PARTIAL
        elif saw_full and not saw_none:
            item.setBackground(0, FULL_SELECTION)
            return _Tri.FULL
        else:
            item.setBackground(0, QBrush())
            return _Tri.NONE

    # === Omero group and user/experimenter selection ===
    def _update_groups_and_user(self):
        """Populate group combo and user label after login"""
        try:
            groups = self.conn.get_user_group()
            current_group = self.conn.getDefaultOmeroGroup()
            self.user_name = self.conn.get_logged_in_user_name()

            self.group_combo.blockSignals(True)
            self.group_combo.clear()
            self.group_combo.addItems(groups)

            if current_group in groups:
                index = groups.index(current_group)
                self.group_combo.setCurrentIndex(index)
            else:
                index = 0

            self.group_combo.blockSignals(False)
            # self.user_label.setText(f"  Logged in as: {self.user_name}")
            self.group_combo.setEnabled(True)
            self._on_group_changed(index)

        except AttributeError:
            self.user_label.setText("Not logged in")
            self.group_combo.setEnabled(False)

    def _on_group_changed(self, index):
        """Handle group selection changes"""
        import Ice

        group_name = self.group_combo.itemText(index)
        try:
            self.conn.setOmeroGroupName(group_name)
            self.load_experimentors()

            # Set experimentor combo to yourself
            self.user_combo.blockSignals(True)
            if self.user_name in self.members:
                user_index = list(self.members.keys()).index(self.user_name)
                self.user_combo.setCurrentIndex(user_index)
            self.user_combo.blockSignals(False)

            # Manually trigger experimentor change once
            self._on_experimentor_changed(self.user_combo.currentIndex())

            self.omero_tree.clear()
            self.download_tree.clear()
            self.download_tree._existing_projects = {}
            self.populate_full_tree()
        except (Ice.Exception, ValueError) as e:
            self.connected = False
            self.update_status_icon()
            QMessageBox.critical(
                self, "Error", f"Failed to switch groups: {str(e)}"
            )

    def load_experimentors(self):
        self.members = self.conn.get_members_of_group()
        self.user_combo.clear()
        for username in self.members:
            self.user_combo.addItem(username)
        self.user_combo.setEnabled(True)

    def _on_experimentor_changed(self, index):
        self.omero_tree.clear()
        self.download_tree.clear()
        self.download_tree._existing_projects = {}
        user_name = self.user_combo.itemText(index)
        if user_name == "":
            user_name = self.user_name
        self.conn.set_user(self.members[user_name])

        self.populate_full_tree()

    def refresh(self):
        if self.connected:
            self._on_experimentor_changed(self.user_combo.currentIndex())
            self.update_omero_tree_highlight()

    # === Show image in Napari ===
    def on_tree_item_open(self, item, column):  # double click code
        node_type, node_id = item.data(0, 1)
        if node_type == "image":
            self.open_in_napari(node_id, item.text(0))

    def on_visualize_clicked(self):
        item = self.omero_tree.currentItem()
        if item is None:
            QMessageBox.warning(
                self, "No selection", "Please select an item in the tree."
            )
            return

        node_type, node_id = item.data(0, 1)
        if node_type == "image":
            self.open_in_napari(node_id, item.text(0))
        else:
            QMessageBox.information(
                self, "Not an image", "Please select an image node."
            )

    def open_in_napari(self, image_id, image_name):
        self._clear_previous_images()

        loader = OmeroDaskLoader(self.conn, image_id)
        dask_img = loader.get_dask_array()

        self.viewer.add_image(
            dask_img,
            name=image_name,
            channel_axis=2,  # because shape is (T, Z, C, Y, X)
            contrast_limits=None,
            rgb=False,
        )

    def _clear_previous_images(self):
        self.viewer.layers.clear()


class OmeroDaskLoader:
    def __init__(self, conn, image_id):
        self.conn = conn
        self.image_id = image_id

        dims = conn.get_image_dims(image_id)
        self.size_z = dims["Z"]
        self.size_c = dims["C"]
        self.size_t = dims["T"]
        self.size_y = dims["Y"]
        self.size_x = dims["X"]

        self._dtype = np.float32

    def get_dask_array(self):

        def get_plane(t, z, c):
            plane = self.conn.load_plane_from_img_id(
                self.image_id, {"theT": int(t), "theZ": int(z), "theC": int(c)}
            )
            return np.asarray(plane, dtype=self._dtype)

        arrays = []
        for t in range(self.size_t):
            z_list = []
            for z in range(self.size_z):
                c_list = []
                for c in range(self.size_c):
                    # create a delayed task that returns an array of shape (1,1,1,Y,X)
                    delayed_block = delayed(get_plane)(
                        t, z, c
                    )  # returns (Y, X)
                    # wrap it so it has the extra dims we need
                    delayed_block = delayed(
                        lambda arr: arr[
                            np.newaxis, np.newaxis, np.newaxis, :, :
                        ]
                    )(delayed_block)
                    # now turn it into a proper dask.array chunk
                    arr = da.from_delayed(
                        delayed_block,
                        shape=(1, 1, 1, self.size_y, self.size_x),
                        dtype=self._dtype,
                    )
                    c_list.append(arr)
                z_list.append(da.concatenate(c_list, axis=2))
            arrays.append(da.concatenate(z_list, axis=1))
        full = da.concatenate(arrays, axis=0)
        return full


class _Tri:
    NONE = 0
    PARTIAL = 1
    FULL = 2


# === Register in Napari ===
if __name__ == "__main__":
    viewer = napari.Viewer()
    widget = OmeroDownloaderWidget(viewer)
    viewer.window.add_dock_widget(widget, area="right")
    napari.run()
