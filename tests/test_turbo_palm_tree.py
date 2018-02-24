import shutil
import random
import sys
import os
from os.path import basename
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from glob import glob
from turbo_palm_tree.utility.parse_arguments \
    import parse_arguments, SubredditSortTypes
from turbo_palm_tree.utility.download_subreddit_submissions \
    import DownloadSubredditSubmissions
from turbo_palm_tree.utility.general_utility \
    import remove_file_extension, slugify
import time


class TestClass:

    subreddit_url = "https://www.reddit.com/r/jtaraTest/"
    subreddit_name = "jtaratest"
    directory = os.path.abspath('_temp_test_downloads')

    def get_random_parsed_arg(self):
        """Returns a parsed arg with a random sort type"""
        def get_random_sort_type():
            """Return a random sort types drawing from the enum class
            of all possible sort types
            """
            sort_types = list(st.value for st in SubredditSortTypes)
            sort_types.extend(
                SubredditSortTypes.top.advanced_sorts() +
                SubredditSortTypes.controversial.advanced_sorts())
            return sort_types[random.randrange(0, len(sort_types))]

        temp_dir = os.path.join(os.getcwd(), 'temp_test_downloads')
        sort_type = get_random_sort_type()
        return (sort_type, 'jtaraTest', temp_dir,
                parse_arguments(['--sort-type', sort_type,
                                 self.subreddit_name, temp_dir]))

    @staticmethod
    def _remove_old_files_decorator():
        if os.path.isdir(TestClass.directory):
            shutil.rmtree(TestClass.directory)

    def test_parsed_args(self):
        sort_type, sr_name, path, args = self.get_random_parsed_arg()
        assert sort_type == args.sort_type
        assert args.subreddit == sr_name
        assert path == args.directory

    def test_downloader(self):
        self._remove_old_files_decorator()
        downloader = DownloadSubredditSubmissions(
            subreddit=self.subreddit_name, path=self.directory,
            sort_type='hot', limit=5, debug=True, disable_db=True,
            disable_im=True
        )
        downloader.download()
        valid_names = [
            '4 beans in 1 album', '._history.txt', '.directory',
            'helmets save lives.jpg', 'rImaginaryCharacters link.jpg',
        ]
        for file in glob(os.path.join(self.directory, '*')):
            file_name = basename(file)
            print(file_name)
            if file_name.startswith('Lorem'):
                base_name_no_ext = remove_file_extension(file_name)
                lorem = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
                assert(base_name_no_ext in slugify(lorem))
            elif file_name.startswith(('2018', '2019', '2020')):
                print(file_name)
            else:
                assert(file_name in valid_names)

