"""
Created on Thu May 15 15:06:43 2025

@author: simon
"""

from pathlib import Path

from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import (
    QDialog,
    QProgressBar,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
)


class OmeroExplorerTree(QTreeWidget):
    itemDoubleClickedToTransfer = Signal(QTreeWidgetItem)  # Custom signal

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(1)
        self.setHeaderLabels(["OMERO Data"])
        self.itemDoubleClicked.connect(self._emit_double_clicked_item)

    def _emit_double_clicked_item(self, item):
        self.itemDoubleClickedToTransfer.emit(item)


class DownloadQueueTree(QTreeWidget):
    itemDoubleClickedToTransfer = Signal(QTreeWidgetItem)  # Custom signal

    def __init__(self, parent=None, conn=None):
        super().__init__(parent)
        self.conn = conn
        self.setColumnCount(1)
        self.setHeaderLabels(["Download Queue"])
        self._existing_projects = {}  # {project_id: QTreeWidgetItem}
        self.itemDoubleClicked.connect(self.remove_from_download_tree)

    def remove_from_download_tree(self, item, column):
        parent = item.parent()
        node_type, node_id = item.data(0, 1)
        if parent is None:
            self.takeTopLevelItem(self.indexOfTopLevelItem(item))
            if node_type == "project" and node_id in self._existing_projects:
                del self._existing_projects[node_id]
        else:
            parent.removeChild(item)

        self.itemDoubleClickedToTransfer.emit(item)

    def add_omerohierarchy(self, omero_item):
        hierarchy = self._get_full_hierarchy(omero_item)
        for project_id, project_data in hierarchy.items():
            if project_id in self._existing_projects:
                project_node = self._existing_projects[project_id]
            else:
                project_node = QTreeWidgetItem(self)
                project_node.setText(0, project_data["name"])
                project_node.setData(0, 1, ("project", project_id))
                self._existing_projects[project_id] = project_node

            for dataset_id, dataset_data in project_data["datasets"].items():
                dataset_node = self._find_or_add_child(
                    project_node, "dataset", dataset_id, dataset_data["name"]
                )
                for image_id, image_name in dataset_data["images"].items():
                    folder_name = self.conn.get_original_upload_folder(
                        image_id
                    )
                    if folder_name and folder_name.lower() != "uploads":
                        folder_node = self._find_or_add_child(
                            dataset_node, "folder", folder_name, folder_name
                        )
                        self._find_or_add_child(
                            folder_node, "image", image_id, image_name
                        )
                    else:
                        self._find_or_add_child(
                            dataset_node, "image", image_id, image_name
                        )

    def _find_or_add_child(self, parent, node_type, node_id, node_name):
        # node_id can be str for folder, int for others
        for i in range(parent.childCount()):
            child = parent.child(i)
            data = child.data(0, 1)
            if data and data[0] == node_type and data[1] == node_id:
                return child
        child = QTreeWidgetItem(parent)
        child.setText(0, node_name)
        child.setData(0, 1, (node_type, node_id))
        return child

    def _get_full_hierarchy(self, item):
        """Returns hierarchical data for the clicked item and its parents"""
        hierarchy = {}
        current_item = item

        # Traverse up to project level
        while current_item:
            node_type, node_id = current_item.data(0, 1)

            if node_type == "project":
                hierarchy[node_id] = {
                    "name": current_item.text(0),
                    "datasets": self._get_child_datasets(current_item),
                }
                break
            elif node_type == "dataset":
                parent_project = self._find_parent_project(current_item)
                if parent_project:
                    project_id = parent_project.data(0, 1)[1]
                    hierarchy[project_id] = {
                        "name": parent_project.text(0),
                        "datasets": {
                            node_id: {
                                "name": current_item.text(0),
                                "images": self._get_child_images(current_item),
                            }
                        },
                    }
                break
            elif node_type == "image":
                parent_dataset = self._find_parent_dataset(current_item)
                parent_project = self._find_parent_project(parent_dataset)
                if parent_dataset and parent_project:
                    project_id = parent_project.data(0, 1)[1]
                    dataset_id = parent_dataset.data(0, 1)[1]
                    hierarchy[project_id] = {
                        "name": parent_project.text(0),
                        "datasets": {
                            dataset_id: {
                                "name": parent_dataset.text(0),
                                "images": {node_id: current_item.text(0)},
                            }
                        },
                    }
                break
            current_item = current_item.parent()
        return hierarchy

    def _add_dataset(self, project_node, dataset_id, dataset_data):
        """Add dataset to project node if not already present"""
        for i in range(project_node.childCount()):
            existing_dataset = project_node.child(i)
            if existing_dataset.data(0, 1)[1] == dataset_id:
                return  # Dataset already exists

        dataset_node = QTreeWidgetItem(project_node)
        dataset_node.setText(0, dataset_data["name"])
        dataset_node.setData(0, 1, ("dataset", dataset_id))

        for image_id, image_name in dataset_data["images"].items():
            image_node = QTreeWidgetItem(dataset_node)
            image_node.setText(0, image_name)
            image_node.setData(0, 1, ("image", image_id))

    # Helper functions
    def _find_parent_project(self, item):
        while item:
            data = item.data(0, 1)
            if data is not None and data[0] == "project":
                return item
            item = item.parent()
        return None

    def _find_parent_dataset(self, item):
        while item:
            data = item.data(0, 1)
            if data is not None and data[0] == "dataset":
                return item
            item = item.parent()
        return None

    def _get_child_datasets(self, project_item):
        datasets = {}
        for i in range(project_item.childCount()):
            dataset_item = project_item.child(i)
            dataset_id = dataset_item.data(0, 1)[1]
            datasets[dataset_id] = {
                "name": dataset_item.text(0),
                "images": self._get_child_images(dataset_item),
            }
        return datasets

    def _get_child_images(self, dataset_item):
        images = {}
        for i in range(dataset_item.childCount()):
            image_item = dataset_item.child(i)
            image_id = image_item.data(0, 1)[1]
            images[image_id] = image_item.text(0)
        return images


