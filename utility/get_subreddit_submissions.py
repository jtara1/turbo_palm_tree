import sys, os, time
import praw
import logging

if __name__ == "__main__":
    from parse_arguments import SubredditSortTypes
    dir = os.getcwd()
    getter = GetSubredditSubmissions('pics', dir, 'hot', 5)
    getter2 = GetSubredditSubmissions('pics', dir, 'topall', 5)
    getter.get_submissions()
    getter2.get_submissions()
    sys.exit(0)

from .parse_arguments import SubredditSortTypes

class GetSubredditSubmissions:
    """Return links and data on a number of submission of a given subreddit."""

    def __init__(self, subreddit, dir, sort_type, numb_submissions):
        """
        :param subreddit: name of subreddit
        :param dir: directory to save images to
        :param sort_type: 'hot', 'top', 'new', or 'controversial' as base
            `sort_type` in addition 'top' and 'controversial' can have an
            advanced sort option such to sort by time frame
            (e.g.: 'topweek', 'controversialall')
        :param numb_submissions: number of submissions to get
        """
        self.log = logging.getLogger('GetSubredditSubmissions')

        self.subreddit = subreddit
        self.praw_reddit = praw.Reddit(user_agent='turbo_palm_tree')
        self.limit = numb_submissions

        # deal with sort types that do and don't have time filter concatenated
        valid_sort_types = list(st.value for st in list(SubredditSortTypes))
        self.base_sort_type = valid_sort_types[
            [st in sort_type for st in valid_sort_types].index(True)
        ]
        self.time_filter = sort_type.split(self.base_sort_type)[-1]

        # get URL of subreddit for given sort_type
        base_url = 'https://www.reddit.com/r/'
        self.url = '%s%s/%s.json' % (base_url, self.subreddit,
            self.base_sort_type)
        if self.time_filter:
            self.url += '?sort=%s&t=%s' % (self.base_sort_type, self.time_filter)

        self.log.debug('attributes = %s' % self.__dict__)


    def get_submissions(self):
        """Returns list of tuples containing submission URLs & title"""
        submissions = self.praw_reddit.get_content(url = self.url,
                                        limit = self.limit)
        # json_data = self.praw_reddit.request_json(url=self.url,
        #     limit=self.limit)
        # with open('myJson.txt', 'w') as f:
        #     f.write(str(json_data))

        return submissions


    def get_submissions_info(self):
        """Extracts info from each submission and returns a generator object"""
        submissions = self.get_submissions()
        pass
