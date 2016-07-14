#!/usr/bin/env python
#-*- coding:utf-8 -*-
from html_downloader import HtmlDownloader
from url_manager import url_manager
from config import *
import threadpool

class LinkExtractor(object):
    def get_menu_page_info(self, menu_page_url):
        downloader = HtmlDownloader()
        html_text = downloader.download(menu_page_url)

        if html_text == None:
            return None

        return self.parse_menu_page_info(html_text)

    def parse_menu_page_info(self, html_text):
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

def main():

    menu_page_urls = ['https://www.ptt.cc/bbs/Food/index{}.html'.format(i) for i in range(1, 6000)]
    link_extractor = LinkExtractor()

    pool = threadpool.ThreadPool(5) 
    requests = threadpool.makeRequests(link_extractor.fetch_menu_page_links, menu_page_urls) 
    [pool.putRequest(req) for req in requests] 
    pool.wait() 


if __name__ == '__main__':
    main()
    exit(0)