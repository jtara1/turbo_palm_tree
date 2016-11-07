import glob
import logging
import os

from elasticsearch import Elasticsearch
from image_match.elasticsearch_driver import SignatureES


class ImageMatchManager(SignatureES):
    """Manage tasks associated with image-match module (checks to see if one image is equal to another in es) and
    elasticsearch (es) engine (contains all images that have been inserted)
    """

    def __init__(self, index='images', doc_type='image', *args, **kwargs):
        """
        :param index: index used for elasticsearch
        :param doc_type: doc_type used for elasticsearch
        :param distance_cutoff: the closer the distance is to 0.0, the more similar the two images in comparison are to
            each other (<= 0.40 is the threshold for identical images)
        .. todo:: automatically create the index & doc_type if not found in elasticsearch
        """
        self.log = logging.getLogger(type(self).__name__)
        es = Elasticsearch(index=index, doc_type=doc_type)
        # super(SignatureES, self).__init__(es=es, index=index, doc_type=doc_type, timeout=timeout, size=size,
        #                                   *args, **kwargs)
        super().__init__(es=es, index=index, doc_type=doc_type, *args, **kwargs)

    def get_duplicates(self, path, metadata=None):
        """Does the following:
        1. add image (or directory containing images) to elasticsearch engine (one at a time)
        2. search for duplicates of the added image(s) & yield the image path & the image duplicates

        :param path: path that points to an image file or directory containing image files
        :param metadata: (dictionary) contains data related to image

        :return: current image path and the list of duplicate images matched for the current image
            If there are no matched images (other than a match for the image just inserted) then `None` is returned in
            place of list of duplicate images
        :rtype: generator yielding tuple containing (string, list of dictionaries or None)

        .. todo::
            1. use git submodule that verifies file is an image
        """
        # if path points to a directory
        if os.path.isdir(path):
            files = sorted(glob.glob(os.path.join(path, '*')))
            for file in files:
                yield file, self._get_duplicates_of_file(file, metadata)
        # elif path points to a file
        elif os.path.isfile(path):
            yield path, self._get_duplicates_of_file(path, metadata)
        else:
            raise ValueError('{func}: Invalid {arg}'.format(func='get_duplicates', arg='path'))

    def _get_duplicates_of_file(self, path, metadata=None):
        """Helper method for `get_duplicates` method
        add an individual image to es, search es for identical images & return the list of dictionaries
        of each duplicate image
        """
        # print('GETTING DUP OF : {}'.format(path))
        self.add_image(path, metadata=metadata, refresh_after=True)
        try:
            matching_images = self.search_image(path)
        except FileNotFoundError:
            self.log.warning('_get_duplicates_of_file: {} NOT FOUND'.format(path))
            return
        if len(matching_images) > 1:
            return list({
                    'path': item['path'],
                    'metadata': item['metadata'],
                    'es_id': item['id']}
                    for item in matching_images)
        return

    def delete_duplicates(self, path, metadata=None):
        """Several steps are done within this method (steps 1 & 2 are done within the `get_duplicates` method):
        1. adds the image from the :param path: to es
        2. search for matching images of :param path: in es (with distance <= 0.40)
        3. delete all except for the most recent copy of the duplicate image (both local file & entry in es)

        :param path: path (url or local file (or folder) path) - should be an image or directory containing images
        :param metadata: (dictionary) this data is attached to image (or each image) when the path(s) are inserted into
            es
        """
        data = self.get_duplicates(path, metadata)  # adds image(s) to es & returns all matching images found
        # if len(duplicates) == 1:
        #     return
        for file_path, duplicates in data:
            if duplicates is None:
                continue

            for duplicate in duplicates:
                # print('path: {}'.format(file_path))
                # print('duplicate: {}'.format(duplicate))
                if file_path != duplicate['path']:
                    self.log.info('Deleting old duplicate: {}'.format(duplicate['path']))
                    os.remove(duplicate['path'])  # delete local file
                    self.es.delete(index=self.index,
                                   doc_type=self.doc_type,
                                   id=duplicate['es_id'], refresh=True)  # delete entry in elasticsearch
