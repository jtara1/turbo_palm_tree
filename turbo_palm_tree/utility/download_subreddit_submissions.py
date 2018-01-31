import shutil
import glob
import json
import time
import logging
import os
from os.path import join
from itertools import chain

from .get_subreddit_submissions import GetSubredditSubmissions

# utility
from .general_utility \
    import slugify, convert_to_readable_time, move_file, \
    get_file_extension, shorten_file_path_if_needed
from .manage_subreddit_last_id import history_log, process_subreddit_last_id
from colorama import init as colorama_init
from colorama import Fore, Style
from gallery_dl import config as gallery_dl_config

# database
from turbo_palm_tree.database_manager.tpt_database import TPTDatabaseManager
try:
    from .image_match_manager import ImageMatchManager
except ImportError:
    # image-match is not installed
    print("Note: image-match module is not installed.")

# Exceptions
from imgur_downloader.imgurdownloader import (
    FileExistsException,
    ImgurException)
from urllib.error import HTTPError
from ssl import SSLError
from gallery_dl.exception import NoExtractorError
from turbo_palm_tree.utility.exception import TurboPalmTreeException

# downloaders
from imgur_downloader import ImgurDownloader
from gallery_dl.job import DownloadJob  # gfycat, but supports many
from turbo_palm_tree.downloaders.deviantart import download_deviantart_url


colorama_init()


