# @Author: j
# @Date:   14-Oct-2016
# @Email:  jtara@tuta.io
# @Last modified by:   j
# @Last modified time: 14-Oct-2016

"""Initializes program"""

import os, sys, time
import logging

from utility.parse_arguments import parse_arguments
from utility.get_subreddit_submissions import GetSubredditSubmissions


if __name__ == "__main__":
    args = parse_arguments(['--help'] if len(sys.argv) == 1 else sys.argv[1:])
    logging.basicConfig(filename='status_report.log',
        format='%(levelname)s|%(asctime)s|%(message)s',
        datefmt='%m/%d/%y %H:%M:%S', level=logging.DEBUG)
    log = logging.getLogger('turbo_palm_tree')
    log.info('args = %s' % args)
    getter = GetSubredditSubmissions(args.subreddit, args.directory,
         args.sort_type, numb_submissions=5)
    getter.get_submissions()
