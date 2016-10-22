import os, time, sys
import logging

from .get_subreddit_submissions import GetSubredditSubmissions

# utility
from .general_utility import slugify
from .manage_subreddit_last_id import history_log, process_subreddit_last_id
from database_manager.tpt_database import TPTDatabaseManager

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
    .. todo:: Make logging log to it's own seperate file"""

    def __init__(self, *args, **kwargs):
        # call constructor of GetSubredditSubmissions class passing args
        super().__init__(*args, **kwargs)
        self.log = logging.getLogger('DownloadSubredditSubmissions')
        self.Exceptions = (FileExistsException, FileExistsError,
            ImgurException, HTTPError, ValueError, Exception)


    def download(self):
        """Download media from submissions"""
        # get db manager object for inserting and saving data to db
        db = TPTDatabaseManager()
        exit_program = False

        # used to check if url ends with any of these
        media_extensions = ('.png', '.jpg', '.jpeg', '.webm', '.gif', '.mp4')
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
        self.previous_id = prev_id if not self.previous_id else self.previous_id

        # ensures the amount of submissions downloaded from is equal to limit
        while(download_count < limit and not exit_program):
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
                    if url.endswith(media_extensions) or (
                        'i.reddituploads.com' in url):
                        direct_link_download(url, file_path)

                    elif 'imgur.com' in url:
                        imgur = ImgurDownloader(imgur_url=url,
                            dir_download=self.path, file_name=filename,
                            delete_dne=True, debug=False)
                        imgur.save_images()

                    elif 'gfycat.com' in url:
                        gfycat_id = url.split('/')[-1]
                        gfycat = Gfycat().more(gfycat_id).download(save_dir)

                    elif 'deviantart.com' in url:
                        download_deviantart_url(url, file_path)

                    else:
                        raise ValueError('Invalid submission URL: %s' % url)

                    # add some data to dict insert data into database
                    submission['download_date'] = time.time()
                    db.insert(submission)

                except self.Exceptions as e:
                    msg = '{}: {}'.format(type(e).__name__, e.args)
                    self.log.warning(msg)
                    print(msg)
                    errors += 1
                except KeyboardInterrupt:
                    msg = 'KeyboardInterrupt sent, exiting program'
                    self.log.info(msg)
                    print(msg)
                    exit_program = True

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
            else:
                log_data[self.subreddit][self.sort_type]['last-id']=submission_id
                history_log(self.path, log_filename, 'write', log_data)

        db.close()
