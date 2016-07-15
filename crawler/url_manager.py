#!/usr/bin/env python
#-*- coding:utf-8 -*-

from module_config import *

class UrlManager(object):
    def __init__(self):
        self.new_urls = set()
        self.old_urls = set()
        self.refresh_new_and_old_urls()
        
    def refresh_new_and_old_urls(self):
        for entry in post_url_infos.find({},{'_id':0, 'post_url':1, 'visited':1}):
            if entry.get('visited', 0) == 0:
                # unvisited
                self.new_urls.add(entry['post_url'])
            else:
                # already visited
                self.old_urls.add(entry['post_url'])

        return self.has_new_url()

    def add_new_url_info(self, url_info):
        url = url_info.get('post_url', None)
        if url_info is None:
            return
        if url not in self.new_urls and url not in self.old_urls:
            self.new_urls.add(url)
            post_url_infos.insert_one(url_info)
    
    def add_new_url_infos(self, url_infos):
        if url_infos is None or len(url_infos) == 0:
            return
        for url_info in url_infos:
            self.add_new_url_info(url_info)

    def has_new_url(self):
        return len(self.new_urls) != 0
        
    def get_new_url(self):
        if not self.has_new_url():
            return None
        new_url = self.new_urls.pop()
        self.old_urls.add(new_url)
        return new_url

    def get_batch_new_urls(self, batch_size):
        new_urls = []
        for _ in range(batch_size):
            if not self.has_new_url():
                break
            new_url = self.get_new_url()
            new_urls.append(new_url)

        return new_urls


url_manager = UrlManager()  
print('Post Url visited: %d, unvisited: %d'%(post_url_infos.find({'visited':1}).count(), post_url_infos.find({'visited':0}).count()))

def main():
    pass

if __name__ == '__main__':
    main()
    exit(0)