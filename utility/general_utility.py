import unicodedata
import re
import time
from praw import Reddit

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
    return (Reddit('turbo_palm_tree').get_subreddit(subreddit)
        ._get_json_dict()['display_name'])



if __name__ == "__main__":
    t = time.time()
    print(time.localtime())
    print(time.localtime(time.time()))
    print(time.time())
    print(convert_to_readable_time(t))
    # note the case-matching name is BackgroundArt
    print(get_subreddit_name('backgroundart'))
