"""
Created on Thu May 15 15:29:18 2025

@author: simon

"""

import numpy as np


class OmeroConnection:

    def __init__(self, hostname, port, token):

        self._connect_to_omero(hostname, port, token)

    def __del__(self):
        self._close_omero_connection()

    def kill_session(self):
        self._close_omero_connection(True)

    def get_omero_connection(self):
        return self.conn

    def _connect_to_omero(self, hostname, port, token):
        from omero.gateway import BlitzGateway

        self.omero_token = token

        self.conn = BlitzGateway(host=hostname, port=port)
        is_connected = self.conn.connect(token)

        if not is_connected:
            raise ConnectionError("Failed to connect to OMERO")

    def _close_omero_connection(self, hardClose=False):
        if self.conn:
            self.conn.close(hard=hardClose)

    def get_user(self):
        return self.conn.getUser()

    def get_logged_in_user_name(self):
        return self.conn.getUser().getFullName()

    def get_user_group(self):
        groups = []
        for group in self.conn.getGroupsMemberOf():
            groups.append(group.getName())
        return groups

    def getDefaultOmeroGroup(self):
        group = self.conn.getGroupFromContext()
        return group.getName()

    def setOmeroGroupName(self, group):
        self.conn.setGroupNameForSession(group)

    def get_user_projects(self):
        projects = {}
        my_expId = self.conn.getUser().getId()
        for project in self.conn.listProjects(
            my_expId
        ):  # Initially we just load Projects
            projects.update({project.getId(): project.getName()})

        return projects

    def get_dataset_from_projectID(self, project_id):
        project = self.conn.getObject("Project", project_id)
        if not project:
            raise Exception(f"Project with ID {project_id} not found")

        datasets = {}
        for dataset in project.listChildren():  # lazy-loading of Datasets here
            datasets.update({dataset.getId(): dataset.getName()})

        return datasets

    def get_images_from_datasetID(self, dataset_id):
        dataset = self.conn.getObject("Dataset", dataset_id)
        if not dataset:
            raise Exception(f"Dataset with ID {dataset_id} not found")

        images = {}
        for image in dataset.listChildren():  # lazy-loading of images here
            images.update({image.getId(): image.getName()})

        return images

    def get_original_upload_folder(self, image_id):
        try:
            folder = dict(
                self.conn.getObject("Image", image_id)
                .getAnnotation()
                .getValue()
            ).get("Folder", "uploads")
        except (AttributeError, KeyError):
            folder = "uploads"  # fallback
        return folder

    def get_fileset_from_imageID(self, image_id):
        # get the image object
        image = self.conn.getObject("Image", image_id)
        return image.getFileset()

    def get_members_of_group(self):
        colleagues = {}
        for idx in self.conn.listColleagues():
            colleagues.update({idx.getFullName(): idx.getId()})

        # need also the current user!!
        colleagues.update(
            {self.get_logged_in_user_name(): self.get_user().getId()}
        )
        return colleagues

    def set_user(self, Id):
        self.conn.setUserId(Id)

    def is_connected(self):
        return self.conn.isConnected()

    def get_all_user(self):
        users = self.conn.getObjects("Experimenter")
        usernames = []
        for user in users:
            name = user.getName()
            if "@" in name:
                usernames.append(name)
        return usernames

    def load_full_image_stack(self, image_id, Ci=None):
        """
        Load a full image stack from OMERO, either all channels or one specific channel (Ci).
        Returns: NumPy array of shape (C, Z, Y, X) or (1, Z, Y, X)
        """
        image = self.conn.getObject("Image", image_id)
        pixels = image.getPrimaryPixels()

        size_z = image.getSizeZ()
        size_t = image.getSizeT()
        size_x = image.getSizeX()
        size_y = image.getSizeY()

        if size_t > 1:
            print(
                f"Warning: image has multiple timepoints (T={size_t}), only T=0 will be loaded."
            )

        if Ci is not None:
            print(f"Loading only channel {Ci}")
            data = np.zeros((1, size_z, size_y, size_x), dtype=np.uint16)
            for z in range(size_z):
                plane = pixels.getPlane(z, Ci, 0)
                data[0, z, :, :] = plane
        else:
            size_c = image.getSizeC()
            print(f"Loading all {size_c} channels")
            data = np.zeros((size_c, size_z, size_y, size_x), dtype=np.uint16)
            for c in range(size_c):
                for z in range(size_z):
                    plane = pixels.getPlane(z, c, 0)
                    data[c, z, :, :] = plane

        return data

    def get_image_dims(self, image_id: int):
        """
        Return the size of the image from the image id of Omero in the format 'ZCTYX'

        Parameters
        ----------
        image_id : int
            image id of Omero

        Returns
        -------
        dict
            size of the image in the format 'ZCTYX'

        """
        image = self.conn.getObject("Image", image_id)
        size_z = image.getSizeZ()
        size_t = image.getSizeT()
        size_c = image.getSizeC()
        size_y = image.getSizeY()
        size_x = image.getSizeX()

        return {
            "Z": size_z,
            "C": size_c,
            "T": size_t,
            "Y": size_y,
            "X": size_x,
        }

    def load_plane_from_img_id(self, image_id, loc):
        image = self.conn.getObject("Image", image_id)
        pixels = image.getPrimaryPixels()
        # print(pixels.getPixelsType().getValue())

        plane = pixels.getPlane(loc["theZ"], loc["theC"], loc["theT"])

        return plane


if __name__ == "__main__":
    pass
