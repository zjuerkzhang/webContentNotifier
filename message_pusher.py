#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import sys
import urllib
import requests

g_push_server = "https://my.messge.push.ur"

def push_message(subject, content):
    quoted_sub = urllib.parse.quote_plus(subject.replace('/', '-'))
    quoted_cont = urllib.parse.quote_plus(content.replace('/', '-'))
    url = g_push_server + quoted_sub + "/" + quoted_cont
    r = requests.post(url)
    if not r.status_code == 200:
        print("Fail to POST request %s, status_code: %d" % (url, r.status_code))

if __name__ == "__main__":
    subject = "empty subject"
    content = "empty content"
    if len(sys.argv) > 1:
        subject = sys.argv[1]
    if len(sys.argv) > 2:
        content = sys.argv[2]
    push_message(subject, content)
