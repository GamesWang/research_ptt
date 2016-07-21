#!/usr/bin/env python
#-*- coding:utf-8 -*-

from module_config import *
from link_extractor import LinkExtractor
from url_manager import *
from html_parser import PttPostParser
import threadpool
import time
from multiprocessing import Process
from util import *

# 可以改一下寫法
# create process to extract post url
# then use multithread there
# Process(link_extractor.run)

#     threadPool(10)
#     while True:
#         get menu page urls
#             if > maximum page index:
#                 break
#         make request
#         put request
#         wait()

# create process to get detail post info
# then use multithread there
# Process(post_parser.run)
#     threadPool(10)
#     while True:
#         get unvisited urls
#             if 0:
#                 if None == refresh_new_and_old_urls:
#                     break
#         make request
#         put request
#         wait()

def main():

    link_extractor = LinkExtractor()
    post_parser = PttPostParser()

    try:
        start_page = 9770
        end_page = 13175
        p_link_extractor = Process(target=link_extractor.run, args=(MENU_PAGE_URL, start_page, end_page, 5))
        p_link_extractor.start()
        
        time.sleep(THREAD_REQUEST_SLEEP_INTERVAL)

        p_post_parser = Process(target=post_parser.run, args=(5,))
        p_post_parser.start()

        p_link_extractor.join()
        p_post_parser.join()

    except Exception as e:
        logRecord('[Exception] ' + str(e), 'gossip.craw.log')
        print('[Exception] ' + str(e))

if __name__ == '__main__':
    main()
    exit(0)
