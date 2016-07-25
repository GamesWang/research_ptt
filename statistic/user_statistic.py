#!/bin/usr/env python
#-*- coding:utf-8 -*-

from module_config import *
from collections import defaultdict
from multiprocessing import Pool
import multiprocessing

def user_statistic(offset, limit):

    parsed_count = 0
    k_count = 0
    user_dict = {}
    for entry in post_detail_infos.find({'crawled_user_info':{'$ne':1}}).sort('_id', 1).skip(offset).limit(limit):
        parsed_count = (parsed_count + 1)%1000
        if parsed_count == 0:
            k_count += 1
            print('Parsed: ' + str(k_count) + 'k docs')

        post_author = entry['author']
        post_url = entry['post_url']
        push_infos = entry['push_infos']

        user_dict.setdefault(post_author, {})
        user_dict[post_author].setdefault('pushed_post', [])
        user_dict[post_author].setdefault('post_urls', [])

        user_dict[post_author]['post_urls'].append(post_url)

        # push_authors_dict = {
        #     push_user1: {
        #         url: '',
        #         push_contents: [],
        #         push_total_score:,
        #         push_negative_score:,
        #         push_positive_score:,
        #         push_neutral_score:,
        #     }
        # }        

        push_authors_dict = {}
        for push in push_infos:
            push_tag = push['push_tag']
            push_author = push['push_author']
            push_content = push['push_content']
            push_tag = push['push_tag']

            push_authors_dict.setdefault(push_author, {})
            push_authors_dict[push_author]['post_url'] = post_url
            push_authors_dict[push_author].setdefault('push_contents', []).append(push_content)
            push_authors_dict[push_author].setdefault('push_positive_score', 0)
            push_authors_dict[push_author].setdefault('push_negative_score', 0)
            push_authors_dict[push_author].setdefault('push_neutral_score', 0)
            push_authors_dict[push_author].setdefault('push_number', 0)

            if push_tag == '推':
                push_authors_dict[push_author]['push_positive_score'] += 1
            elif push_tag == '噓':
                push_authors_dict[push_author]['push_negative_score'] += 1
            elif push_tag == '→':
                push_authors_dict[push_author]['push_neutral_score'] += 1
            push_authors_dict[push_author]['push_number'] += 1

        for push_user in push_authors_dict:
            user_dict.setdefault(push_user, {})
            user_dict[push_user].setdefault('post_urls', [])
            user_dict[push_user].setdefault('pushed_post', [])
            user_dict[push_user]['pushed_post'].append(push_authors_dict[push_user])

        update_data = {
            'crawled_user_info': 1
        }
        # print(user_dict)
        post_detail_infos.update_one({'_id': entry['_id']}, {'$set': update_data})

    for user in user_dict:
        update_data = {
            '$addToSet': {
                'post_urls': {
                    '$each': user_dict[user]['post_urls']
                },
                'pushed_post': {
                    '$each': user_dict[user]['pushed_post']
                }
            }
        }
        # print(update_data)
        user_statistic_table.update_one({'_id': user}, update_data, True)

def main():
    # user_statistic(0, 50)

    num_process = 4
    pool = Pool(num_process)

    num_post = post_detail_infos.find({'crawled_user_info':{'$ne':1}}).count()
    print('Number to get user infos: ' + str(num_post))

    batch_size = int(num_post/num_process)
    print('Batch size: ' + str(batch_size))
    args = [(idx*batch_size, (idx+1)*batch_size) for idx in range(num_process)]
    pool.starmap(user_statistic, args)
    pool.close()
    pool.join()

if __name__ == '__main__':
    main()
    exit(0)