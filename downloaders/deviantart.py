# @Author: rachmadaniHaryono (https://github.com/rachmadaniHaryono)

"""Module to parse deviantart page; The basis of this was built by
[rachmadaniHaryono](https://github.com/rachmadaniHaryono)"""
try:  # py2
    from urllib2 import urlopen
except ImportError:  # py3
    from urllib.request import urlopen

from bs4 import BeautifulSoup


def process_deviant_url(url):
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


if __name__ == "__main__":
    user_url = 'http://cartoongirl7.deviantart.com/'
    single_image = 'http://www.deviantart.com/art/Impossible-LOV3-ver-3-35710689'
    ret = process_deviant_url(single_image)
    print(ret)
    print(len(ret))
