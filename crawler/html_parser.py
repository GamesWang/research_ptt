#!/usr/bin/env python
#-*- coding:utf-8 -*-
from html_downloader import HtmlDownloader
from module_config import *
from bs4 import BeautifulSoup

class PttPostParser(object):
    def __init__(self):
        self.html_downloader = HtmlDownloader()

    def get_post_detail_info(self, post_url):
        html_text = self.html_downloader.download(post_url)
        post_data = self.parse_post_detail_info(html_text)
        post_detail_infos.insert_one(post_data)
        post_url_infos.update_one({'post_url': post_url},{'$set':{'visited':1}})

    def parse_post_detail_info(self, html_text):
        if html_text is None:
            return None

        soup = BeautifulSoup(html_text, 'lxml')

        # post url
        post_url = soup.select('head > link[rel=canonical]')[0].get('href')

        # 標題部分，抓 author, title, post_date_time
        metalines = soup.select('.article-metaline')
        author, title, post_date_time = None, None, None
        for metaline in metalines:
            if metaline.select('.article-meta-tag') and metaline.select('.article-meta-tag')[0].text == '作者':
                author = metaline.select('.article-meta-value')[0].text if metaline.select('.article-meta-value') else None
            elif metaline.select('.article-meta-tag') and metaline.select('.article-meta-tag')[0].text == '標題':
                title = metaline.select('.article-meta-value')[0].text if metaline.select('.article-meta-value') else None
            elif metaline.select('.article-meta-tag') and metaline.select('.article-meta-tag')[0].text == '時間':
                post_date_time = metaline.select('.article-meta-value')[0].text if metaline.select('.article-meta-value') else None

        # 其他 infos
        other_infos = []
        others = soup.select('span.f2')
        for other in others:
            other_infos.append(other.text)

        # 推文資訊
        push_infos = []
        pushes = soup.select('.push')
        push_floor = 1
        for push in pushes:
            push_tag = push.select('.push-tag')[0].text if push.select('.push-tag') else None
            push_author = push.select('.push-userid')[0].text if push.select('.push-userid') else None
            push_content = push.select('.push-content')[0].text if push.select('.push-content') else None
            push_date_time = push.select('.push-ipdatetime')[0].text if push.select('.push-ipdatetime') else push.select('.push-ipdatetime')
            data = {
                'push_tag': push_tag,
                'push_author': push_author,
                'push_content': push_content,
                'push_date_time': push_date_time,
                'push_floor': push_floor
            }
            push_floor += 1
            push_infos.append(data)

        # 過濾已爬 tags 資訊
        ignore_tags = ['.article-metaline']
        for tag in soup.find_all(class_=['article-metaline','article-metaline-right','f2', 'push']):
            tag.replace_with('')

        # 主文
        body_content = soup.select('#main-content')[0].text.strip()

        post_info = {
            'title': title,
            'author': author,
            'post_date_time': post_date_time,
            'other_infos': other_infos,
            'body_content': body_content,
            'push_infos': push_infos,
            'post_url': post_url
        }

        return post_info

def main():
    post_parser = PttPostParser()
    data = post_parser.get_post_detail_info('https://www.ptt.cc/bbs/Food/M.1468296379.A.ACF.html')
    print(data)

if __name__ == '__main__':
    main()
    exit(0)