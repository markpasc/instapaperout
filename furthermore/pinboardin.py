"""

pinboardin.py
=============

Imports an `instapaperout` export to Pinboard.

"""


import getpass
import json
import logging
import os
from os.path import join
import time

import argh
import arghlog
import requests
from requests.auth import HTTPBasicAuth


__version__ = '1.0'


BLACK_STAR = u'\u2605'


def pinboardin(username: 'pinboard account to import bookmarks to',
               exportdir: 'directory of instapaperout export to import',
               unread: 'mark imported bookmarks as unread' =False,
               starred: 'tag imported bookmarks with a Unicode star' =False,
               skip: 'filename to skip through and continue saving after' =None):
    """Import an `instapaperout` export to Pinboard."""
    req = requests.Session()
    req.headers.update({'user-agent': 'instapaperout-pinboardin/{}'.format(__version__)})

    try:
        password = getpass.getpass('Password for {}: '.format(username))
    except KeyboardInterrupt:
        return
    req.auth = HTTPBasicAuth(username, password)

    def request(*args, **kwargs):
        delay = 3
        while True:
            time.sleep(delay)
            res = req.get(*args, **kwargs)
            if res.status_code != 429:
                break
            delay *= 2
            logging.debug("Got a 429 Too Many Requests response, slowing our roll to %d secs", delay)
        return res

    filenames = [x for x in os.listdir(exportdir) if x.endswith('.json')]
    if skip:
        try:
            skip_in_filenames = filenames.index(skip)
        except ValueError:
            raise argh.CommandError("File '{}' is not in the export".format(skip))
        del filenames[:skip_in_filenames+1]
        logging.debug("Skipping %d files to start after %r", skip_in_filenames+1, skip)
    logging.debug("Found %d .json files in %s, let's get started!", len(filenames), exportdir)

    for filename in filenames:
        filepath = join(exportdir, filename)
        with open(filepath, 'r') as f:
            data = json.load(f)

        title = data['title'] or data['url']
        query = {
            'format': 'json',
            'url': data['url'],
            'description': title,
            'replace': 'no',
            'dt': data['created_at'] + 'Z',
        }
        if data['description']:
            query['extended'] = data['description']
        if unread:
            query['toread'] = 'yes'
        if starred:
            query['tags'] = BLACK_STAR

        res = request('https://api.pinboard.in/v1/posts/add', params=query)
        res.raise_for_status()

        result = res.json()
        if result['result_code'] == 'done':
            logging.debug("Saved bookmark '%s' to pinboard", title)
            continue

        # Handle bookmarks that already exist specially.
        if result['result_code'] != 'item already exists':
            raise ValueError("Unexpected error: {}".format(result['result_code']))

        if not unread and not starred:
            # No special handling, so the bookmark already existing is fine.
            logging.debug("Bookmark '%s' already existed but that's fine", title)
            continue

        # If the user asked to make them unread or starred, then make sure they're unread or starred.
        query = {
            'format': 'json',
            'url': data['url'],
        }
        res = request('https://api.pinboard.in/v1/posts/get', params=query)
        result = res.json()
        post = result['posts'][0]

        need_to_replace = False
        post_tags, post_toread = post['tags'], post['toread']
        if starred and BLACK_STAR not in post_tags.split():
            need_to_replace = True
            post_tags = ' '.join((post_tags, BLACK_STAR))
        if unread and post_toread != 'yes':
            need_to_replace = True
            post_toread = 'yes'

        if not need_to_replace:
            logging.debug("Bookmark '%s' already existed and needed no update, yay", title)
            continue

        query.update({
            'replace': 'yes',

            'tags': post_tags,
            'toread': post_toread,
            # Keep all these old settings of the existing bookmark.
            'description': post['description'],
            'extended': post['extended'],
            'shared': post['shared'],
            'dt': post['time'],
        })
        res = request('https://api.pinboard.in/v1/posts/add', params=query)
        res.raise_for_status()
        logging.debug("Updated bookmark '%s' for unread/starredness", title)


def main():
    parser = argh.ArghParser()
    arghlog.add_logging(parser)
    parser.set_default_command(pinboardin)

    # But first don't spam us with requests' debug info, we really only want our debug info.
    logging.getLogger('requests').propagate = False

    parser.dispatch()


if __name__ == '__main__':
    main()
