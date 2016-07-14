import pymongo
from collections import Counter
# mongoDB
client = pymongo.MongoClient('192.168.56.102', 27017)
ptt_food = client['ptt_Food']
post_url_infos = ptt_food['post_url_infos']
post_detail_infos = ptt_food['post_detail_infos']



# urls = []
# for url_info in post_url_infos.find({}):
#     urls.append(url_info['post_url'])

# detail_urls = []
# for url_info in post_detail_infos.find({}):
#     detail_urls.append(url_info['post_url'])

# result = (Counter(detail_urls) - Counter(urls))

# for url in result:
#     if post_url_infos.find({'post_url':url}):
#         print('Duplicate: %s'%url)
#     else:
#         print('not Duplicate: %s'%url)




# pipeline = [
#     # { '$project' : { 'title' : 1 , 'author' : 1 } },
#     {'$group':{'_id':'$author', 'counts':{'$sum':1}}},
#     # {'$sort':{'counts':-1}},
#     {'$limit':10}
# ]

pipeline = [
    # {'$project' : { 'title' : 1 , 'post_url' : 1 } },
    {'$group':{'_id':{'post_url':'$post_url'}, 'dups':{'$push':'$_id'}, 'counts':{'$sum':1}}},
    { '$match': { 'counts': { '$gt': 1 } }},
    {'$limit':1}
]

for info in post_detail_infos.aggregate(pipeline):
    for idx, dup in enumerate(info['dups']):
        if idx ==1:
            continue
        else:
            for doc in post_detail_infos.find({'_id': dup}):
                print('ggggggg')
                print(doc['post_url'])


# pipeline = [
#     {'$match':{'$and':[{'visited':1}]}}
# ]

# for entry in post_url_infos.find({'visited':1},{'post_url':1}):
#     print(entry['post_url'])