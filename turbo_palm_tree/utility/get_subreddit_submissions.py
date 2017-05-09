import sys
import os
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
from turbo_palm_tree.utility.general_utility import slugify, convert_to_readable_time


class GetSubredditSubmissions:
    """Return links and data on a number of submission of a given subreddit."""

    def __init__(self, subreddit, path, sort_type, limit, previous_id=None,
                 debug=False):
        """
        :param subreddit: name of subreddit
        :param path: directory to save images to
        :param sort_type: 'hot', 'top', 'new', or 'controversial' as base
            `sort_type` in addition 'top' and 'controversial' can have an
            advanced sort option such to sort by time frame
            (e.g.: 'topweek', 'controversialall')
        :param limit: number of submissions to get
        :param previous_id: reddit id (or fullname) to begin downloading after
        :param disable_db: disables the use of database which is used to record data of each submission
        :param disable_im: disable use of image-match & elasticsearch modules which are used to delete reposts/duplicate
            images
        :param debug: enable debug prints and logging
        """
        self.log = logging.getLogger('GetSubredditSubmissions')

        self.subreddit = subreddit
        self.sort_type = sort_type
        self.praw_reddit = praw.Reddit(user_agent='tpt')
        self.limit = limit
        self.previous_id = '' if not previous_id else (
            self.set_previous_id(previous_id))
        self.path = path

        # deal with sort types that do and don't have time filter concatenated
        valid_sort_types = list(st.value for st in list(SubredditSortTypes))
        self.base_sort_type = valid_sort_types[
            [st in sort_type for st in valid_sort_types].index(True)]

        self.time_filter = sort_type.split(self.base_sort_type)[-1]

        # get URL of subreddit for given sort_type
        base_url = 'https://www.reddit.com/r/'
        self.url = '{}{}/{}'.format(base_url, self.subreddit,
                                    self.base_sort_type)

        self.log.debug('attributes = {}'.format(self.__dict__))

    def get_submissions(self):
        """Returns list of tuples containing submission URLs & title"""
        submissions = self.praw_reddit.get_content(
            url=self.url,
            limit=self.limit,
            params={
                'sort': self.base_sort_type,
                't': self.time_filter,
                'after': self.previous_id
            }
        )
        return submissions

    def get_submissions_info(self):
        """Extracts info from each submission and returns a generator object
        .. protip:: Check `submission.__dict__` or `submission._api_link` for
        more dictionary keys and values that are usable"""
        submissions = self.get_submissions()

        # it's possible someone submits a submission then delete their account
        return ({
                    'subreddit': self.subreddit,
                    'url': s.url,
                    'fullname': s.fullname,
                    'id': s.fullname[3:],
                    'title': s.title,
                    'score': s.score,
                    'author': s.author.name if s.author else '[deleted]',
                    'selftext': s.selftext,
                    'submit_date': convert_to_readable_time(s.created),
                    'comments_url': s.permalink,
                    'file_path': os.path.join(self.path, slugify(s.title))
                } for s in submissions)

    def set_limit(self, limit):
        """Set attribute limit to :param limit:"""
        self.limit = limit

    def set_previous_id(self, prev_id):
        """Set attribute previous_id to :param prev_id:"""
        fullname_tag = 't3_'
        if prev_id[:3] != fullname_tag:
            prev_id = '{tag}{id}'.format(tag=fullname_tag, id=prev_id)
        self.previous_id = prev_id
