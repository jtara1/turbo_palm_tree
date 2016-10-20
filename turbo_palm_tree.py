# @Author: jtara1
# @Date:   14-Oct-2016
# @Email:  jtara@tuta.io

"""Initializes program"""

import os, sys, time
import logging
import pprint

from utility.parse_arguments import parse_arguments
from utility.get_subreddit_submissions import GetSubredditSubmissions
from utility.download_subreddit_submissions import DownloadSubredditSubmissions


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


if __name__ == "__main__":
    # pass raw command line args to parse_arguments function
    args = parse_arguments(['--help'] if len(sys.argv) == 1 else sys.argv[1:])

    # setup logging
    logging.basicConfig(filename='status_report.log',
        format='%(levelname)s | %(name)s | %(asctime)s | %(message)s',
        datefmt='%m/%d/%y %H:%M:%S',
        level=logging.DEBUG if args.debug else logging.INFO)
    log = logging.getLogger('turbo_palm_tree')
    log.info('cli args = %s' % args)

    # create directory if not yet created
    if not os.path.isdir(args.directory):
        os.makedirs(args.directory)

    download_submissions(subreddit=args.subreddit,
        path=args.directory, sort_type=args.sort_type, limit=args.limit,
        previous_id=args.prev_id, debug=args.debug)

    # get_submissions(subreddit=args.subreddit,
    #     path=args.directory, sort_type=args.sort_type, limit=args.limit,
    #     previous_id=args.prev_id, debug=args.debug)
