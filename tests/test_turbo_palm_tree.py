import pytest
import turbo_palm_tree
from utility.parse_arguments import parse_arguments
import os
import sys
import time
import itertools


subreddit_url = "https://www.reddit.com/r/jtaraTest/"
subreddit_name = "jtaratest"
#
# @pytest.fixture
# def setup_test():
#     pass

def get_parsed_args():
    """Returns all combinations of possible sort_type options and one subreddit name for cli (parsed)"""
    temp_dir = os.path.join(os.getcwd(), 'temp_test_downloads')
    # if not os.path.isdir(temp_dir):
    #     os.makedirs(temp_dir)
    # downloads_dir = os.path.expanduser('~/Downloads')
    # if not os.path.isdir(downloads_dir):
    #     os.makedirs(downloads_dir)

    # directories for images to get downloaded to
    # directories = [temp_dir, downloads_dir]

    # all possible valid sort types that can be used via cli
    time_sort_types = ['', 'hour', 'week', 'month', 'year', 'all']
    sort_types = ['hot', 'new', 'rising']
    sort_types.extend(['top'+t for t in time_sort_types])
    sort_types.extend(['controversial'+t for t in time_sort_types])

    sort_types = ['--sort-type '+s_type for s_type in sort_types]

    # all_cli_combinations = [list(zip(x, subreddit_name)) for x in combinations(sort_types, len(sort_types))]
    all_cli_combinations = [itertools.product(sort_types, ['{} {}'.format(subreddit_name, temp_dir)])]
    all_parsed_args = []
    for cli_args in all_cli_combinations:
        all_parsed_args.append(list(parse_arguments(cli_args)))

    # args1 = ['--sort-type %s' % sort_types[0], subreddit_name, directories[1].replace('\n', '')]
    # cli_args = parse_arguments(args1)
    return all_parsed_args

def test_duplicates():
    all_parsed_args = get_parsed_args()
    pass
