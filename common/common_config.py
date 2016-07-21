#!/bin/usr/env python
#-*- coding:utf-8 -*-

import pymongo

# mongoDB
PTT_BOARD = 'Food_cleaned'
client = pymongo.MongoClient('localhost', 27017, connect=False)
use_db = client['ptt_' + PTT_BOARD]
post_url_infos = use_db['post_url_infos']
post_detail_infos = use_db['post_detail_infos']
y2015_detail_infos = use_db['y2015_detail_infos']
