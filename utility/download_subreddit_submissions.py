import json
import time
import logging
import os
import glob
from itertools import chain

from .get_subreddit_submissions import GetSubredditSubmissions

# utility
from .general_utility import slugify, convert_to_readable_time
from .manage_subreddit_last_id import history_log, process_subreddit_last_id

# database
from database_manager.tpt_database import TPTDatabaseManager
from elasticsearch import Elasticsearch
from image_match.elasticsearch_driver import SignatureES

# Exceptions
from downloaders.imgur_downloader.imgurdownloader import (
    FileExistsException,
    ImgurException)
from urllib.error import HTTPError

# downloaders
from downloaders.direct_link_download import direct_link_download
from downloaders.imgur_downloader.imgurdownloader import ImgurDownloader
from downloaders.gfycat.gfycat.gfycat import Gfycat
from downloaders.deviantart import download_deviantart_url


class DownloadSubredditSubmissions(GetSubredditSubmissions):
    """Downloads subreddit submissions
    .. todo:: Make logging log to its own seperate file"""

    def __init__(self, *args, **kwargs):
        # call constructor of GetSubredditSubmissions class passing args
        super().__init__(*args, **kwargs)

        self.log = logging.getLogger('DownloadSubredditSubmissions')
        self.Exceptions = (FileExistsException, FileExistsError,
                           ImgurException, HTTPError, ValueError)
        # object used to add, search and compare images in elasticsearch for duplicate deletion
        se = Elasticsearch()
        # index, doc_type = 'tpt_test', 'image'
        index, doc_type = 'images', 'image'
        self.image_match_ses = SignatureES(se, index=index, doc_type=doc_type, distance_cutoff=0.40)

        # used to check if url ends with any of these
        self.image_extensions = ('.png', '.jpg', '.jpeg', '.gif')
        video_extensions = ('.webm', '.mp4')
        self.media_extensions = tuple(chain(self.image_extensions, video_extensions))

    def download(self):
        """Download media from submissions"""
        # get db manager object for inserting and saving data to db
        db = TPTDatabaseManager()
        continue_downloading = True

        # var limit is constant, self.limit is not constant
        limit = self.limit

        # counters to keep track of how many submissions downloaded & more
        download_count, error_count, skip_count = 0, 0, 0
        status_variables = [download_count, error_count, skip_count]

        # load last-id of submission downloaded from or create new file for id
        log_filename = '._history.txt'
        log_data, prev_id = process_subreddit_last_id(
            subreddit=self.subreddit, sort_type=self.sort_type,
            dir=self.path, log_file=log_filename, verbose=True)
        self.set_previous_id(prev_id) if not self.previous_id else (
            self.previous_id)

        # ensures the amount of submissions downloaded from is equal to limit
        while continue_downloading:
            errors, skips = 0, 0
            # get submissions (dict containing info) & use data to download
            submissions = self.get_submissions_info()
            for submission in submissions:
                url = submission['url']
                title = submission['title']
                filename = slugify(title)
                file_path = submission['file_path']
                submission_id = submission['id']
                final_filenames = []  # if an entire imgur album was downloaded, filenames will be stored here

                self.log.info('Attempting to save {} as {}'.format(url, file_path))

                # check domain and call corresponding downloader download functions or methods
                try:
                    if url.endswith(self.media_extensions) or (
                                'i.reddituploads.com' in url):
                        direct_link_download(url, file_path)

                    elif 'imgur.com' in url:
                        imgur = ImgurDownloader(imgur_url=url,
                                                dir_download=self.path, file_name=filename,
                                                delete_dne=True, debug=False)
                        final_filenames, skipped = imgur.save_images()
                        if len(final_filenames) == 1:
                            filename = final_filenames[0]
                            file_path = os.path.join(os.path.dirname(file_path), filename)

                    elif 'gfycat.com' in url:
                        gfycat_id = url.split('/')[-1]
                        Gfycat().more(gfycat_id).download(file_path)

                    elif 'deviantart.com' in url:
                        download_deviantart_url(url, file_path)

                    else:
                        raise ValueError('Invalid submission URL: {}'.format(url))

                    time.sleep(3)  # sometimes files get referenced before they're actually saved locally

                    creation_time = os.path.getctime(file_path)
                    # update elasticsearch & check if image has been downloaded previously
                    metadata = {'source_url': url, 'creation_time': creation_time}
                    # self.image_match_ses.add_image(
                    #     file_path,
                    #     metadata={'source_url': url, 'creation_time': creation_time},
                    #     refresh_after=True)

                    self.image_match_ses.es_delete_all()  #### DEBUG
                    duplicates = self.get_duplicates(file_path, metadata, delete_duplicates=True)
                    print('DUPLICATES: {}'.format(duplicates))
                    # self.write_to_file(data=list(self.get_duplicates(file_path)))

                    # add some data to dict insert data into database
                    submission['download_date'] = convert_to_readable_time(creation_time)
                    db.insert(submission)

                except self.Exceptions as e:
                    msg = '{}: {}'.format(type(e).__name__, e.args)
                    self.log.warning(msg)
                    print(msg)
                    errors += 1
                except KeyboardInterrupt:
                    msg = 'KeyboardInterrupt caught, exiting program'
                    self.log.info(msg)
                    print(msg)
                    continue_downloading = False

            # update previous id downloaded
            self.set_previous_id(submission_id)

            # update count of media successfully downloaded
            download_count += self.limit - errors - skips
            error_count += errors
            skip_count += skips

            # update attribute limit which is used when getting submissions
            if download_count < limit:
                self.set_limit(limit - download_count)
            elif download_count >= limit or not continue_downloading:
                log_data[self.subreddit][self.sort_type]['last-id'] = submission_id
                history_log(self.path, log_filename, 'write', log_data)
                continue_downloading = False

        db.close()
        print("{} errors occured".format(error_count))
        print("Downloaded from {} submissions from {}/{}".format(download_count,
                                                                 self.subreddit,
                                                                 self.sort_type))

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
            file_iter = glob.iglob(os.path.join(path, '*'))
            for file in file_iter:
                all_duplicates.extend(self._get_duplicates_of_file(file, metadata, delete_duplicates))
        # elif path points to a file
        elif os.path.isfile(path):
            self._get_duplicates_of_file(path, metadata, delete_duplicates)
        else:
            raise ValueError('{func}: Invalid {arg}'.format(func='get_duplicates', arg='path'))
        return all_duplicates

    def _get_duplicates_of_file(self, path, metadata=None, delete_duplicates=False):  # if path points to a file
        all_duplicates = []
        print('GETTING DUP OF : {}'.format(path))
        if os.path.isfile(path):
            self.image_match_ses.add_image(path, metadata=metadata, refresh_after=True)
            matching_images = self.image_match_ses.search_image(path)
            if len(matching_images) > 1:
                all_duplicates = [
                    (item['path'], item['metadata'])
                    for item in matching_images]
                if delete_duplicates:
                    for image_path, metadata in all_duplicates:
                        if image_path != path:
                            self.log.info('Deleting old duplicate: {}'.format(image_path))
                            os.remove(image_path)  # delete local file
                    self.image_match_ses.delete_duplicates(path, refresh_after=True)  # delete all but one entries in elasticsearch
        else:
            raise ValueError('{func}: Invalid {arg}'.format(func='_get_duplicates_of_image', arg='path'))
        return all_duplicates

    def write_to_file(self, path=os.path.join(os.getcwd(), str(int(time.time()))), data=None):
        """
        :param path: path (including filename) of file that's to be written to
        :param data: data that gets written in file
        """
        if not data:
            return
        with open(path, 'w') as f:
            f.write(json.dumps(data))
