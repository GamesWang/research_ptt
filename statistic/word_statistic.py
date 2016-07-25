#!/bin/usr/env python
#-*- coding:utf-8 -*-

import sys
sys.path.append('../')
from collections import Counter
from module_config import *
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from monary import Monary
import pandas as pd
import numpy as np
from scipy import sparse
import operator
from util import *
from monary import Monary
import numpy as np
from gensim import corpora, models, similarities
import json


## map reduce example
from bson.code import Code

def mapReduceCount(outputFile, newCollectionName):
    mapper = Code("""
        function () {
            var words = this.segmented_title_and_body.split(' ');
            for(var i = 0; i < words.length; i++) {
                emit(words[i], 1);
            }
        }
    """)

    reducer = Code("""
        function (key, values) {
            var total = 0;
            for (var i = 0; i < values.length; i++) {
                total += values[i];
            }
            return total;
        }
    """)
    result = post_detail_infos.map_reduce(mapper, reducer, newCollectionName)

    with open(outputFile, 'w') as f:
        for doc in result.find():
            key = doc['_id']
            value = doc['value']
            f.write('%s %d\n'%(key, int(value)))


# 所有文章的 word statistic
# output 到 file 中方便查找
def total_word_statistic(outputFile):
    parsed_count = 0
    k_count = 0
    word_statistic = Counter()
    for doc in post_detail_infos.find():
        parsed_count = (parsed_count + 1)%1000
        if parsed_count == 0:
            k_count += 1
            print('Parsed: ' + str(k_count) + 'k docs')

        word_statistic += Counter(doc['segmented_title_and_body'].split())

    with open(outputFile, 'w') as f:
        for key, value in word_statistic.items():
            f.write('%s %d\n'%(key, word_statistic[key]))

def get_doc_TFIDF(doc_index, tfidf_result, featureNames):
    data = {}
    for _, idx_col in zip(*tfidf_result.getrow(doc_index).nonzero()):
        key = featureNames[idx_col]
        data[key] = tfidf_result[doc_index, idx_col]
    return data

def get_top30_tfidf(tfidf_dict):
    sorted_tfidf = sorted(tfidf_dict.items(), key=operator.itemgetter(1), reverse=True)
    return [key for key, _ in sorted_tfidf[:30]]

def count_column_tfidf(columns):

    # with Monary('127.0.0.1') as monary:
    #     sizes, = monary.query(DB_NAME, 'post_detail_infos', {}, columns, ['size'])
    #     max_size = sizes.max()
    #     print('Max string size: ' + str(max_size))
    #     print('Start query...')
    #     np_arr = monary.query(
    #         DB_NAME,                         # database name
    #         'post_detail_infos',                   # collection name
    #         {},                             # query spec
    #         columns, # field names (in Mongo record)
    #         ['string:%d' % max_size]             # Monary field types (see below)
    #     )
    # df = np.matrix(np_arr).transpose() 
    # df = pd.DataFrame(df, columns=columns)

    print('Load dataframe...')

    cursor = post_detail_infos.find().sort('_id',1)
    df = pd.DataFrame(list(cursor), columns=columns)
    cursor.close()
    docs = df['segmented_title_and_body']
    print('dataframe docs counts:' + str(docs.count()))
    len_doc = post_detail_infos.find().count()
    print('post_length: ' + str(len_doc))

    vectorizer = CountVectorizer(stop_words=list(stopwords_list))
    transformer = TfidfTransformer()

    print('Count vectors...')
    vec_result = vectorizer.fit_transform(docs)
    tfidf_result = transformer.fit_transform(vec_result)

    featureNames = vectorizer.get_feature_names()

    return featureNames, tfidf_result

