import sys, os, time
import praw


class GetSubredditSubmissions:
    """Return links and data on a number of submission of a given subreddit."""

    def __init__(subreddit, sort_type, numb_submissions):
        """
        :param subreddit: name of subreddit
        :param sort_type: 'hot', 'top', 'new', or 'controversial' as base
            `sort_type` in addition 'top' and 'controversial' can have an
            advanced sort option such to sort by time frame
            (e.g.: 'topweek', 'controversialall')
        :param numb_submissions: number of submissions to get
        """


        r = praw.Reddit(user_agent='turbo_palm_tree')




if __name__ == "__main__":
    pass