class DownloadManager:
    def __init__(self, download_tree, conn, base_path):
        self.download_tree = download_tree
        self.conn = conn
        self.base_path = Path(base_path)
        self.downloaded_filesets = set()  # Track downloaded fileset IDs
        self.progress_signals = None

    def update_overall_progress(self, current, total):
        if self.progress_signals:
            self.progress_signals.set_overall_max(total)
            self.progress_signals.set_overall_value(current)

    def update_file_progress(self, current, total):
        if self.progress_signals:
            self.progress_signals.set_file_max(total)
            self.progress_signals.set_file_value(current)

    def _collect_fileset_ids(self):
        fileset_set = set()
        for i in range(self.download_tree.topLevelItemCount()):
            project_item = self.download_tree.topLevelItem(i)
            for j in range(project_item.childCount()):
                dataset_item = project_item.child(j)
                for k in range(dataset_item.childCount()):
                    child_item = dataset_item.child(k)
                    if child_item is None:
                        continue
                    data = child_item.data(0, 1)
                    if data is None:
                        continue
                    node_type, node_id = data
                    if node_type == "folder":
                        for child_idx in range(child_item.childCount()):
                            image_item = child_item.child(child_idx)
                            if image_item is None:
                                continue
                            image_data = image_item.data(0, 1)
                            if image_data is None:
                                continue
                            node_type, image_id = image_data
                            fileset = self.conn.get_fileset_from_imageID(
                                image_id
                            )
                            if fileset:
                                fileset_set.add(fileset.getId())
                    elif node_type == "image":
                        image_id = node_id
                        fileset = self.conn.get_fileset_from_imageID(image_id)
                        if fileset:
                            fileset_set.add(fileset.getId())
        return list(fileset_set)

    def download_files_generator(self):
        if not self.base_path.exists():
            self.base_path.mkdir(parents=True, exist_ok=True)

        all_fileset_ids = self._collect_fileset_ids()
        self.total_files = len(all_fileset_ids)
        self.files_downloaded = 0
        self.update_overall_progress(self.files_downloaded, self.total_files)

        for i in range(self.download_tree.topLevelItemCount()):
            project_item = self.download_tree.topLevelItem(i)
            yield from self._download_project_generator(
                project_item, self.base_path
            )

        yield "done"

    def _download_project_generator(self, project_item, current_path):
        project_name = project_item.text(0)
        project_path = current_path / project_name
        project_path.mkdir(exist_ok=True)

        for i in range(project_item.childCount()):
            dataset_item = project_item.child(i)
            yield from self._download_dataset_generator(
                dataset_item, project_path
            )

    def _download_dataset_generator(self, dataset_item, current_path):
        dataset_name = dataset_item.text(0)
        dataset_path = current_path / dataset_name
        dataset_path.mkdir(exist_ok=True)

        for i in range(dataset_item.childCount()):
            child_item = dataset_item.child(i)
            node_type, node_id = child_item.data(0, 1)
            if node_type == "folder":
                folder_name = child_item.text(0)
                folder_path = dataset_path / folder_name
                folder_path.mkdir(exist_ok=True)
                for j in range(child_item.childCount()):
                    image_item = child_item.child(j)
                    yield from self._download_image_generator(
                        image_item, folder_path
                    )
            elif node_type == "image":
                yield from self._download_image_generator(
                    child_item, dataset_path
                )

    def _download_image_generator(self, image_item, current_path):
        image_name = image_item.text(0)
        node_type, image_id = image_item.data(0, 1)

        fileset = self.conn.get_fileset_from_imageID(image_id)
        if fileset is None:
            print(f"No fileset for image {image_name} (ID: {image_id})")
            return

        fileset_id = fileset.getId()
        if fileset_id in self.downloaded_filesets:
            return

        for orig_file in fileset.listFiles():
            file_name = orig_file.getName()
            file_path = current_path / file_name
            file_size = orig_file.getSize()
            self.update_file_progress(0, file_size)

            with open(file_path, "wb") as f:
                bytes_written = 0
                for chunk in orig_file.getFileInChunks():
                    f.write(chunk)
                    bytes_written += len(chunk)
                    self.update_file_progress(bytes_written, file_size)
                    yield

            self.downloaded_filesets.add(fileset_id)
            self.files_downloaded += 1
            self.update_overall_progress(
                self.files_downloaded, self.total_files
            )
            yield


class DownloadProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Download Progress")
        self.setWindowModality(Qt.ApplicationModal)  # Modal window
        self.setFixedSize(400, 120)

        self.overall_progress = QProgressBar()
        self.overall_progress.setFormat("Overall Progress: %v/%m files")
        self.overall_progress.setAlignment(Qt.AlignCenter)

        self.file_progress = QProgressBar()
        self.file_progress.setFormat("Current File Progress: %p%")
        self.file_progress.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.overall_progress)
        layout.addWidget(self.file_progress)
        self.setLayout(layout)

    def set_overall_max(self, max_files):
        self.overall_progress.setMaximum(max_files)

    def set_overall_value(self, value):
        self.overall_progress.setValue(value)

    def set_file_max(self, max_bytes):
        self.file_progress.setMaximum(max_bytes)

    def set_file_value(self, value):
        self.file_progress.setValue(value)
