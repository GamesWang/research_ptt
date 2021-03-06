#!/bin/usr/env python
#-*- coding:utf-8 -*-

import sys, os
sys.path.append('../')
from common.common_config import *
from common.util import *

# default parameter
RETRY_SLEEP_INTERVAL = 1
DEFAULT_RETRY_TIMES = 3
PTT_HOST_URL = 'https://www.ptt.cc'
PTT_BOARD = 'Gossiping'
MENU_PAGE_URL = PTT_HOST_URL + '/bbs/'+ PTT_BOARD +'/index{}.html'
MAXIMUM_MENU_PAGE = 1000

# mongoDB
use_db = client['ptt_' + PTT_BOARD]
post_url_infos = use_db['post_url_infos']
post_detail_infos = use_db['post_detail_infos']

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LOG_FILE = os.path.join(BASE_DIR, 'process.log')

NUM_THREAD = 10
THREAD_REQUEST_SLEEP_INTERVAL = 5
REQUEST_BATCH_SIZE = 30
REQUEST_SLEEP_INTERVAL = 0
