import unicodedata
import re
import time
import sys
from praw import Reddit
from elasticsearch import Elasticsearch, ElasticsearchException
from subprocess import call


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
    return (Reddit('tpt').get_subreddit(subreddit)._get_json_dict()['display_name'])


def start_elasticsearch():
    """Starts elsaticsearch service if not already running & sleeps until it has finished starting up"""
    es = Elasticsearch()
    try:
        es.ping()
    except ElasticsearchException:
        if sys.platform.startswith(('win32', 'cygwin')):
            raise NotImplementedError('Could not connect to elasticsearch service & there\'s no implementation for '
                                      'windows OS to start the elasticsearch service')
        return_code = call(['sudo', 'service', 'elasticsearch', 'start'])
        while return_code is None:
            print('waiting')
            time.sleep(0.5)


if __name__ == "__main__":
    t = time.time()
    print(time.localtime())
    print(time.localtime(time.time()))
    print(time.time())
    print(convert_to_readable_time(t))
    # note the case-matching name is BackgroundArt
    print(get_subreddit_name('backgroundart'))
