import pytest
import turbo_palm_tree
from turbo_palm_tree.utility.parse_arguments import parse_arguments
import os
import sys
import time


subreddit_url = "https://www.reddit.com/r/jtaraTest/"
subreddit_name = "jtaratest"

@pytest.fixture
def setup_test():
    pass

def test_cli_args():
    downloads_dir = os.path.expanduser('~/Downloads')
    cwd = os.getcwd()
    if not os.path.isdir(downloads_dir):
        os.mkdirs(downloads_dir)

    directories = [cwd, downloads_dir]
    time_sort_types = ['', 'hour', 'week', 'month', 'year', 'all']
    sort_types = ['hot', 'new', 'rising']
    sort_types.extend(['top'+t for t in time_sort_types]).extend(['controversial'+t for t in time_sort_types])

    args1 = ['--sort-type %s' % sort_types[0], subreddit_name, directories[0]]
    cli_args = parse_arguments(args1)
    assert cli_args.sort_type == sort_types[0]
    assert cli_args.subreddit == subreddit_name
    assert cli_args.directory == directories[0]

def test_duplicates():
    pass
