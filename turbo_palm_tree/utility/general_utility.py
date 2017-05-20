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

try:
    from elasticsearch import Elasticsearch, ElasticsearchException
except ImportError:
    print("Note: elastic search module is not installed")


def slugify(value):
    """Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    # taken from http://stackoverflow.com/a/295466
    # with some modification
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = str(re.sub(r'[^\w\s-]', '', value.decode('ascii')).strip())
    # value = re.sub(r'[-\s]+', '-', value) # not replacing space with hypen
    return value


def convert_to_readable_time(time_epoch):
    """Converts from time since epoch to time in fmt: MONTH-DAY-YR HR:MIN"""
    return time.strftime('%m-%d-%y %H:%M', time.localtime(time_epoch))


def get_subreddit_name(subreddit):
    """Get exact (case-matching) subreddit name"""
    return (Reddit('tpt by /u/jtara1').get_subreddit(subreddit)._get_json_dict()['display_name'])


def start_elasticsearch():
    """Starts elsaticsearch service if not already running & sleeps until it has finished starting up"""
    es = Elasticsearch()
    try:
        es.ping()
    except ElasticsearchException:
        if sys.platform.startswith(('win32', 'cygwin')):
            raise NotImplementedError('Could not connect to elasticsearch service & there\'s no implementation for '
                                      'Windows OS to start the elasticsearch service')
        return_code = call(['sudo', 'service', 'elasticsearch', 'start'])
        while return_code is None:
            print(Fore.RED + 'waiting' + Style.RESET_ALL)
            time.sleep(0.5)


def is_image(image_path):
    """Returns true if (param) image_path is a file path that points to an image, false otherwise"""
    if os.path.isfile(image_path):
        media_info = MediaInfo.parse(image_path)
        if (track.track_type.startswith('Video', 'Audio') for track in media_info.tracks):
            return False
        if (track.track_type == 'Image' for track in media_info.tracks):
            return True
    return False


if __name__ == "__main__":
    t = time.time()
    print(time.localtime())
    print(time.localtime(time.time()))
    print(time.time())
    print(convert_to_readable_time(t))
    # note the case-matching name is BackgroundArt
    print(get_subreddit_name('backgroundart'))
