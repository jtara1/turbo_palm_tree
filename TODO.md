### Priority 1

- [x] get basic functioning subreddit image downloader
- [x] cli
- [x] integrate database to keep track of aggregate downloads and metadata
- [ ] use submodule `image-match` to check if image is already downloaded

### Priority 2

- [ ] build on `ImageMatchManager` class to automate starting elasticsearch service,
creating index for es
- [x] setup logging
- [x] setup pytest
- [ ] add more submodules to `downloaders` folder to support downloading from
a wider variety of websites

### Priority 3

- [ ] add support for video downloading using module `youtube-dl`
- [ ] gui
