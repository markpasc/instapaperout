# instapaperout #

`instapaperout` is a command line tool for exporting an Instapaper archive to local files.


## Installation ##

`instapaperout` is a program for Python 3.

Install `instapaperout` as any other Python program:

    $ python setup.py install

If you don't want to install its dependencies system-wide, try installing it in a [virtual environment](http://www.virtualenv.org/).


## Theory ##

Instapaper provides three ways for a program to see your archive:

* a manually downloaded CSV export
* the Full API (subscribers only)
* the “secret” feeds for each folder

However, none of these provides a way to programmatically read your *entire* Instapaper archive:

* CSV exports are “Limited to your most recent 2,000 articles”, though actual results seem to vary by server load at the time of export.
* The Full API's `bookmarks/list` resource provides up to 500 bookmarks, with no option to paginate back.
* Secret feeds don't page either, offering only the last 10 bookmarks in a folder (or 50, if you are an Instapaper subscriber).

Of these, only the secret feeds provide an exact timestamp when the bookmark was added to its folder. Therefore `instapaperout` uses your secret feeds to record your Instapaper archive.

That means recording past the last 10 (or 50, if you subscribe to Instapaper) bookmarks with `instapaperout` is a **destructive** operation: you must manually delete the new bookmarks to add the less recent ones to the feed.

If you use `instapaperout` to record your whole archive, when you're done your Instapaper account will be **empty**.


## Configuring ##

Because `instapaperout` uses your secret Instapaper feeds, no configuration is necessary.


## Usage ##

To use `instapaperout`, you'll need the secret RSS URL of the Instapaper folder you want to save.

### Finding the RSS URL ###

Log into Instapaper on the web at instapaper.com and select the folder you want to export.

If your web browser supports it, click the “feed” or “RSS” button to go to the feed for that Instapaper folder. This is the RSS URL to use with `instapaperout`.

If your web browser doesn't support feeds directly, view the source of the page and look for the line (near the top, in the `<head>` section) that looks like:

    <link rel="alternate" type="application/rss+xml" title="RSS" href="/rss/453325/fJRvNR5e8TtQ43Pp5hWlkUx7wVS" />

Copy the link in the `href` attribute of that HTML tag. That is the RSS URL to use with `instapaperout`.

### Saving the folder ###

To run `instapaperout` provide the name of a directory to save to and a folder's secret RSS URL.

    $ instapaperout ./archive http://www.instapaper.com/rss/453325/fJRvNR5e8TtQ43Pp5hWlkUx7wVS
    Saved through 'Rands In Repose: The Second Test'. Continue? (Y/n)

`instapaperout` will save the bookmarks in the feed to files in the directory (here, `./archive`), then ask if you want to continue. If you aren't backing up the whole folder, or don't want to delete your bookmarks, answer “n”. Only the most recent bookmarks in the folder at that time (the most recent 10, or 50 if you're an Instapaper subscriber) are saved to that directory.

If you want to back up the entire folder, in the instapaper.com web site **manually delete** the most recent bookmarks, from the newest through and including the named one (in this example, `Rands In Repose: The Second Test`). Then enter “Y” or press enter.

    Saved through 'Rands In Repose: The Second Test'. Continue? (Y/n) Y
    Saved through 'No Joke: With Lumia, Nokia Crushes The iPhone'. Continue? (Y/n) Y
    Saved through 'Mule Design Studio’s Blog: Always Be Disclosing'. Continue? (Y/n) Y
    ...
    Saved through 'The Virtual Startup: Taking Flight'. Continue? (Y/n) Y
    $

The last listed item will be the last item in the folder. Delete through it and confirm again (“Y” or enter) and `instapaperout` will exit. The whole folder has now been downloaded to the named directory.

    $ ls -1 ./archive/ | wc -l
        2498
    $ ls -1 ./archive/ | head
    http-0fps-wordpress-com-2012-01-14-an-analysis-of-minecraft-like-engines-.json
    http-2dboy-com-2011-10-03-xbla-.json
    http-37signals-com-svn-posts-2845-exit-interview-newsvines-mike-davidson.json
    http-37signals-com-svn-posts-3018-api-design-for-humans.json
    http-37signals-com-svn-posts-3124-give-it-five-minutes.json
    http-37signals-com-svn-posts-3285.json
    http-37signals-com-svn-posts-3328-twitters-descent-into-the-extractive.json
    http-3lc3lc3lc-tumblr-com-post-51064842008-who-will-survive-in-america-who-will-survive-in.json
    http-512pixels-net-2013-04-greater-than-.json
    http-512pixels-net-creation-of-next-.json
    $ cat ./archive/http-512pixels-net-creation-of-next-.json
    {
        "created_at": "2012-04-30T06:58:21",
        "description": null,
        "title": "On the Creation of NeXT \u2014 512 Pixels",
        "url": "http://512pixels.net/creation-of-next/"
    }
    $

See `instapaperout --help` for full help.

### Upload to Pinboard (or somewhere else) ###

After exporting, use the `furthermore/pinboardin.py` script or one like it to import your archived bookmarks to [Pinboard](https://pinboard.in/) or another service.

    $ python furthermore/pinboardin.py markpasc ./unread/ --unread
    $ python furthermore/pinboardin.py markpasc ./starred/ --starred
    $ python furthermore/pinboardin.py -v -v markpasc ./archive/
    DEBUG Found 1582 .json files in ./archive/, let's get started!
    ...
    DEBUG Saved bookmark 'Typography for Lawyers' to pinboard
    DEBUG Saved bookmark 'The War for Catch-22 | Culture | Vanity Fair' to pinboard
    DEBUG Saved bookmark 'Vlambeer | Random level generation in Wasteland Kings' to pinboard
    ^C
    $ python furthermore/pinboardin.py -v -v markpasc ./archive/ --skip http-www-vlambeer-com-2013-04-02-random-level-generation-in-wasteland-kings-.json
    DEBUG Skipping 1226 files to start after 'http-www-vlambeer-com-2013-04-02-random-level-generation-in-wasteland-kings-.json'
    DEBUG Found 356 .json files in ./archive/, let's get started!
    DEBUG Saved bookmark 'The Inside Story of How John Carter Was Doomed by Its First Trailer -- Vulture' to pinboard
    ...
    $

See `python furthermore/pinboardin.py --help` for its full help.
