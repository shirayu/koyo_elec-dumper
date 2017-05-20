#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Download koyo electric data
'''

import argparse
import urllib.request
import sys
import http.cookiejar
import re
import json
import codecs


LOGIN_URL = 'https://www.k-epco.net/koyo/portal'
LOGIN_POST_URL = 'https://www.k-epco.net/koyo/portal/login'
GRAPH_URL = 'https://www.k-epco.net/koyo/portal/graph/daily/?data_month='


def get_token(opener):
    '''
    Get login token
    '''
    res = opener.open(urllib.request.Request(url=LOGIN_URL))
    if res.status != 200:
        sys.exit(1)
    body = res.read().decode('utf8')
    token = re.search(r'name="_token" value="([^"]*)"', body).group(1)
    return token


def login(opener, token, email, password):
    '''
    login
    '''
    data = {
        '_token': token,
        'email': email,
        'password': password,
    }
    encoded_post_data = json.dumps(data).encode(encoding='ascii')
    res = opener.open(urllib.request.Request(url=LOGIN_POST_URL,
                                             headers={"Content-Type": "application/json"},
                                             data=encoded_post_data,
                                             method='POST'))
    body = res.read().decode('utf8')
    if res.status != 200 or "間違って" in body:
        sys.exit(1)


def get_page(opener, year, month):
    '''
    Get month data
    '''
    res = opener.open(urllib.request.Request(url="%s%04d%02d" % (GRAPH_URL, year, month)))
    if res.status != 200:
        sys.exit(1)
    body = res.read().decode('utf8')
    data = re.search(r'columns: (.*)\n', body).group(1).rstrip(',')
    return data


def operation(cfg, year, month):
    '''
    Stub
    '''

    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(
            http.cookiejar.CookieJar()))
    token = get_token(opener)
    login(opener, token, cfg["id"], cfg["password"])
    data = get_page(opener, year, month)
    return data


def main():
    '''
    Parse arguments
    '''
    oparser = argparse.ArgumentParser()
    oparser.add_argument("-c", "--config", dest="config", default=None, required=True)
    oparser.add_argument("-o", "--output", dest="output")
    oparser.add_argument("-y", "--year", dest="year", type=int, required=True)
    oparser.add_argument("-m", "--month", dest="month", type=int, required=True)
    opts = oparser.parse_args()

    cfg = None
    with open(opts.config) as fhdl:
        cfg = json.loads(fhdl.read())
    data = operation(cfg, opts.year, opts.month)

    with codecs.open(opts.output, "w", "utf8") as outf:
        outf.write(data)
        outf.write("\n")

if __name__ == '__main__':
    main()
