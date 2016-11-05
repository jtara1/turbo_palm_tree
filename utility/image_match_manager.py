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
        # self.index = index
        # self.doc_type = doc_type
        self.log = logging.getLogger(type(self).__name__)
        es = Elasticsearch(index=index, doc_type=doc_type)
        # super(SignatureES, self).__init__(es=es, index=index, doc_type=doc_type, timeout=timeout, size=size,
        #                                   *args, **kwargs)
        super().__init__(es=es, index=index, doc_type=doc_type, *args, **kwargs)

    def get_duplicates(self, path, metadata=None, delete_duplicates=False):
        """Add image (or directory containing images) to elasticsearch engine then search for duplicates
        of the added image(s), and return duplicate file data (local file)
        :param path: path that points to an image file or directory containing image files
        :param metadata: (dictionary) contains data related to path
        :param delete_duplicates: delete BOTH all but one of local files and entries in elasticsearch that are
            matched as duplicates
        .. todo::
            1. use git submodule that verifies file is an image
            2. update image-match module so that all entries except the most recent one are deleted
        """
        all_duplicates = []
        # if path points to a directory
        if os.path.isdir(path):
            files = sorted(glob.glob(os.path.join(path, '*')))
            for file in files:
                all_duplicates.extend(self._get_duplicates_of_file(file, metadata, delete_duplicates))
        # elif path points to a file
        elif os.path.isfile(path):
            return self._get_duplicates_of_file(path, metadata, delete_duplicates)
        else:
            raise ValueError('{func}: Invalid {arg}'.format(func='get_duplicates', arg='path'))
        return all_duplicates

    def _get_duplicates_of_file(self, path, metadata=None, delete_duplicates=False):  # if path points to a file
        all_duplicates = []
        print('GETTING DUP OF : {}'.format(path))
        self.add_image(path, metadata=metadata, refresh_after=True)
        try:
            matching_images = self.search_image(path)
        except FileNotFoundError:
            return all_duplicates
        if len(matching_images) > 1:
            all_duplicates = [
                {
                    'path': item['path'],
                    'metadata': item['metadata'],
                    'es_id': item['id'],
                }
                for item in matching_images]

            if delete_duplicates:
                for duplicate in all_duplicates:
                    if path != duplicate['path']:
                        self.log.info('Deleting old duplicate: {}'.format(duplicate['path']))
                        os.remove(duplicate['path'])  # delete local file
                        self.es.delete(index=self.index,
                                       doc_type=self.doc_type,
                                       id=duplicate['es_id'], refresh=True)  # delete entry in elasticsearch
        return all_duplicates

    def delete_duplicates(self, path, metadata=None):
        """Several steps are done within this method:
        1. adds the image from the :param path: to es
        2. search for matching images of :param path: in es (with distance <= 40)
        Search for image in es then all delete local files (except for the one given in parameter path)
        and all duplicates in es (except for the one whose path value is equal to the argument of path"""
        duplicates = self.get_duplicates(path, metadata)
        pass  # ...
