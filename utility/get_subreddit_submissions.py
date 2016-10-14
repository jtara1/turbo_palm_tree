import sys, os, time
import praw
from enum import Enum


class CheckST:
    """Check if sort type for subreddit is valid and get sort type and
    time filter. Mid way through building this I realized it'd be more clear
    to just use an enum class.
    """
    def __init__(self, sort_type):
        normal_sort_types = ['hot', 'new', 'rising', 'controversial', 'top']
        time_filters = ['hour', 'week', 'month', 'year', 'all']

        def is_valid_sort_type(sort_type):
            if sort_type in normal_sort_types:
                self.valid_type = True
                return True
            else:
                self.valid_type = False
                return False

        # are any elements of normal_sort_types contained in string sort_types
        if (valid_type in sort_type for valid_type in normal_sort_types):
            # valid sort type without time filter
            if is_valid_sort_type(sort_type):
                self.sort_type = sort_type
                self.advanced_sort = False
            # possibly valid sort type with time filter
            else:
                filter_found = [t_filter in sort_type
                                for t_filter in time_filters]
                # there's more than one time filter in given sort_type
                if filter_found.count(True) > 1:
                    self.valid_type = False
                    return
                self.time_filter = time_filters[filter_found.index(True)]
                self.sort_type = sort_type.split(self.time_filter, 1)[0]
                if not is_valid_sort_type(self.sort_type):
                    self.valid_type
        else:
            self.valid_type = False




class SubredditSortTypes(Enum):
    hot = "hot"
    new = "new"
    rising = "rising"
    controversial = "controversial"
    top = "top"

    def __init__(self, sort_type):
        self.time_filters = ['hour', 'week', 'month', 'year', 'all']

    def advanced_sorts(self):
        # only top and controversial sort types are sortable by time filter
        if self.value not in [self.top.value, self.controversial.value]:
            return []

        return [self.value + t_filter for t_filter in self.time_filters]




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
    checker = CheckST('topweek')
    print(list(SubredditSortTypes))
    print(SubredditSortTypes.top.advanced_sorts())
    print(SubredditSortTypes.top.time_filters)
