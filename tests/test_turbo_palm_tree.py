import random
import pytest
from turbo_palm_tree.utility.parse_arguments import parse_arguments, SubredditSortTypes
import os
import time


class TestClass:

    subreddit_url = "https://www.reddit.com/r/jtaraTest/"
    subreddit_name = "jtaratest"

    def get_random_parsed_arg(self):
        """Returns a parsed arg with a random sort type"""
        def get_random_sort_type():
            """Return a random sort types drawing from the enum class of all possible sort types"""
            sort_types = list(st.value for st in SubredditSortTypes)
            sort_types.extend(SubredditSortTypes.top.advanced_sorts() +
                              SubredditSortTypes.controversial.advanced_sorts())
            return sort_types[random.randrange(0, len(sort_types))]

        temp_dir = os.path.join(os.getcwd(), 'temp_test_downloads')
        sort_type = get_random_sort_type()
        return (sort_type, 'jtaraTest', temp_dir,
                parse_arguments(['--sort-type', sort_type, self.subreddit_name, temp_dir]))

    def test_parsed_args(self):
        sort_type, sr_name, path, args = self.get_random_parsed_arg()
        assert sort_type == args.sort_type
        assert args.subreddit == sr_name
        assert path == args.directory
