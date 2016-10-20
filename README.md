# turbo_palm_tree

Download images from subreddits.

Currently supports downloading from the following sites:
* imgur
* deviantart
* gfycat
* reddituploads
* [any url that ends with a media file extension]

## Requirements

* Python 3

#### Modules

* praw
* BeautifulSoup (bs4)


## Installation

Note, this repo has a few other git submodules so be sure to use `--recursive`
option with `git clone` to clone those in addition to this repo.

Clone this repo somewhere, e.g.:

    git clone --recursive https://github.com/jtara1/turbo_palm_tree && cd turbo_palm_tree

Install Python 3 then the needed [modules](#Modules)

    pip3 install -r requirements.txt


## Usage

Run this to check CLI args and options

    python3 turbo_palm_tree.py

Then run the same python file with desired options and args

examples:

    python3 turbo_palm_tree.py pics my_folder_for_pics --limit 5 --sort-type topall

#### Command Line Interface

    usage: turbo_palm_tree.py [-h] [--sort-type s] [--limit l] [--prev-id id]
                              [--restart] [--debug]
                              <subreddit> [<directory>]

    Downloads image files from the specified subreddit or list of subreddits.

    positional arguments:
      <subreddit>           Subreddit or subreddit list file name
      <directory>           Directory to save images in

    optional arguments:
      -h, --help            show this help message and exit
      --sort-type s, -s s   Sort type for subreddit
      --limit l, --num l, -l l
                            Number of submissions to download from
      --prev-id id, --last-id id
                            Begin downloading from the submission after the given
                            reddit id
      --restart, -r         Begin downloading from the beggining
      --debug, -d           Enable debug mode


## Credits

* [nim901](https://github.com/nim901/gfycat) for the gfycat submodule
* [rachmadaniHaryono](https://github.com/rachmadaniHaryono) for deviantart
parsing submodule
* praw and BeautifulSoup contributers
* [jtara1](https://github.com/jtara1) for imgur_downloader and everything else

Inspired by [RedditImageGrab](https://github.com/jtara1/RedditImageGrab).
