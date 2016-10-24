# @Author: rachmadaniHaryono (https://github.com/rachmadaniHaryono)

"""Module to parse or download images from deviantart page.
The basis of this was built by
[rachmadaniHaryono](https://github.com/rachmadaniHaryono) with additions and
modifications from jtara1 & contributers of [turbo_palm_tree]
(https://github.com/jtara1/turbo_palm_tree)
"""
try:  # py2
    from urllib2 import urlopen
except ImportError:  # py3
    from urllib.request import urlopen

from bs4 import BeautifulSoup
import logging
import os
import math

from .direct_link_download import direct_link_download


def process_deviantart_url(url):
    """
    process deviantart url.

    Given a DeviantArt URL, determine if it's a direct link to an image, or
    a standard DeviantArt Page. If the latter, attempt to acquire Direct link.

    :return: deviantart image urls
    :rtype: list
    """
    # We have it! Dont worry
    if url.endswith('.jpg'):
        return [url]
    else:
        imgs = []
        html_soup = BeautifulSoup(urlopen(url).read(), 'lxml')
        marker = 'filters:no_upscale():origin()/'
        soup_imgs = [xx.get('src') for xx in html_soup.select('img')
                     if marker in xx.get('src')]
        for ori_img in soup_imgs:
            img_parts = ori_img.split(marker)[1].split('/', 1)
            img_server = img_parts[0]
            img_sub = img_parts[1]
            imgs.append('http://%s.deviantart.net/%s' % (img_server, img_sub))
        return imgs
    return [url]


def download_deviantart_url(url, path):
    """Downloads image(s) from given deviantart url"""
    urls = process_deviantart_url(url)

    if len(urls) == 1:
        direct_link_download(urls[0], path)

    elif len(urls) > 1:
        if os.path.isfile(path):
            raise ValueError('%s points to a file, but there\'s more than one'
                             ' image to download' % path)

        for index in range(len(urls)):
            # prefix source: https://github.com/alexgisby/imgur-album-downloader
            prefix = "%0*d" % (
                int(math.ceil(math.log(len(urls) + 1, 10))), index)
            direct_link_download(urls[index], os.path.join(path, prefix))


if __name__ == "__main__":
    from direct_link_download import direct_link_download

    user_url = 'http://cartoongirl7.deviantart.com/'
    single_image = 'http://www.deviantart.com/art/Impossible-LOV3-ver-3-35710689'
    # ret = process_deviantart_url(single_image)
    # print(ret)
    # print(len(ret))
    dir1 = os.path.join(os.getcwd(), 'devimg.png')
    # download_deviantart_url(single_image, dir1)
    dir2 = os.path.join(os.getcwd(), 'tmp')
    download_deviantart_url(user_url, dir2)
