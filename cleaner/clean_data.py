#!/bin/usr/env python
#-*- coding:utf-8 -*-

from util import *
from dbconnect import *

def getDataFromDB(outFile, url):
    res = {}
    for data in post_detail_infos.find({'post_url':url}, {'_id':0}):
        res = data

    with open(outFile, 'w') as f:
        json.dump(res, f)

# url = 'https://www.ptt.cc/bbs/Food/M.1331565910.A.A10.html'
# outFile = 'ptt_post2.txt'
# getDataFromDB(outFile, url)
# clean detail info table

def main():
        parsed_count = 0
        k_count = 0
        for doc in post_detail_infos.find({'parsed':{'$ne':1}}):
            parsed_count = (parsed_count + 1)%1000
            if parsed_count == 0:
                k_count += 1
                print('Parsed: ' + str(k_count) + 'k docs')

            try:
                author = getAuthorByPostUrl(doc['post_url'])
                nickname = getNickName(doc['author']) if doc['author'] else None
                body_content = bodyContentParse(doc['body_content'])
                title = parseTitle(doc['title']) if doc['title'] else parseTitle(getTitleByPostUrl(doc['post_url']))
                post_type = getPostType(title) # ['post', 'reply', 'forward']
                post_date_simple = parseDateToSimpleDate(doc['post_date_time']) if doc['post_date_time'] else None
                post_date_struct = parseDateToStructTime(doc['post_date_time']) if doc['post_date_time'] else None

                new_other_infos = []
                for other_info in doc['other_infos']:
                    new_other_infos.append(other_info.strip())

                new_push_infos = []
                for push_info in doc['push_infos']:
                    data = {
                        'push_floor': push_info['push_floor'],
                        'push_date_time': push_info['push_date_time'].strip(),
                        'push_content': push_info['push_content'].strip(),
                        'push_tag': push_info['push_tag'].strip(),
                        'push_author': push_info['push_author'].strip(),
                    }
                    new_push_infos.append(data)

                update_data = {
                        'author': author,
                        'nickname': nickname,
                        'body_content' : body_content,
                        'title': title,
                        'post_type': post_type,
                        'post_date_simple': post_date_simple,
                        'post_date_struct': post_date_struct,
                        'other_infos': new_other_infos,
                        'push_infos': new_push_infos,
                        'parsed' : 1
                    }

                # print(doc['post_url'])
                # print(update_data)

                post_detail_infos.update_one({'_id': doc['_id']}, {'$set': update_data})

            except Exception as e:
                print('[Exception] post_url: ' + doc['post_url'] + str(e))
                logRecord('[Exception] post_url: ' + doc['post_url'] + str(e), 'clean.log')


if __name__ == '__main__':
    main()
    exit(0)