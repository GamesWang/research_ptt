import pymongo


# mongoDB
PTT_BOARD = 'Food_cleaned'
client = pymongo.MongoClient('localhost', 27017)
use_db = client['ptt_' + PTT_BOARD]
post_url_infos = use_db['post_url_infos']
post_detail_infos = use_db['post_detail_infos']