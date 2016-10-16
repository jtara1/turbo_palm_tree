import sys, os, time
import praw
from parse_arguments import SubredditSortTypes
import logging
from urllib.request import urlopen, Request

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
        logging.basicConfig(filename='submissions.log')
        log = logging.getLogger('GetSubredditSubmissions')

        self.subreddit = subreddit
        self.praw_reddit = praw.Reddit(user_agent='turbo_palm_tree')
        self.numb_submissions = numb_submissions
        self.limit = 25

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

        log.debug(self.url)
        print(self.url)


    def get_submissions(self):
        """Returns list of tuples containing submission URLs & title"""
        s = self.praw_reddit.get_content(url = self.url,
                                        limit = self.limit)
        # req = self.praw_reddit.request_json(url=self.url)

        for submission in s:
            print(submission.url)

        # if self.base_sort_type == "hot":
        #     submissions = self.praw_reddit.get_subreddit(self.subreddit).get_hot(self.limit)
        # elif self.base_sort_type == "top":
        #     self.praw_reddit.get_subreddit(self.subreddit).get_top(self.limit)
        # elif self.base_sort_type == "new":
        #     self.praw_reddit.get_subreddit(self.subreddit).get_new(self.limit)
        # elif self.base_sort_type == "rising":
        #     self.praw_reddit.get_subreddit(self.subreddit)
        #         .get_rising(self.limit)
        # elif self.base_sort_type == "controversial":
        #     self.praw_reddit.get_subreddit(self.subreddit)
        #         .get_controversial(self.limit)

if __name__ == "__main__":
    dir = os.getcwd()
    getter = GetSubredditSubmissions('pics', dir, 'hot', 5)
    getter2 = GetSubredditSubmissions('pics', dir, 'topall', 5)
    getter.get_submissions()
    # getter2.get_submissions()
