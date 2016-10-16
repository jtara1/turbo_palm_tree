# @Author: j
# @Date:   14-Oct-2016
# @Email:  jtara@tuta.io
# @Last modified by:   j
# @Last modified time: 14-Oct-2016

"""Initializes program"""

import os, sys, time
from utility.parse_arguments import parse_arguments
from utility.get_subreddit_submissions import GetSubredditSubmissions

if __name__ == "__main__":
    args = parse_arguments(['--help'] if len(sys.argv) == 1 else sys.argv[1:])
    print(args)
    getter = GetSubredditSubmissions(args.subreddit, args.directory,
         args.sort_type, numb_submissions=25)
    getter.get_submissions()
