# @Author: jtara1
# @Date:   14-Oct-2016
# @Email:  jtara@tuta.io

"""Initializes program"""

import os
import sys
import logging
import pprint
from gooey import Gooey

from turbo_palm_tree.utility.parse_arguments import parse_arguments
from turbo_palm_tree.utility.get_subreddit_submissions import GetSubredditSubmissions
from turbo_palm_tree.utility.download_subreddit_submissions import DownloadSubredditSubmissions
from turbo_palm_tree.utility.parse_subreddit_list import parse_subreddit_list
from turbo_palm_tree.utility.general_utility import start_elasticsearch


def get_submissions(*args, **kwargs):
    getter = GetSubredditSubmissions(*args, **kwargs)
    submissions = getter.get_submissions_info()
    ## pretty printer
    pp = pprint.PrettyPrinter(indent=4)
    for s in submissions:
        pp.pprint(s)


def download_submissions(*args, **kwargs):
    downloader = DownloadSubredditSubmissions(*args, **kwargs)
    downloader.download()


def gooey_enabler(main_func):
    """
    Runs and returns the main_func if GUI flag not found in cli args
    else it returns the reference to the main_func thus continuing to
    execute app with Gooey decorator
    :param main_func: func for this decorator
    """
    # if we're not enabling the Gooey GUI, bypass the decorator by calling the main func
    if not ('--gui' in sys.argv or '-g' in sys.argv):
        return main_func()
    else:
        return main_func


@Gooey
@gooey_enabler
def main():
    """
    With the decorators:
    main = Gooey(gooey_enabler(main))
    This is the main entry point to the app that setups logging, cli args, and begins the app
    """

    # pass raw command line args to parse_arguments function
    args = parse_arguments(['--help'] if len(sys.argv) == 1 else sys.argv[1:])

    # setup logging
    logging.basicConfig(
        filename='status_report.log',
        format='%(levelname)s | %(name)s | %(asctime)s | %(message)s',
        datefmt='%m/%d/%y %H:%M:%S',
        level=logging.DEBUG if args.debug else logging.INFO)
    log = logging.getLogger('tpt')
    log.info('cli args = %s' % args)

    if not args.disable_image_match:
        # start elasticsearch service if not already started
        start_elasticsearch()

    # check if subreddit or local file for list of subreddits was passed
    list_file_extensions = ('.txt')
    if os.path.isfile(args.subreddit) and args.subreddit.endswith(list_file_extensions):
        subreddit_list = parse_subreddit_list(args.subreddit, args.directory)
    else:
        subreddit_list = [(args.subreddit, args.directory)]

    # iterate over the list of subreddit(s) and download from each of them
    for subreddit, path in subreddit_list:
        # create directory if not yet created
        if not os.path.isdir(path):
            os.makedirs(path)

        download_submissions(
            subreddit=subreddit,
            path=path, sort_type=args.sort_type, limit=args.limit,
            previous_id=args.prev_id, disable_db=args.disable_database, disable_im=args.disable_image_match,
            debug=args.debug)

    sys.exit(0)


if __name__ == "__main__":
    main()
