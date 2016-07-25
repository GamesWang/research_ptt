from module_config import *
from collections import Counter

stopword_dicts_list = ['../resource/dicts/git_stopwords.txt', '../resource/dicts/mystopwords.txt']
stopwords_list = {}

def loadStopWords():
    global stopwords_list
    for file in stopword_dicts_list:
        with open(file, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                stopwords_list[line.strip().lower()] = 1

def main():
    # total_word_statistic('total_words_statistic.txt')
    # print(post_detail_infos.find({'segmented_title_and_body':{'$in':[None]}}).count())
    # for doc in post_detail_infos.find({'segmented_title_and_body':{'$in':[None]}}):
    #     print(doc)
    #     break

    pass

if __name__ == '__main__':
    main()
    exit(0)