#!/bin/usr/env python
#-*- coding:utf-8 -*-

import pymongo
from util import *

client = pymongo.MongoClient('localhost', 27017)

org_db = client['ptt_Food']
org_post_url_infos = org_db['post_url_infos']
org_post_detail_infos = org_db['post_detail_infos']

cleaned_db = client['ptt_Food_cleaned']
cleaned_post_url_infos = cleaned_db['post_url_infos']
cleaned_post_detail_infos = cleaned_db['post_detail_infos']

def getOrgTitle(url):
    for doc in org_post_detail_infos.find({'post_url': url}):
        return doc['title']

def main():
    parsed_count = 0
    k_count = 0
    for doc in cleaned_post_detail_infos.find():
        parsed_count = (parsed_count + 1)%1000
        if parsed_count == 0:
            k_count += 1
            print('Parsed: ' + str(k_count) + 'k docs')
        
        orgTitle = getOrgTitle(doc['post_url'])
        post_type = getPostType(orgTitle) if orgTitle is not None else getPostType(getTitleByPostUrl(orgTitle))
        if post_type == 'post':
            continue
        update_data = {
            'post_type': post_type
        }
        # print(orgTitle)
        # print(doc['post_url'])
        # print(update_data)
        # print()
        cleaned_post_detail_infos.update_one({'_id': doc['_id']}, {'$set': update_data})

if __name__ =='__main__':
    main()
    exit(0)