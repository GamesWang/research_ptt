#!/bin/usr/env python
#-*- coding:utf-8 -*-

import jieba
import jieba.analyse
from collections import Counter
from module_config import *
import re
import json

jieba.set_dictionary('../resource/dicts/dict.txt.big') # set 繁體辭典
jieba.load_userdict('../resource/dicts/ptt_words.txt') # load PTT 用語
jieba.load_userdict('../resource/dicts/restaurant.txt') # load 餐廳名稱
jieba.load_userdict('../resource/dicts/taiwan_area.txt') # load 台灣地名
jieba.load_userdict('../resource/dicts/taiwan_words.txt') # load 台灣 words
jieba.load_userdict('../resource/dicts/taiwan_party.txt') # load 台灣政黨
jieba.analyse.set_stop_words('../resource/dicts/mystopwords.txt') # set stopwords

# jieba.analyse.set_idf_path(file_name) # set idf

# ret = open("president_speech.txt", "r", encoding='utf-8').read()
# seglist = jieba.cut(ret, cut_all=False)
# tags = jieba.analyse.extract_tags(content, 10) # get top 10 tf-idf

# print(' '.join(seglist))

# print(Counter(list(seglist)))

def main():

    parsed_count = 0
    k_count = 0
    ip_pat = re.compile('.+From: (((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)).*')

    # {'segmented_title_and_body':{'$in':[None]}}
    for doc in post_detail_infos.find():
        parsed_count = (parsed_count + 1)%1000
        if parsed_count == 0:
            k_count += 1
            print('Parsed: ' + str(k_count) + 'k docs')
        
        try:
            post_ip = ''
            m = ip_pat.match(doc['body_content'])
            if m is not None:
                post_ip = m.group(1)
                doc['body_content'] = re.sub(post_ip, ' ', doc['body_content'])

            body_seglist = jieba.cut(doc['body_content'], cut_all=False)
            body_result = ' '.join(body_seglist)

            title_seglist = jieba.cut(doc['title'], cut_all=False)
            title_result = ' '.join(title_seglist)

            update_data = {
                'segmented_body': body_result + ' ' + post_ip,
                'segmented_title': title_result,
                'segmented_title_and_body': title_result + ' ' + body_result + ' ' + post_ip,
                'jieba_top30_tfidf': jieba.analyse.extract_tags(doc['title'] + ' ' + doc['body_content'], 30),
                'post_ip': post_ip,
                'word_statistic': str(dict(Counter((title_result + ' ' + body_result + ' ' + post_ip).split()))),
                'segmented': 1
            }
            # print(update_data)
            post_detail_infos.update_one({'_id': doc['_id']}, {'$set': update_data})

            # for elem in update_data:
            #     print(str(elem) + ': \n' + str(update_data[elem]))
            #     print()

        except Exception as e:
            print('[Exception] post_url: ' + doc['post_url'] + str(e))
            logRecord('[Exception] post_url: ' + doc['post_url'] + str(e), 'segment.gossip.log')


if __name__ == '__main__':
    main()
    exit(0)