class DownloadSubredditSubmissions(GetSubredditSubmissions):
    """Downloads subreddit submissions, deletes older reposts/duplicate images, 
    & stores data of each download in db
    .. todo:: Make logging log to its own separate file
    """
    OS_MAX_PATH_LENGTH = 260

    def __init__(self, subreddit, path, sort_type, limit, previous_id=None,
                 debug=False, disable_db=False, disable_im=False):
        # call constructor of GetSubredditSubmissions class passing args
        super().__init__(subreddit, path, sort_type, limit, previous_id, debug)

        self.log = logging.getLogger('DownloadSubredditSubmissions')
        self.Exceptions = (FileExistsException, FileExistsError,
                           ImgurException, HTTPError, ValueError,
                           SSLError, NoExtractorError, TurboPalmTreeException)

        self.disable_im = disable_im
        if not self.disable_im:
            # elastic search variables
            self.es_index, self.es_doc_type = 'tpt_images', 'image'
            # object used to add, search and compare images in elasticsearch
            # for duplicate deletion
            self.im = ImageMatchManager(index=self.es_index,
                                        doc_type=self.es_doc_type,
                                        distance_cutoff=0.40)

        self.disable_db = disable_db
        if not self.disable_db:
            # get db manager object for inserting and saving data to db
            self.db = TPTDatabaseManager()

        # used to check if url ends with any of these
        self.image_extensions = ('.png', '.jpg', '.jpeg', '.gif')
        video_extensions = ('.webm', '.mp4')
        self.media_extensions = tuple(chain(self.image_extensions,
                                            video_extensions))

        # prevent gallery-dl module from printing to std output
        gallery_dl_config.set(("output", "mode"), "null")

    def download(self):
        """Download media from submissions"""
        continue_downloading = True

        # var limit is constant, self.limit is not constant
        limit = self.limit

        # counters to keep track of how many submissions downloaded & more
        download_count, error_count, skip_count = 0, 0, 0

        # load last-id of submission downloaded from or create new file for id
        log_filename = '._history.txt'
        log_data, prev_id = process_subreddit_last_id(
            subreddit=self.subreddit, sort_type=self.sort_type,
            dir=self.path, log_file=log_filename, verbose=True)
        if not self.previous_id:
            self.set_previous_id(prev_id)

        # ensures the amount of submissions downloaded from is equal to limit
        while continue_downloading:
            errors, skips = 0, 0
            # get submissions (dict containing info) & use data to download
            submissions = self.get_submissions_info()
            for submission in submissions:
                url = submission['url']
                title = submission['title']
                # makes an assumption that len(file_extension) <= 5
                filename = shorten_file_path_if_needed(
                    slugify(title),
                    max_length=self.OS_MAX_PATH_LENGTH - len(self.path) - 5)
                file_path = submission['file_path']
                submission_id = submission['id']

                # if an entire imgur album was downloaded,
                # filenames will be stored here
                final_filenames = []

                self.log.info('Attempting to save {} as {}'
                              .format(url, file_path))

                # check domain and call corresponding downloader
                # download functions or methods
                try:
                    if 'imgur.com' in url:
                        imgur = ImgurDownloader(imgur_url=url,
                                                dir_download=self.path,
                                                file_name=filename,
                                                delete_dne=True,
                                                debug=False)
                        final_filenames, skipped = imgur.save_images()
                        if len(final_filenames) == 1:
                            filename = final_filenames[0]
                            file_path = os.path.join(
                                os.path.dirname(file_path), filename)

                    elif 'deviantart.com' in url:
                        download_deviantart_url(url, file_path)

                    else:
                        job = DownloadJob(url)
                        job.run()
                        # text submission on a subreddit
                        if job.pathfmt is None:
                            raise TurboPalmTreeException(
                                'No path for gallery-dl DownloadJob\n'
                                '\turl = {}'.format(url))
                        file_path = os.path.abspath(job.pathfmt.path)
                        file_path = move_file(
                            file_path,
                            join(self.path,
                                 filename + get_file_extension(file_path)))

                    print('downloaded: {title}; {url}'
                          .format(title=filename, url=url))

                    # get time if file is created, else just use the time now
                    if file_path and os.path.exists(file_path):
                        creation_time = os.path.getctime(file_path)
                    else:
                        creation_time = time.time()

                    if not self.disable_im:
                        metadata = {'source_url': url,
                                    'creation_time': creation_time}
                        # add img, locate & delete older duplicates
                        self.im.delete_duplicates(file_path, metadata=metadata)
                    if not self.disable_db:
                        # add some data to dict insert data into database
                        submission['download_date'] = convert_to_readable_time(
                            creation_time)
                        self.db.insert(submission)

                except self.Exceptions as e:
                    msg = '{}: {}'.format(type(e).__name__, e.args)
                    self.log.warning(msg)
                    print(Fore.RED + msg + Style.RESET_ALL)
                    errors += 1
                except KeyboardInterrupt:
                    msg = 'KeyboardInterrupt caught, exiting program'
                    self.log.info(msg)
                    print(msg)
                    continue_downloading = False
                    break

            # update previous id downloaded
            if 'submission_id' in locals().keys():
                self.set_previous_id(submission_id)

            # update count of media successfully downloaded
            download_count += self.limit - errors - skips
            error_count += errors
            skip_count += skips

            # update attribute limit which is used when getting submissions
            if download_count < limit:
                self.set_limit(limit - download_count)
            elif download_count >= limit or not continue_downloading:
                if 'submission_id' in locals().keys():
                    log_data[self.subreddit][self.sort_type]['last-id'] = \
                    submission_id

                history_log(self.path, log_filename, 'write', log_data)
                continue_downloading = False

        # continue_downloading is false
        if not self.disable_db:
            self.db.close()

        self._cleanup_files()
        print("{}{} errors occured".format(Fore.YELLOW, error_count))
        print("{}Downloaded from {} submissions from {}/{}{reset}"
              .format(Fore.GREEN, download_count, self.subreddit,
                      self.sort_type, reset=Style.RESET_ALL))

    @staticmethod
    def _cleanup_files():
        """Remove gallery-dl folder if it's there"""
        for path in glob.glob(os.path.join(os.getcwd(), '*')):
            if os.path.basename(path) == 'gallery-dl' and os.path.isdir(path):
                shutil.rmtree(path)
                break

    @staticmethod
    def write_to_file(path=os.path.join(os.getcwd(), str(int(time.time()))),
                      data=None):
        """
        :param path: path (including filename) of file that's to be written to
        :param data: data that gets written in file
        """
        if not data:
            return
        with open(path, 'w') as f:
            f.write(json.dumps(data))
