#!/usr/bin/env python
#-*- coding:utf-8 -*-

from module_config import *
from link_extractor import LinkExtractor
from url_manager import *
from html_parser import PttPostParser
from util import logRecord
import threadpool
import time

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

    threadPool = threadpool.ThreadPool(NUM_THREAD)

    loop = 0
    while True:
        try:

            # link extract
            if REQUEST_BATCH_SIZE*loop < MAXIMUM_MENU_PAGE:
                menu_page_urls = [MENU_PAGE_URL.format(i) for i in range(REQUEST_BATCH_SIZE*loop + 1, REQUEST_BATCH_SIZE*(loop+1) + 1)]
                requests = threadpool.makeRequests(link_extractor.fetch_menu_page_links, menu_page_urls)
                [threadPool.putRequest(req) for req in requests]
                print('Get Menu Page %d to %d.'%(REQUEST_BATCH_SIZE*loop, REQUEST_BATCH_SIZE*(loop+1)))
                loop += 1

            time.sleep(THREAD_REQUEST_SLEEP_INTERVAL)

            # detail post extract
            post_urls = url_manager.get_batch_new_urls(REQUEST_BATCH_SIZE)
            requests = threadpool.makeRequests(post_parser.get_post_detail_info, post_urls)
            [threadPool.putRequest(req) for req in requests]
            
            print('Visited Post Count: %d '%(post_url_infos.find({'visited':1}).count()))

            if not url_manager.has_new_url() and not url_manager.refresh_new_and_old_urls():
                print('Task Done')
                logRecord('Task Done')
                break

        except Exception as e:
            logRecord('[Exception] ' + str(e))
            print('[Exception] ' + str(e))

    threadPool.wait()

if __name__ == '__main__':
    main()
    exit(0)
