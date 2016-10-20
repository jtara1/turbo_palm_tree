import os, time, sys
import logging

from .get_subreddit_submissions import GetSubredditSubmissions
from .general_utility import slugify

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
    """Downloads subreddit submissions"""

    def __init__(self, *args, **kwargs):
        # call constructor of GetSubredditSubmissions class passing args
        super().__init__(*args, **kwargs)

        # setup logging
        # logging.basicConfig(filename='download_history.log',
        #     format='%(levelname)s|%(name)s|%(asctime)s|%(message)s',
        #     datefmt='%m/%d/%y %H:%M:%S',
        #     level=logging.DEBUG)
        self.log = logging.getLogger('DownloadSubredditSubmissions')
        self.Exceptions = (FileExistsException, FileExistsError,
            ImgurException, HTTPError, ValueError, Exception)


    def download(self):
        """Download media from submissions"""
        # used to check if url ends with any of these
        media_extensions = ('.png', '.jpg', '.jpeg', '.webm', '.gif', '.mp4')
        limit = self.limit
        # we_stuck = False

        # counters to keep track of how many submissions we downloaded & more
        download_count, error_count, skip_count = 0, 0, 0
        status_variables = [download_count, error_count, skip_count]

        # ensures the amount of submissions downloaded from is equal to limit
        while(download_count < limit):
            errors, skips = 0, 0
            # get submissions (dict containing info) & use data to download
            submissions = self.get_submissions_info()
            for submission in submissions:
                url = submission['url']
                title = submission['title']
                filename = slugify(title)
                file_path = os.path.join(self.path, filename)
                submission_id = submission['id']

                self.log.info('Attempting to save %s as %s' % (url, file_path))

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

                # except (FileExistsException, FileExistsError) as e:
                #     msg = '%s already exists (url = %s)' % (file_path, url)
                #     self.log.warning(msg)
                #     print(msg)

                except self.Exceptions as e:
                    msg = '%s: %s' % (type(e).__name__, e.args)
                    self.log.warning(msg)
                    print(msg)
                    errors += 1

            # update previous id downloaded
            self.set_previous_id(submission_id)

            # update count of media successfully downloaded
            download_count += download_count + (
                self.limit - errors - skips)
            print('dl count: %s' % download_count)
            error_count += errors
            skip_count += skips

            # Prevents infinite looping over submissions tht can't be downloaded
            # but it also can prevent progression in getting next submissions
            # if the submissions checked are already downloaded
            # if errors + skips >= self.limit:
            #     if we_stuck:
            #         break
            #     else:
            #         we_stuck = True
            # else:
            #     we_stuck = False

            # update attribute limit which is used when getting submissions
            if download_count < limit:
                self.set_limit(limit - download_count)
