import os
from urllib.request import urlretrieve


def direct_link_download(url, file_path):
    """Download content from url to file_path using `urllib.request.urlretrieve`

    :param url: direct link to an image
    :param file_path: file path (including filename) to save image to
    """
    file_path = os.path.abspath(file_path)

    # make sure the file_path param doesn't point to a directory
    if os.path.isdir(file_path):
        raise ValueError(':param file_path: shouldn\'t point to a directory')

    # make sure the file doesn't already exist
    if os.path.isfile(file_path):
        raise FileExistsError('%s already exists' % file_path)

    # create path(s) for file_path if necessary
    base_dir = os.path.dirname(file_path)
    if not os.path.isdir(base_dir):
        os.makedirs(base_dir)

    # download and save the image
    urlretrieve(url, file_path)


if __name__ == "__main__":
    # tests
    dir1 = os.path.join(os.getcwd(), 'img1.jpg')
    print(dir1)
    url = 'http://i.imgur.com/2MlAOkC.jpg'
    url2 = 'http://img05.deviantart.net/41ee/i/2013/299/9/f/_stock__mystic_woods_by_dominikaaniola-d2ehxq4.jpg'
    # direct_link_download(url, 'img1.jpg')
    direct_link_download(url2, './tmp/tmp2/img2.jpg')
