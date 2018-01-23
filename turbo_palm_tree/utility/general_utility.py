import unicodedata
import re
import time
import sys
import os
from praw import Reddit
from subprocess import call
from colorama import init as colorama_init
from colorama import Fore, Style
colorama_init()
from pymediainfo import MediaInfo
import shutil

try:
    from elasticsearch import Elasticsearch, ElasticsearchException
except ImportError:
    print("Note: elastic search module is not installed")


def slugify(value):
    """Normalizes string, removes characters that are not:
    alphanumeric, whitespace, or dash characters"""
    # taken from http://stackoverflow.com/a/295466
    # with some modification
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = str(re.sub(r'[^\w\s-]', '', value.decode('ascii')).strip())
    return value


def shorten_file_path(path, file_extension='', max_length=260):
    """Shortens the file path if it has more than max_length chars. Assumes
    there is no file extension that needs to be saved
    e.g.: # asserts True
    shorten_file_path('/home/j/file.jpg', '.jpg', 12)) == '/home/j/f.jpg'
    :param path: path we can measuring and possibly changing
    :param file_extension: the extension of the file the path points to if
        there is any
    :param max_length: max length (in characters) permitted by the OS for any
        file path
    """
    path = os.path.abspath(path)
    path_len = len(path)
    if path_len > max_length:
        directory = os.path.dirname(path)
        max_base_name = max_length - len(directory) - len(file_extension)
        if max_base_name <= 0:
            raise Exception('File path is too long (> {} chars): {}'
                            .format(max_length, path))

        base_name = os.path.basename(path)
        base_name_no_ext = base_name[:base_name.rfind(file_extension)]
        path = os.path.join(directory,
                            base_name_no_ext[:max_base_name] + file_extension)
    return path


def get_file_extension(file_name):
    """e.g.: "/home/j/path/my.video.mp4" -> ".mp4"
    Throws an exception, ValueError, if there is no "." character in file_name
    :param file_name: <str> any string or path that is the name of a file
    :return: the file extension of the param, file_name
    """
    return file_name[file_name.rindex('.'):]


def convert_to_readable_time(time_epoch):
    """Converts from time since epoch to time in fmt: MONTH-DAY-YR HR:MIN"""
    return time.strftime('%m-%d-%y %H:%M', time.localtime(time_epoch))


def get_subreddit_name(subreddit):
    """Get exact (case-matching) subreddit name"""
    return (Reddit('tpt by /u/jtara1').get_subreddit(subreddit)
        ._get_json_dict()['display_name'])


def start_elasticsearch():
    """Starts elsaticsearch service if not already running & sleeps
    until it has finished starting up
    """
    es = Elasticsearch()
    try:
        es.ping()
    except ElasticsearchException:
        if sys.platform.startswith(('win32', 'cygwin')):
            raise NotImplementedError(
                'Could not connect to elasticsearch service & '
                'there\'s no implementation for '
                'Windows OS to start the elasticsearch service')
        return_code = call(['sudo', 'service', 'elasticsearch', 'start'])
        while return_code is None:
            print(Fore.RED + 'waiting' + Style.RESET_ALL)
            time.sleep(0.5)


def is_image(image_path):
    """Returns True if (param) image_path is a file path that points to an
    image, False otherwise
    """
    if os.path.isfile(image_path):
        media_info = MediaInfo.parse(image_path)
        if (track.track_type.startswith('Video', 'Audio')
            for track in media_info.tracks):
            return False
        if (track.track_type == 'Image' for track in media_info.tracks):
            return True
    return False


def move_file(source_path, destination_path, delete_original=True):
    """Move file from source_path to destination_path"""
    if os.path.isfile(source_path):
        new_path = shutil.copy(source_path, destination_path)
        if delete_original:
            os.remove(source_path)
        return new_path


def rename_file(file_path, new_file_name):
    """e.g.:
    rename_file('/home/j/file.txt', 'new_file.txt') == '/home/j/new_file.txt'
    """
    path = os.path.abspath(file_path)
    return move_file(path, os.path.join(os.path.dirname(path), new_file_name))


if __name__ == "__main__":
    t = time.time()
    print(time.localtime())
    print(time.localtime(time.time()))
    print(time.time())
    print(convert_to_readable_time(t))
    # note the case-matching name is BackgroundArt
    print(get_subreddit_name('backgroundart'))
    print('-' * 60)
    print(shorten_file_path('/home/j/file.jpg', '.jpg', 12))  # '/home/j/f.jpg'
    print(shorten_file_path('/home/j/Documents', '', 12))  # '/home/j/Docum'