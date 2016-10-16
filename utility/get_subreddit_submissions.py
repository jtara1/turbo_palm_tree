import sys, os, time
import praw


class GetSubredditSubmissions:
    """Return links and data on a number of submission of a given subreddit."""

    def __init__(self, subreddit, sort_type, numb_submissions):
        """
        :param subreddit: name of subreddit
        :param sort_type: 'hot', 'top', 'new', or 'controversial' as base
            `sort_type` in addition 'top' and 'controversial' can have an
            advanced sort option such to sort by time frame
            (e.g.: 'topweek', 'controversialall')
        :param numb_submissions: number of submissions to get
        """
        self.praw_reddit = praw.Reddit(user_agent='turbo_palm_tree')
        self.numb_submissions = numb_submissions
        self.limit = 25


    def get_submissions(self):
        """Returns list of tuples containing submission URLs & title"""
        pass


if __name__ == "__main__":
    getter = GetSubredditSubmissions('pics', 'hot', 25)