def statistic():
    # count tfidf
    # total words statistic
    # top co-occurence tfidf
    columns = ['segmented_title_and_body']
    featureNames, tfidf_result = count_column_tfidf(['segmented_title_and_body'])
    print('Start updating...')

    topOcc = Counter()
    total_word_statistic = Counter()

    parsed_count = 0
    k_count = 0
    len_doc = post_detail_infos.find().count()
    cursor = post_detail_infos.find().sort('_id', 1)
    for idx, entry in enumerate(cursor):
        if idx >= len_doc:
            print('idx: %d, post_url: %s'%(idx, entry['post_url']))
            logRecord('idx: %d, post_url: %s'%(idx, entry['post_url']), 'word_statistic.log')
            continue
        parsed_count = (parsed_count + 1)%1000
        if parsed_count == 0:
            k_count += 1
            print('Parsed: ' + str(k_count) + 'k docs')

        tfidf_dict = get_doc_TFIDF(idx, tfidf_result, featureNames)
        top30_tfidf = get_top30_tfidf(tfidf_dict)
        update_data = {
            'tfidf_dict': tfidf_dict,
            'top30_tfidf': top30_tfidf
        }
        topOcc += Counter(top30_tfidf)
        total_word_statistic += Counter(entry['segmented_title_and_body'].split())
        post_detail_infos.update_one({'_id': entry['_id']}, {'$set': update_data})
    cursor.close()

    with open('./outputs/gossip_top_occurence.txt', 'w') as f:
        for key, val in topOcc.items():
            f.write(key + ' ' + str(val) + '\n')

    with open('./outputs/gossip_total_word_statistic.txt', 'w') as f:
        for key, value in total_word_statistic.items():
            f.write('%s %d\n'%(key, total_word_statistic[key]))

    print('Done!!')


# def count_tfidf():

#     columns = ['segmented_title_and_body']
#     feature_Names, tfidf_result = count_column_tfidf(['segmented_title_and_body'])
#     print('Load dataframe...')
#     columns = ['segmented_title_and_body']

#     print('Start updating...')

#     topOcc = Counter()
#     parsed_count = 0
#     k_count = 0
#     cursor = post_detail_infos.find()
#     for idx, entry in enumerate(cursor):
#         if idx >= len_doc:
#             print(entry['post_url'])
#             continue
#         parsed_count = (parsed_count + 1)%1000
#         if parsed_count == 0:
#             k_count += 1
#             print('Parsed: ' + str(k_count) + 'k docs')
#         tfidf_dict = get_doc_TFIDF(idx, tfidf_result, featureNames)
#         top30_tfidf = get_top30_tfidf(tfidf_dict)
#         update_data = {
#             'tfidf_dict': tfidf_dict,
#             'top30_tfidf': top30_tfidf
#         }
#         topOcc += Counter(top30_tfidf)

#         # print(update_data)
#         post_detail_infos.update_one({'_id': entry['_id']}, {'$set': update_data})
#     cursor.close()

#     with open('gossip_top_occurence.txt', 'w') as f:
#         for key, val in topOcc.items():
#             f.write(key + ' ' + str(val) + '\n')
#     print('Finished~~')

# def top_cooccurrence_tfidf(outputFile=None):
#     cursor = post_detail_infos.find()
#     topOcc = Counter()
#     print('Start counting...')
#     parsed_count = 0
#     k_count = 0
#     for idx, entry in enumerate(cursor):
#         parsed_count = (parsed_count + 1)%1000
#         if parsed_count == 0:
#             k_count += 1
#             print('Parsed: ' + str(k_count) + 'k docs')
#         topOcc += Counter(entry['top30_tfidf'])

#     print('Counting finished.')
#     print('Start ouput file: '+ outputFile)

#     if outputFile is not None:
#         with open(outputFile, 'w') as f:
#             for key, val in topOcc.items():
#                 f.write(key + ' ' + str(val) + '\n')
#     print('Done')

def encodeKey(key):
    return key.replace("\\", "\\\\").replace("\$", "\\u0024").replace(".", "\\u002e")

def decodeKey(key):
    return key.replace("\\u002e", ".").replace("\\u0024", "\$").replace("\\\\", "\\")

def encodeDictKeys(dict):
    return {encodeKey(key):val for key, val in dict.items()}

def decodeDictKeys(dict):
    return {decodeKey(key):val for key, val in dict.items()}

class MyCorpus(object):
    def __iter__(self):
        for idx, doc in enumerate(post_detail_infos.find().sort('_id', 1)):
            yield [word
                   for word in doc['segmented_title_and_body'].split(' ') 
                   if word not in stopwords_list]

def tuples_to_word_map(list_of_tuples, widMap):
    return {widMap[word_id]: val for word_id, val in list_of_tuples}

