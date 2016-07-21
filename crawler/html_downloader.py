#!/usr/bin/env python
#-*- coding:utf-8 -*-

import requests
from bs4 import BeautifulSoup
import time
from module_config import *
requests.packages.urllib3.disable_warnings()

class HtmlDownloader(object):
    def __init__(self):
        payload = {
            'from': '/bbs/' + PTT_BOARD + '/index.html',
            'yes': 'yes'
        }
        self.rs = requests.session()
        self.rs.post('https://www.ptt.cc/ask/over18', verify=False, data=payload)

    def download(self, url):
        if url == None:
            return None
        time.sleep(REQUEST_SLEEP_INTERVAL)
        return self._reTryConnect(url)

    def _reTryConnect(self, url, retry_times=DEFAULT_RETRY_TIMES):
        i = 0
        while i <  retry_times:
            res = self.rs.get(url, verify=False)
            if res.status_code == 200:
                return res.text
            time.sleep(RETRY_SLEEP_INTERVAL)
            i += 1
        return None

def main():
    # html_downloader = HtmlDownloader()
    # print(html_downloader.download('https://www.ptt.cc/bbs/Food/index1.html'))
    pass
    
if __name__ == '__main__':
    main()
    exit(0)