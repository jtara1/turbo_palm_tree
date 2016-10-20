import sys, os, time
from argparse import ArgumentParser
from enum import Enum

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


def valid_sort_type(sort_type):
    """Make sure the sort-type given by user is a valid sort type
    :return: sort_type passed if valid else an emtpy string
    :rtype: string
    """
    # build list of valid sort types based on SubredditSortTypes enum class
    valid_st_list = list(st.value for st in list(SubredditSortTypes))
    valid_st_list.extend(SubredditSortTypes.top.advanced_sorts() +
                        SubredditSortTypes.controversial.advanced_sorts())

    checker_list = list(sort_type == valid_st for valid_st in valid_st_list)
    if checker_list.count(True) == 1:
        return sort_type
    else:
        return ''


def parse_arguments(args):
    """Parse arguments using the builtin argparse module"""
    parser = ArgumentParser(description='Downloads image files from the'
                            ' specified subreddit or list of subreddits.')
    parser.add_argument('subreddit', metavar='<subreddit>', type=str,
                        help='Subreddit or subreddit list file name')
    parser.add_argument('directory', metavar='<directory>', nargs='?', type=str,
                        default=os.getcwd(), help='Directory to save images in')
    parser.add_argument('--sort-type', '-s', metavar='s', required=False,
                        default='hot', type=str, help='Sort type for subreddit')
    parser.add_argument('--limit', '--num', '-l', metavar='l', required=False,
                        default=25, type=int, help='Number of submissions to'
                        ' download from')
    parser.add_argument('--prev-id', '--last-id', metavar='id', type=str,
                        default=None, required=False, help='Begin downloading'
                        ' from the submission after the given reddit id')
    parser.add_argument('--restart', '-r', required=False, action='store_false',
                        default=False,
                        help='Begin downloading from the beggining')
    parser.add_argument('--debug', '-d', required=False, default=True,
                        action='store_true', help='Enable debug mode')

    parsed_argument = parser.parse_args(args)

    if not valid_sort_type(parsed_argument.sort_type):
        print('CLI ERROR: Invalid sort-type')
        parse_arguments(['--help'])

    return parsed_argument
