#!/usr/bin/env python
#-*- coding:utf-8 -*-

def get_(self):
    start_link = 'https://www.ptt.cc/bbs/Food/index1.html'

    counter = 0
    next_page_link = start_link
    while next_page_link:
        menu_page_data, next_page_link = self.get_menu_page_info(next_page_link)
        url_manager.add_new_url_infos(menu_page_data)
        print(menu_page_data)

        if counter >= 10:
            break
        counter+=1

def gen():
    for i in range(10):
        yield i
    

def main():
    a = [i for i in gen()]
    print(a)

if __name__ == '__main__':
    main()
    exit(0)