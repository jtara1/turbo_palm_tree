import json
import time
import logging
import os
from itertools import chain

from .get_subreddit_submissions import GetSubredditSubmissions

# utility
from .general_utility import slugify, convert_to_readable_time
from .manage_subreddit_last_id import history_log, process_subreddit_last_id
from colorama import init as colorama_init
from colorama import Fore, Style

# database
from turbo_palm_tree.turbo_palm_tree.database_manager.tpt_database \
    import TPTDatabaseManager
try:
    from .image_match_manager import ImageMatchManager
except ImportError:
    # image-match is not installed
    print("Note: image-match module is not installed.")

# Exceptions
from turbo_palm_tree.turbo_palm_tree \
    .downloaders.imgur_downloader.imgurdownloader.imgurdownloader\
    import (FileExistsException,
            ImgurException)
from urllib.error import HTTPError
from ssl import SSLError

# downloaders
from turbo_palm_tree.turbo_palm_tree\
    .downloaders.direct_link_download import direct_link_download
from turbo_palm_tree.turbo_palm_tree\
    .downloaders\
    .imgur_downloader.imgurdownloader.imgurdownloader \
    import ImgurDownloader
from turbo_palm_tree.turbo_palm_tree.downloaders.gfycat.gfycat.gfycat \
    import Gfycat
from turbo_palm_tree.turbo_palm_tree.downloaders.deviantart \
    import download_deviantart_url


colorama_init()


class DownloadSubredditSubmissions(GetSubredditSubmissions):
    def __init__(self, disable_db=False, disable_im=False, *args, **kwargs):
        """Downloads subreddit submissions, deletes older reposts/duplicate
        images, & stores data of each download in db.
        Args are passed on to parent class - might not be updated

        :param subreddit: name of subreddit
        :param path: directory to save images to
        :param sort_type: 'hot', 'top', 'new', or 'controversial' as base
            `sort_type` in addition 'top' and 'controversial' can have an
            advanced sort option such to sort by time frame
            (e.g.: 'topweek', 'controversialall')
        :param limit: number of submissions to get
        :param previous_id: reddit id (or fullname) to begin downloading after
        :param disable_db: disables the use of database which is used to record
            data of each submission
        :param disable_im: disable use of image-match & elasticsearch modules
            which are used to delete reposts/duplicate images
        :param debug: enable debug prints and logging
        """
        # call constructor of GetSubredditSubmissions class passing args
        super().__init__(*args, **kwargs)

        self.log = logging.getLogger('DownloadSubredditSubmissions')
        self.Exceptions = (FileExistsException, FileExistsError,
                           ImgurException, HTTPError, ValueError,
                           SSLError)

        self.disable_im = disable_im
        if not self.disable_im:
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
                filename = slugify(title)
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
                    print('downloading: {title}; {url}'
                          .format(title=filename, url=url))

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

                    elif 'gfycat.com' in url:
                        gfycat_id = url.split('/')[-1]
                        file_path += '.mp4'
                        Gfycat().more(gfycat_id).download(file_path)

                    elif 'deviantart.com' in url:
                        download_deviantart_url(url, file_path)

                    if url.endswith(self.media_extensions) or \
                            'i.reddituploads.com' in url:
                        file_path = direct_link_download(url, file_path)

                    else:
                        raise ValueError('Invalid submission URL: {}'
                                         .format(url))

                    # get time if file is create, else just use the time now
                    if os.path.exists(file_path):
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
                    print('url = {}'.format(url))
                    print(msg)
                    errors += 1
                except KeyboardInterrupt:
                    msg = 'KeyboardInterrupt caught, exiting program'
                    self.log.info(msg)
                    print(msg)
                    continue_downloading = False
                    break

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
                log_data[self.subreddit][self.sort_type]['last-id'] = \
                    submission_id

                history_log(self.path, log_filename, 'write', log_data)
                continue_downloading = False

        # continue_downloading is false
        if not self.disable_db:
            self.db.close()
        # if not self.disable_im:
        #     self.im.close()

        print("{}{} errors occured".format(Fore.YELLOW, error_count))
        print("{}Downloaded from {} submissions from {}/{}{reset}"
              .format(Fore.GREEN, download_count, self.subreddit,
                      self.sort_type, reset=Style.RESET_ALL))

    def write_to_file(self,
                      path=os.path.join(os.getcwd(), str(int(time.time()))),
                      data=None):
        """
        :param path: path (including filename) of file that's to be written to
        :param data: data that gets written in file
        """
        if not data:
            return
        with open(path, 'w') as f:
            f.write(json.dumps(data))
