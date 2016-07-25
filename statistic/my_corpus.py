#!/bin/usr/env python
#-*- coding:utf-8 -*-
from util import *
from module_config import *

class MyCorpus(object):
    def __init__(self):
        loadStopWords()

    def __iter__(self):
        for idx, doc in enumerate(post_detail_infos.find().sort('_id', 1)):
            yield [word.lower()
                   for word in doc['segmented_title_and_body'].split()
                   if word not in stopwords_list]
