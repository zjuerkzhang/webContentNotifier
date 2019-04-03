#-*- coding: UTF-8 -*-
from bs4 import BeautifulSoup
from datetime import datetime
import requests

g_link = "http://www.google.com"

class general_fetcher(object):
    def __init__(self, config):
        self.config = config

    def fetch_content_from_link(self):
        r = requests.get(self.config['link'])
        if r.status_code != 200:
            return None
        r.encoding = "gb2312"
        return BeautifulSoup(r.text, 'html5lib')

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

