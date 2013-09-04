from datetime import datetime
import json
import logging
import os
from os.path import join
import re
from urllib.parse import urljoin
from xml.etree import ElementTree

import argh
from argh.interaction import confirm
import arghlog
import requests


def instapaper_out(exportpath: 'name of the directory to export to',
                   rss_url: 'URL of the RSS file to same items from',
                   noinput: "save only the first results and don't ask for input" =False):
    os.makedirs(exportpath, exist_ok=True)

    # Make sure the RSS URL is a whole URL.
    rss_url = urljoin('http://www.instapaper.com/', rss_url)

    while True:
        res = requests.get(rss_url)
        res.raise_for_status()
        root = ElementTree.fromstring(res.content)

        items = root.findall('./channel/item')
        if not items:
            logging.debug("No items found in the feed, stopping!")
            break
        for item_node in items:
            url = item_node.find('link').text
            timestamp = item_node.find('pubDate').text
            # e.g. Fri, 30 Aug 2013 16:50:51
            created_at = datetime.strptime(timestamp, '%a, %d %b %Y %H:%M:%S')

            item = {
                'title': item_node.find('title').text,
                'url': url,
                'description': item_node.find('description').text,
                'created_at': created_at.isoformat(),
            }

            filename = re.sub(r'\W+', '-', url) + '.json'
            with open(join(exportpath, filename), 'w') as f:
                json.dump(item, f, sort_keys=True, indent=4)
            logging.debug("Wrote %r to %s", item['title'], filename)

        if noinput or not confirm("Saved through '{}'. Continue".format(item['title']), default=True):
            logging.debug("Oops, user answered no, stopping!")
            break

    logging.debug("Finished.")


def main():
    parser = argh.ArghParser()
    arghlog.add_logging(parser)
    parser.set_default_command(instapaper_out)
    parser.dispatch()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger().setLevel(logging.DEBUG)
    main()
