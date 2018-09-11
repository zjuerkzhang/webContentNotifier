#-*- coding: UTF-8 -*-
import urllib2
from bs4 import BeautifulSoup
from datetime import datetime

g_link = "http://www.google.com"

class general_fetcher(object):
    def __init__(self, config):
        self.config = config

    def fetch_content_from_link(self):
        hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
               'Accept-Encoding': 'none',
               'Accept-Language': 'en-US,en;q=0.8',
                'Connection': 'keep-alive'}
        req = urllib2.Request(self.config['link'], headers=hdr)
        try:
            page = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            print e.code
            print e.read()
            return None
        return BeautifulSoup(page, 'html5lib')

    def get_interested_content(self):
        soup = self.fetch_content_from_link()
        if soup:
            return soup.prettify()
        else:
            return ""

if __name__ == "__main__":
    config = {}
    config['link'] = "http://www.google.com"
    fetcher = general_fetcher(config)
    print fetcher.get_interested_content()

