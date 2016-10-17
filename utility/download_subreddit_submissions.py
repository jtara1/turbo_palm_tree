import os, time, sys
import logging

from .get_subreddit_submissions import GetSubredditSubmissions
from .general_utility import slugify

# Exceptions
from downloaders.imgur_downloader.imgurdownloader import (
    FileExistsException, ImgurException)


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
        logging.basicConfig(filename='download_history.log',
            format='%(levelname)s|%(name)s|%(asctime)s|%(message)s',
            datefmt='%m/%d/%y %H:%M:%S',
            level=logging.DEBUG)
        self.log = logging.getLogger('DownloadSubredditSubmissions')


    def download(self):
        """Download media from submissions"""
        media_extensions = ('.png', '.jpg', '.jpeg', '.webm', '.gif', '.mp4')
        submissions = self.get_submissions_info()

        for submission in submissions:
            url = submission['url']
            title = submission['title']
            filename = slugify(title)
            file_path = os.path.join(self.path, filename)

            self.log.info('Attempting to save %s as %s' % (url, file_path))

            try:
                if url.endswith(media_extensions):
                    direct_link_download(url, file_path)

                elif 'imgur.com' in url:
                    imgur = ImgurDownloader(imgur_url=url, dir_download=self.path,
                        file_name=filename, delete_dne=True, debug=False)
                    imgur.save_images()

                elif 'gfycat.com' in url:
                    # choose the smallest file on gfycat
                    gfycat_json = Gfycat().more(url.split("gfycat.com/")[-1]).json()
                    if gfycat_json["mp4Size"] < gfycat_json["webmSize"]:
                        urls = [gfycat_json["mp4Url"]]
                    else:
                        urls = [gfycat_json["webmUrl"]]
                    (direct_link_download(url) for url in urls)

                elif 'deviantart.com' in url:
                    download_deviantart_url(url, file_path)

            except (FileExistsException, FileExistsError) as e:
                msg = '%s already exists (url = %s)' % (file_path, url)
                self.log.warn(msg)
                print(msg)

            except ImugrException as e:
                msg = 'ImgurException: %s' % e.msg
                self.log.warn(msg)
                print(msg)

            except Exception as e:
                msg = 'Exception: %s' % e.msg
                self.log.warn(msg)
                print(msg)
