import os
from argparse import ArgumentParser
from enum import Enum
from .general_utility import get_subreddit_name


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
                        help='Directory to save images in; defaults to cwd \
                            joined with name of subreddit')
    parser.add_argument('--sort-type', '-s', metavar='<s>', required=False,
                        default='hot', type=str,
                        help='Sort type for subreddit. Search '
                             'SubredditSortTypes in this repo for more info')
    parser.add_argument('--limit', '--num', '-l', metavar='<l>', required=False,
                        default=5, type=int, help='Number of submissions to'
                        ' download from; defaults to 5')
    parser.add_argument('--prev-id', '--last-id', metavar='<id>', type=str,
                        default='', required=False, help='Begin downloading'
                        ' from the submission after the given reddit id')
    parser.add_argument('--restart', '-r', required=False, action='store_false',
                        default=False,
                        help='Begin downloading from the beggining')
    parser.add_argument('--gui', '-g', required=False, action='store_false',
                        default=False,
                        help='Enables use of Gooey module to provide a GUI '
                             'for use of application')
    parser.add_argument('--ignore-gooey', required=False, action='store_false',
                        default=False,
                        help='Use -g or --gui for GUI enabling instead '
                             '(GUI disable by default). '
                             'This disables Gooey GUI wrapper for CLI.')
    parser.add_argument('--disable-database', '--disable-db', '--no-db',
                        required=False,
                        action='store_false', default=False,
                        help='Disable use of database to record data of each '
                             'submission downloaded')
    parser.add_argument('--disable-image-match', '--disable-im', '--no-im',
                        required=False,
                        action='store_true', default=True,
                        help='Disable use of elasticsearch and image-match '
                             'modules which delete duplicate images')
    parser.add_argument('--debug', '-d', required=False, default=True,
                        action='store_true', help='Enable debug mode')

    parsed_arguments = parser.parse_args(args)

    # validate sort-type passed
    if not valid_sort_type(parsed_arguments.sort_type):
        print('CLI ERROR: Invalid sort-type')
        parse_arguments(['--help'])

    # if subreddit name passed
    subreddit_list_extensions = ('.txt')
    if not (parsed_arguments.subreddit.endswith(subreddit_list_extensions) and (
            os.path.isfile(parsed_arguments.subreddit))):
        parsed_arguments.subreddit = \
            get_subreddit_name(parsed_arguments.subreddit)
        # set default directory if none given
        if not parsed_arguments.directory:
            parsed_arguments.directory = os.path.join(
                os.getcwd(),
                parsed_arguments.subreddit)
    # if subreddit list passed
    else:
        if not parsed_arguments.directory:
            parsed_arguments.directory = os.getcwd()

    return parsed_arguments
