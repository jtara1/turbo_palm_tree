import time
import logging
import os
import glob

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
                           ImgurException, HTTPError, ValueError, Exception)
        # object used to add, search and compare images in elasticsearch for duplicate deletion
        se = Elasticsearch()
        self.image_match_ses = SignatureES(se, distance_cutoff=0.40)

        # used to check if url ends with any of these
        self.media_extensions = ('.png', '.jpg', '.jpeg', '.webm', '.gif', '.mp4')

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
                # file_path = os.path.join(self.path, filename)
                file_path = submission['file_path']
                submission_id = submission['id']

                self.log.info('Attempting to save {} as {}'.format(url,
                                                                   file_path))

                # check domain and call corresponding downloader download
                # functions or methods
                try:
                    if url.endswith(self.media_extensions) or (
                                'i.reddituploads.com' in url):
                        direct_link_download(url, file_path)

                    elif 'imgur.com' in url:
                        imgur = ImgurDownloader(imgur_url=url,
                                                dir_download=self.path, file_name=filename,
                                                delete_dne=True, debug=False)
                        imgur.save_images()

                    elif 'gfycat.com' in url:
                        gfycat_id = url.split('/')[-1]
                        Gfycat().more(gfycat_id).download(file_path)

                    elif 'deviantart.com' in url:
                        download_deviantart_url(url, file_path)

                    else:
                        raise ValueError('Invalid submission URL: %s' % url)

                    # add some data to dict insert data into database
                    submission['download_date'] = convert_to_readable_time(
                        time.time())
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

                # update elasticsearch & check if image has been downloaded previously
                self.remove_duplicates(file_path)

            # update previous id downloaded
            self.set_previous_id(submission_id)

            # update count of media successfully downloaded
            download_count += self.limit - errors - skips
            print('dl count: {}'.format(download_count))
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

    def remove_duplicates(self, path):
        """Add image (or directory containing images) to elasticsearch engine then search for duplicates
        of the added image(s), and delete (both local file and elasticsearch entry) all duplicates
        keeping the most recently downloaded image.
        """
        if os.path.isfile(path) and path.endswith(self.media_extensions):
            self.image_match_ses.add_image(path, refresh_after=True)
            matching_images = self.image_match_ses.search_image(path)
            if len(matching_images) > 1:
                for item in matching_images:
                    if item['path'] != path:
                        self.log.warning('Deleting old duplicate: {}'.format(item['path']))
                        os.remove(item['path'])
                        self.image_match_ses.delete_duplicates(path)
        elif os.path.isdir(path):
            image_iter = glob.iglob(os.path.join(path, '/*'))
            try:
                while True:
                    self.remove_duplicates(next(image_iter))
            except StopIteration:
                pass

