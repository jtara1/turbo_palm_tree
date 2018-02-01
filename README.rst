turbo\_palm\_tree
=================

Download images from subreddits.

Features
^^^^^^^^

-  Pass a subreddit name or text file containing subreddits on each line
   to be processed (see subreddit-list-examples folder for examples)
-  Resume downloading from last submission if same subreddit, directory,
   and sort type is used
-  logging (info, debug, and warning)
-  metadata recording of each submission in database (see file
   ``turbo_palm_tree/database_manager/tpt.db``)

Optionally
----------

-  Specify directory to download to
-  Start downloading from beginning with ``--restart`` or ``-r``
-  Get submissions sorted (just as reddit handles sorting)
-  Download image/video from ``--limit l`` number of submission from
   (each) subreddit (defaults to 5)
-  Pass a reddit id (or fullname) with ``--prev-id id`` cli option to
   begin downloading after the submission the passed id points to

Image/Video scraping from
^^^^^^^^^^^^^^^^^^^^^^^^^

-  imgur
-  deviantart
-  gfycat
-  reddituploads
-  `gallery-dl supported sites <https://github.com/mikf/gallery-dl/blob/master/docs/supportedsites.rst>`__

Requirements
------------

-  Python 3

Modules
^^^^^^^

See ``requirements.txt``

Installation
------------

Clone this repo somewhere, e.g.:

::

    git clone https://github.com/jtara1/turbo_palm_tree
    cd turbo_palm_tree

Install Python 3 then the needed `modules <#Modules>`__

::

    pip install -r requirements.txt

Usage from command line
-----------------------

First, change directory to where ``run.py`` is located.

Run this to check CLI args and options

::

    python run.py

Then run the same python file with desired options and args

examples:

::

    python run.py pics

    python run.py pics /home/james/Downloads/pics -l 5

    python run.py pics my_folder_for_pics --limit 5 --sort-type topall

If you install it via ``pip`` or ``python setup.py install`` then you can use ``tpt`` as the alias to run turbo_palm_tree

::

    tpt pics -l 5


Usage as an API
---------------
Install via pip

::

    $ pip install git+https://github.com/jtara1/turbo_palm_tree

    $ python

    >>> from turbo_palm_tree import DownloadSubredditSubmissions as Tpt

    >>> downloader = Tpt('pics', path='my_downloads/', sort_type='hot', limit=5)

    >>> downloader.download()


Command Line Interface
^^^^^^^^^^^^^^^^^^^^^^

::

    usage: run.py [-h] [--sort-type <s>] [--limit <l>] [--prev-id <id>]
                  [--restart] [--gui] [--ignore-gooey] [--disable-database]
                  [--disable-image-match] [--debug]
                  <subreddit> [<directory>]

    Downloads image files from the specified subreddit or list of subreddits.

    positional arguments:
      <subreddit>           Subreddit or subreddit list file name
      <directory>           Directory to save images in; defaults to cwd joined
                            with name of subreddit

    optional arguments:
      -h, --help            show this help message and exit
      --sort-type <s>, -s <s>
                            Sort type for subreddit
      --limit <l>, --num <l>, -l <l>
                            Number of submissions to download from; defaults to 5
      --prev-id <id>, --last-id <id>
                            Begin downloading from the submission after the given
                            reddit id
      --restart, -r         Begin downloading from the beggining
      --gui, -g             Enables use of Gooey module to provide a GUI for use
                            of application
      --ignore-gooey        Use -g or --gui for GUI enabling instead (GUI disable
                            by default). This disables Gooey GUI wrapper for CLI.
      --disable-database, --disable-db, --no-db
                            Disable use of database to record data of each
                            submission downloaded
      --disable-image-match, --disable-im, --no-im
                            Disable use of elasticsearch and image-match modules
                            which delete duplicate images
      --debug, -d           Enable debug mode


Credits
-------

-  `rachmadaniHaryono <https://github.com/rachmadaniHaryono>`__ for
   deviantart parsing submodule
-  praw and BeautifulSoup contributers
-  `jtara1 <https://github.com/jtara1>`__ for imgur\_downloader and
-  gallery-dl maintainers

Inspired by
`RedditImageGrab <https://github.com/jtara1/RedditImageGrab>`__.