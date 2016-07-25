#!/bin/usr/env python
#-*- coding:utf-8 -*-

from module_config import *
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
from util import *
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from scipy import sparse
from sklearn.externals import joblib
import csv
import gensim
from gensim import corpora, models, similarities
from my_corpus import MyCorpus
import matplotlib.pyplot as plt
import logging
# logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
from word_statistic import tuples_to_word_map
import operator
from multiprocessing import Pool
import multiprocessing
import os.path

def outputDistortion(outputFile, k_num, inertia):
    with open(outputFile, 'a') as f:
        f.write('%d %f\n' %(k_num, inertia))

def preprocess_with_gensim_clustering(k_num=5):
    str_k_means_model = 'cluster_'+str(k_num)+'_means'
    kmeans_table = use_db[str_k_means_model]

    already_update_count = post_detail_infos.find({str_k_means_model:{'$ne':None}}).sort('_id', 1).count()
    total_documents = post_detail_infos.find().count()
    if already_update_count == total_documents and kmeans_table.find().count() == k_num:
        print('==========Task for '+ str(str_k_means_model) +' already finished.==========')
        return
    print('==========Start task for '+ str_k_means_model + '...==========')

    print('==========Load Stop words...==========')
    loadStopWords()

    print('==========Load corpus to construct dictionary==========')
    dictionary = corpora.Dictionary.load('./serialization/uniq_words.dict')
    # postCorp = MyCorpus()
    # dictionary = corpora.Dictionary(postCorp)
    # dictionary.save('./serialization/uniq_words.dict')
    dicMap = dictionary.token2id
    widMap = {v:k for k,v in dicMap.items()}

    print('==========Transform corpus to bowCorpus==========')
    bowCorpus = corpora.MmCorpus('./serialization/gossip_corpus.mm')
    # bowCorpus = [dictionary.doc2bow(text) for text in postCorp]
    # corpora.MmCorpus.serialize('./serialization/gossip_corpus.mm', bowCorpus)

    print('==========Counting tfidf...==========')
    tfidf = models.TfidfModel.load('./serialization/gossip_corpus.tfidf_model')
    # tfidf = models.TfidfModel(bowCorpus)
    # tfidf.save('./serialization/gossip_corpus.tfidf_model')
    corpus_tfidf = tfidf[bowCorpus]
    print('=========Transform to scipy sparse matrix=========')
    tfidf_result = gensim.matutils.corpus2csc(corpus_tfidf).T

    distortions = []
    cluster_tfidf_counter = {}
    try:
        if os.path.exists('./serialization/' + str_k_means_model + '.pkl'):
            print('==========Load ' + str_k_means_model + '...==========')
            km = joblib.load('./serialization/' + str_k_means_model + '.pkl')
        else:
            print('==========Start clustering...%s==========' % str_k_means_model)
            km = KMeans(n_clusters=k_num, init='k-means++', n_init=10)
            print('==========Dump k-means model...==========')
            joblib.dump(km, './serialization/' + str_k_means_model +'.pkl') 

        y_km = km.fit_predict(tfidf_result)

        distortions.append(km.inertia_)
        outputDistortion('./kmeans.inertia.out', k_num, km.inertia_)

        print('==========Start calculate cluster_tfidf_counter and update documents in mongoDB...==========')
        parsed_count = 0
        k_count = 0
        for idx, doc in enumerate(post_detail_infos.find().sort('_id', 1)):
            parsed_count = (parsed_count + 1)%1000
            if parsed_count == 0:
                k_count += 1
                print('Parsed: ' + str(k_count) + 'k docs')
            assigned_cluster = int(y_km[idx])
            doc_tuple_list = corpus_tfidf[idx]
            tfidf_dict = tuples_to_word_map(doc_tuple_list, widMap)
            cluster_tfidf_counter.setdefault(assigned_cluster, Counter())
            cluster_tfidf_counter[assigned_cluster] += Counter(tfidf_dict)
            update_data = {
                str_k_means_model: assigned_cluster,
            }
            # print(update_data)
            post_detail_infos.update_one({'_id': doc['_id']}, {'$set': update_data})

        print('==========Output cluster_tfidf_counter to kmeans_table==========')
        for assigned_cluster, tfidf_counter in cluster_tfidf_counter.items():
            sorted_tuples = sorted(tfidf_counter.items(), key=operator.itemgetter(1), reverse=True)
            sorted_term_list = [key for key, _ in sorted_tuples]
            update_data = {
                'term_list': sorted_term_list,
                'tuple_list': sorted_tuples
            }
            # print(update_data)
            kmeans_table.update_one({'_id': assigned_cluster}, {'$set': update_data}, True)

    except Exception as e:
        print('[Exception] ' + str(e))
        logRecord('[Exception] ' + str(e), 'clustering.log')

    # plt.plot(range(1,51), distortions, marker='o')
    # plt.xlabel('Number of clusters')
    # plt.ylabel('Distortion')
    # plt.savefig('clustering_curve.png')
    # plt.show()

    # km = joblib.load('kmeans.'+ str(k_num) +'.pkl') 
    # y_km = km.predict(tfidf_result)

# def clustering():
#     columns = ['segmented_title_and_body']
#     cursor = post_detail_infos.find()
#     print('Load dataframe...')
#     df = pd.DataFrame(list(cursor), columns=columns)
#     print('Load docs...')
#     docs = df['segmented_title_and_body']
#     print('Load Stopwords')
#     loadStopWords()
#     vectorizer = CountVectorizer(stop_words=list(stopwords_list))
#     transformer = TfidfTransformer()

#     print('Start Counter and TFIDF...')
#     vec_result = vectorizer.fit_transform(docs)
#     tfidf_result = transformer.fit_transform(vec_result)

#     try:
#         for k_num in range(5, 51, 5):

#             print('Start clustering...' + str(k_num) + '-means.')
#             km = KMeans(n_clusters=k_num, init='k-means++', n_init=10)
#             y_km = km.fit_predict(tfidf_result)
#             len_result = len(y_km)

#             print('Start updating mongoDB...')
#             parsed_count = 0
#             k_count = 0
#             for idx, doc in enumerate(post_detail_infos.find()):
#                 if idx >= len_result:
#                     print('idx: %d, post_url: %s'%(idx, doc['post_url']))
#                     continue

#                 parsed_count = (parsed_count + 1)%1000
#                 if parsed_count == 0:
#                     k_count += 1
#                     print('Parsed: ' + str(k_count) + 'k docs')

#                 update_data = {
#                     'cluster_'+str(k_num)+'_means': int(y_km[idx]),
#                 }
#                 # print(update_data)
#                 post_detail_infos.update_one({'_id': doc['_id']}, {'$set': update_data})

#     except Exception as e:
#         print('[Exception] ' + str(e))
#         logRecord('[Exception] ' + str(e), 'clustering.log')

    # joblib.dump(km, 'kmeans.'+ str(k_num) +'.pkl') 
    # km = joblib.load('kmeans.'+ str(k_num) +'.pkl') 
    # y_km = km.predict(tfidf_result)


    # print('Start Output...')
    # with open('kmean.'+ str(k_num) +'.csv', 'w') as csvfile:
    #     csvWriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    #     for i in range(docs.count()):
    #         csvWriter.writerow([str(y_km[i]), docs[i]])

def main():
    # preprocess_with_gensim_clustering()
    num_process = 2
    pool = Pool(num_process)

    args = [num_topics for num_topics in range(5, 51, 5)]
    pool.map(preprocess_with_gensim_clustering, args)
    pool.close()
    pool.join()

if __name__ =='__main__':
    main()
    exit(0)

