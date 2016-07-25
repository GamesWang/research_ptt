#!/bin/usr/env python
#-*- coding:utf-8 -*-
from gensim import corpora, models, similarities
import jieba
from module_config import *
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
from util import *
import operator
from multiprocessing import Pool
import multiprocessing


def train_update_topic_model(num_topics=5, max_remained_topics=3):
    print('==========Load Stop words...==========')
    loadStopWords()

    print('==========Load corpus to construct dictionary==========')
    dictionary = corpora.Dictionary.load('./serialization/uniq_words.dict')
    # postCorp = MyCorpus()
    # dictionary = corpora.Dictionary(postCorp)
    # dictionary.save('./serialization/uniq_words.dict')

    print('==========Transform corpus to bowCorpus==========')
    bowCorpus = corpora.MmCorpus('./serialization/gossip_corpus.mm')
    # bowCorpus = [dictionary.doc2bow(text) for text in postCorp]
    # corpora.MmCorpus.serialize('./serialization/gossip_corpus.mm', bowCorpus)

    # print('==========Counting tfidf...==========')
    # tfidf = models.TfidfModel(bowCorpus)
    # corpus_tfidf = tfidf[bowCorpus]

    str_topic_k_model = 'topic_' + str(num_topics) + '_model'
    print('==========Start training LDA model for %s...==========' % str_topic_k_model)
    # lda = models.LdaModel.load('./serialization/topic_' + str(num_topics) + '.lda')
    lda = models.LdaModel(bowCorpus, id2word=dictionary, num_topics=num_topics)
    lda.save('./serialization/topic_' + str(num_topics) + '.lda')

    # # output LDA topic infos to topic_k_model table
    print('==========Start output LDA topic infos to topic_k_model table...==========')
    topic_table = use_db[str_topic_k_model]
    for topic_id, term_list in (lda.show_topics(num_topics=num_topics, formatted=False)):
        sorted_tuples = sorted(term_list, key=operator.itemgetter(1), reverse=True)
        sorted_term_list = [key for key, _ in sorted_tuples]
        update_data = {
            'term_list': sorted_term_list,
            'tuple_list': sorted_tuples
        }
        topic_table.update_one({'_id': topic_id}, {'$set': update_data}, True)

    # # update topic to each document
    print('==========Start update topic to each document....==========')
    k_count = 0
    for idx, doc in enumerate(post_detail_infos.find().sort('_id', 1)):
        if idx%1000 == 0:
            print('==========Update %d k documents...==========' % k_count)
            k_count += 1
        sorted_tuples = sorted(lda.get_document_topics(bowCorpus[idx]), key=operator.itemgetter(1), reverse=True)
        sorted_topic_list = [key for key, _ in sorted_tuples]
        update_data = {
            str_topic_k_model: sorted_topic_list[:max_remained_topics]
        }
        post_detail_infos.update_one({'_id': doc['_id']}, {'$set': update_data})


def main():
    # train_update_topic_model()
    num_process = 4
    pool = Pool(num_process)

    args = [num_topics for num_topics in range(5, 51, 5)]
    pool.map(train_update_topic_model, args)
    pool.close()
    pool.join()

    pass
    
if __name__ == '__main__':
    main()
    exit(0)


"""
sentences = ["我喜歡吃土豆","土豆是個百搭的東西","我不喜歡今天霧霾的北京"]

# 分詞
words=[]
for doc in sentences:
    words.append(list(jieba.cut(doc)))
# print(words)

# 統計所有字的出現次數、並改成字典格式
dic = corpora.Dictionary(words)
# print (dic)
# print (dic.token2id)

# 將每個 document 改成以 tuple (word, 出現頻率) 的格式來表示
corpus = [dic.doc2bow(text) for text in words]
# print(corpus)

# print()

# 用 corpus 建立出 tfidf model，實際上就是去計算出所有文件中所有 word 的 tfidf
# 並將 idf 資訊存起來
tfidf = models.TfidfModel(corpus)
# print(tfidf)
# print()

# 假設有個新 document 為[(0,1),(4,1)]
# test_doc = [(0,1),(4,1)]
# 根據之前建出來的 tfidf model ，來將他也轉化成 tfidf 的樣子
# 我猜應該是乘上 idf 而已
# print(tfidf[test_doc]) 
# print()

# 這邊是表示所有文本的 tfidf
corpus_tfidf = tfidf[corpus]
# for doc in corpus_tfidf:
#     print (doc)

# 有了 tfidf 就可以作一些簡單搜尋、比較相似度

# 搜尋前要先建立 index
# 這裡對所有文件建出了 index tfidf[corpus] 就是 list of documents 
index = similarities.SparseMatrixSimilarity(tfidf[corpus], num_features=len(dic))

# print(index)
# 把想要搜尋的文章先轉成 tfidf 樣子，然後丟進去 indexer中，會回傳對於每個文章的相似度
test_doc = [(0,1),(4,1)]
sims = index[tfidf[test_doc]]
# print (list(enumerate(sims)))

# lsi = models.LsiModel(corpus_tfidf, id2word=dic, num_topics=2)
# lsiout=lsi.print_topics(2)
# print(lsiout[0])

lda = models.LdaModel(corpus_tfidf, id2word=dic, num_topics=2)
ldaOut=lda.print_topics(2)
print (ldaOut[0])

"""