def outputDictKeyValue(dict, outputFile):
    with open(outputFile, 'w') as f:
        for key, value in dict.items():
            f.write('%s %f\n'%(key, value))

def outputJson(dict, outputFile):
    with open(outputFile, 'w') as f:
        json.dump(dict, f)

def gensim_statistic():

    # start and Load corpus
    print('gensim start...')
    postCorpus = MyCorpus()

    # 建立字典
    print('load corpus to construct dictionary...')
    dictionary = corpora.Dictionary(postCorpus)
    dictionary.save('./tmp/words.dict')
    dictionary.load('./tmp/words.dict')
    dicMap = dictionary.token2id
    widMap = {v:k for k,v in dicMap.items()}

    # 轉換成 bow 格式 tuple: (word_id, times)
    print('transform to bowCorpus...')
    bowCorpus = [dictionary.doc2bow(text) for text in postCorpus]
    corpora.MmCorpus.serialize('./tmp/bowCorpus.mm', bowCorpus)
    bowCorpus = corpora.MmCorpus('./tmp/bowCorpus.mm')

    # 計算 tfidf 
    print('count tfidf...')
    tfidf = models.TfidfModel(bowCorpus)
    corpus_tfidf = tfidf[bowCorpus]

    # 統計所有 words 之出現次數 以及統計 tfidf top30 的 word co-occurence
    # 並更新至 tfidf 至 DB
    print('update tfidf to db and count top30 co-occurence and total word statistic')
    day_cooccurence = {}
    merged_tfidf = Counter()
    total_word_statistic = Counter()
    topOcc = Counter()
    parsed_count = 0
    k_count = 0

    try:
        for idx, doc in enumerate(post_detail_infos.find().sort('_id', 1)):
            simple_date = doc['post_date_simple']
            day_cooccurence.setdefault(simple_date, Counter())

            parsed_count = (parsed_count + 1)%1000
            if parsed_count == 0:
                k_count += 1
                print('Parsed: ' + str(k_count) + 'k docs')
            doc_tuple_list = corpus_tfidf[idx]
            tfidf_dict = tuples_to_word_map(doc_tuple_list, widMap)
            top30_tfidf = get_top30_tfidf(tfidf_dict)
            update_data = {
                'tfidf_dict': encodeDictKeys(tfidf_dict),
                'top30_tfidf': top30_tfidf
            }

            # total_word_statistic 是計算次數，不是 tfidf
            total_word_statistic += tuples_to_word_map(bowCorpus[idx], widMap)
            topOcc += Counter(top30_tfidf)
            merged_tfidf += Counter(tfidf_dict)
            day_cooccurence[simple_date] += Counter(tfidf_dict)

            # print(total_word_statistic)
            # print(topOcc)
            # print(update_data)
            # print('===============================')
            # print('===============================')
            # if idx == 2:
            #     break
            post_detail_infos.update_one({'_id': doc['_id']}, {'$set': update_data})
    except Exception as e:
        print('[Exception] post_url: ' + doc['post_url'] + ' idx: '+ str(idx) + ' Error: ' + str(e))
        logRecord('[Exception] post_url: ' + doc['post_url'] + ' idx: '+ str(idx) + ' Error: ' + str(e), 'word_statistic.log')

    print('output total word statistic...')
    outputDictKeyValue(total_word_statistic, './outputs/gossip_total_word_statistic.txt')

    print('output top30 co-occurence')
    outputDictKeyValue(topOcc, './outputs/gossip_top_occurence.txt')

    print('output merged tfidf')
    outputDictKeyValue(merged_tfidf, './outputs/gossip_merged_tfidf.txt')

    print('output day_cooccurence tfidf')
    outputJson(day_cooccurence, './outputs/gossip_day_cooccurence_tfidf.txt')


def main():
    loadStopWords()
    gensim_statistic()
    # total_word_statistic('./gossip_word_statistic.txt')
    # count_tfidf()
    # top_cooccurrence_tfidf('gossip_top_occurence.txt')
    # mapReduceCount('./outputs/gossip_total_word_statistic.txt', 'gossip_total_word_statistic')
    # statistic()
    
if __name__ == '__main__':
    main()
    exit(0)