#!/usr/bin/env python
#-*- coding:utf-8 -*-

import requests
import time
from module_config import *

class HtmlDownloader(object):
    def download(self, url):
        if url == None:
            return None

        return self._reTryConnect(url)

    def _reTryConnect(self, url, retry_times=DEFAULT_RETRY_TIMES):
        i = 0
        while i <  retry_times:
            res = requests.get(url)
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