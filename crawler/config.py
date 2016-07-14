import pymongo
from bs4 import BeautifulSoup
import sys, os



# default parameter
RETRY_SLEEP_INTERVAL = 1
DEFAULT_RETRY_TIMES = 3
PTT_HOST_URL = 'https://www.ptt.cc'
PTT_BOARD = 'Food'
MENU_PAGE_URL = PTT_HOST_URL + '/bbs/'+ PTT_BOARD +'/index{}.html'
MAXIMUM_MENU_PAGE = 6000

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LOG_FILE = os.path.join(BASE_DIR, 'process.log')

NUM_THREAD = 10
THREAD_REQUEST_SLEEP_INTERVAL = 5
REQUEST_BATCH_SIZE = 30

# mongoDB
client = pymongo.MongoClient('localhost', 27017)
use_db = client['ptt_' + PTT_BOARD]
post_url_infos = use_db['post_url_infos']
post_detail_infos = use_db['post_detail_infos']

