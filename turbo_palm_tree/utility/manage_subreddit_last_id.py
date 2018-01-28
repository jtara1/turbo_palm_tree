"""This file contains functions to enable me to read or write last-reddit-id
associated with a subreddit, sort-type, and directory.
I originally wrote these for RedditImageGrab.
"""
import os
import logging
import json


def history_log(wdir=os.getcwd(), log_file='log_file.txt', mode='read',
                write_data=None):
    """Read python dictionary from or write python dictionary to a file

    :param wdir: directory for text file to be saved to
    :param log_file: name of text file (include .txt extension)
    :param mode: 'read', 'write', or 'append' are valid
    :param write_data: data that'll get written in the log_file
    :type write_data: dictionary (or list or set)

    :return: returns data read from or written to file (depending on mode)
    :rtype: dictionary

    .. note:: Big thanks to https://github.com/rachmadaniHaryono for helping
        cleanup & fix security of this function.
    """
    mode_dict = {
        'read': 'r',
        'write': 'w',
        'append': 'a'
    }
    if mode in mode_dict:
        # create folder, if it doesn't exist
        if not os.path.isdir(wdir):
            os.mkdir(wdir)

        with open(os.path.join(wdir, log_file), mode_dict[mode]) as f:
            if mode == 'read':
                return json.loads(f.read())
            else:
                f.write(json.dumps(write_data))
                return write_data
    else:
        logging.debug('history_log func: invalid mode (param #3)')
        return {}


def process_subreddit_last_id(subreddit, sort_type, dir, log_file,
                              verbose=False):
    """Open & update log_file to get last_id of subreddit of sort_type
    Creates log_file if no existing log file was found

    :param subreddit: name of subreddit
    :param sort_type: sort type of subreddit
    :param dir: directory log_file (& images) will be saved to
    :param log_file: name of log file
    :param verbose: prints extra messages

    :return: log_data (contains last ids of subreddits),
        last_id (for this subreddit, sort_type, & dir)
    :rtype: tuple
    """
    no_history = False
    try:
        # first: we try to open the log_file
        log_data = history_log(dir, log_file, 'read')

        # second: we check if the data loaded is a dictionary
        if not isinstance(log_data, dict):
            raise ValueError(
                log_data,
                'data from %s is not a dictionary, overwriting %s'
                % (log_file, log_file))

        # third: try loading last id for subreddit & sort_type
        if subreddit in log_data:
            if sort_type in log_data[subreddit]:
                last_id = log_data[subreddit][sort_type]['last-id']
            else:  # sort_type not in log_data but subreddit is
                no_history = True
                log_data[subreddit][sort_type] = {'last-id': ''}
        else:  # subreddit not listed as key in log_data
            no_history = True
            log_data[subreddit] = {sort_type: {'last-id': ''}}

    # py3 or py2 exception for dne file
    except (FileNotFoundError, IOError, FileExistsError):
        last_id = ''
        log_data = {
            subreddit: {
                sort_type: {
                    'last-id': ''
                }
            }
        }
        history_log(dir, log_file, 'write', log_data)
        if verbose:
            print('%s not found in %s, created new %s'
                  % (log_file, dir, log_file))

    except ValueError as e:
        if verbose:
            print('log_data:\n{}'.format(e.args))

    except Exception:
        print('-------WHAT HAPPENED IN %s PROCESSING-------?' % log_file)

    if no_history:
        last_id = ''
        log_data = history_log(dir, log_file, 'write', log_data)

    return log_data, last_id
