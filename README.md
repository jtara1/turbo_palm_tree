# turbo_palm_tree

Download images from subreddits.

## Requirements

* Python 3

#### Modules

* praw
* BeautifulSoup (bs4)


## Installation

Clone this repo somewhere, e.g.:

    git clone --recursive https://github.com/jtara1/turbo_palm_tree && cd turbo_palm_tree

Install Python 3 then the needed [modules](#Modules)

    pip install -r requirements.txt


## Usage

Run this to check CLI args and options

    python turbo_palm_tree.py

Then run the same python file with desired options and args

examples:

    python turbo_palm_tree.py pics my_folder_for_pics --limit 5 --sort-type topall

## Credits

* [nim901](https://github.com/nim901/gfycat) for the gfycat submodule
* [rachmadaniHaryono](https://github.com/rachmadaniHaryono) for deviantart
parsing submodule
* praw and BeautifulSoup contributers
* [jtara1](https://github.com/jtara1) for imgur_downloader and everything else

Inspired by [RedditImageGrab](https://github.com/jtara1/RedditImageGrab).
