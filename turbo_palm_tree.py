# @Author: jtara1
# @Date:   14-Oct-2016
# @Email:  jtara@tuta.io

"""Initializes program"""

import os, sys, time
import logging
import pprint

from utility.parse_arguments import parse_arguments
from utility.get_subreddit_submissions import GetSubredditSubmissions


if __name__ == "__main__":
    # pass raw command line args to parse_arguments function
    args = parse_arguments(['--help'] if len(sys.argv) == 1 else sys.argv[1:])

    # setup logging
    logging.basicConfig(filename='status_report.log',
        format='%(levelname)s|%(asctime)s|%(message)s',
        datefmt='%m/%d/%y %H:%M:%S',
        level=logging.DEBUG if args.debug else logging.INFO)
    log = logging.getLogger('turbo_palm_tree')
    log.info('args = %s' % args)

    # get submissions from a subreddit
    getter = GetSubredditSubmissions(args.subreddit, args.directory,
         args.sort_type, args.limit, args.prev_id)
    submissions = getter.get_submissions()
    submissions2 = getter.get_submissions_info()

    ## pretty printer
    pp = pprint.PrettyPrinter(indent=4)

    # print and log the id and url of each submission
    # for submission in submissions:
    #     # print(submission.title)
    #     # print(submission.score)
    #     print('fullname=%s, url=%s' % (submission.fullname, submission.url))
    #     log.debug('fullname (id), url = %s, %s' % (
    #         submission.fullname, submission.url))

    for s in submissions2:
        pp.pprint(s)
