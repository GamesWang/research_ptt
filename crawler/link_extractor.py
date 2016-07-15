#!/usr/bin/env python
#-*- coding:utf-8 -*-
from html_downloader import HtmlDownloader
from url_manager import url_manager
from module_config import *
from bs4 import BeautifulSoup
import threadpool

class LinkExtractor(object):
    def __init__(self):
        self.counter = 0
        self.k_count = 0

    def get_menu_page_info(self, menu_page_url):
        if menu_page_url is None:
            return None

        downloader = HtmlDownloader()
        html_text = downloader.download(menu_page_url)

        if html_text == None:
            return None

        self.counter = (self.counter + 1)%100
        if self.counter == 0:
            self.k_count += 1
            print('Get Manu Pages: %d00'%(self.k_count))

        return self.parse_menu_page_info(html_text)

    def parse_menu_page_info(self, html_text):
        if html_text is None:
            return None

        soup = BeautifulSoup(html_text, 'lxml')

        menu_page_data = []
        for entry in soup.select('.r-ent'):
            data = {
                'title': entry.select('.title')[0].text.strip(),
                'post_url': PTT_HOST_URL + entry.select('.title > a')[0].get('href') if entry.select('.title > a') else None,
                'date': entry.select('.date')[0].text.strip(),
                'author': entry.select('.author')[0].text.strip(),
                'visited': 0
            }
            menu_page_data.append(data)
        return menu_page_data

    # 抓 post_links 到 post_url_infos table
    def fetch_menu_page_links(self, menu_page_url):
        menu_page_data = self.get_menu_page_info(menu_page_url)
        if menu_page_data != None:
            url_manager.add_new_url_infos(menu_page_data)

    def next_page(self, html_text):
        soup = BeautifulSoup(html_text, 'lxml')
        if soup.find_all('a', class_='btn wide', text='下頁 ›'):
            return PTT_HOST_URL + soup.find_all('a', class_='btn wide', text='下頁 ›')[0].get('href')
        return None

    def run(self, root_menu_page, max_menu_page_index=6000, threadNum=5):
        print('===================== start run extractor() ========================')
        try:
            pool = threadpool.ThreadPool(threadNum) 
            
            menu_page_urls = [root_menu_page.format(i) for i in range(1, max_menu_page_index)]
            requests = threadpool.makeRequests(self.fetch_menu_page_links, menu_page_urls) 
            [pool.putRequest(req) for req in requests] 
            pool.wait() 
        except:
            print('link_extractor excepttion')
            raise
def main():
    # link_extractor = LinkExtractor()

    # menu_page_urls = ['https://www.ptt.cc/bbs/Food/index{}.html'.format(i) for i in range(1, 6000)]

    # pool = threadpool.ThreadPool(5) 
    # requests = threadpool.makeRequests(link_extractor.fetch_menu_page_links, menu_page_urls) 
    # [pool.putRequest(req) for req in requests] 
    # pool.wait() 
    pass

if __name__ == '__main__':
    main()
    exit(0)