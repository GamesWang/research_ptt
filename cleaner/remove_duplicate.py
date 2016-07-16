#!/bin/usr/env python
#-*- coding:utf-8 -*-

from util import *
from module_config import *

def main():
    pipeline = [
        {"$group": {"_id": { "post_url": "$post_url"}, "dups": { "$push": "$_id" }, "count": {"$sum": 1}}},
        {"$match": {"count": { "$gte": 2 }}},
        {"$sort":{"count":-1}}
    ]

    for doc in post_detail_infos.aggregate(pipeline):
        print('Remove: ' + doc['_id']['post_url'])
        logRecord('Remove: ' + doc['_id']['post_url'], 'remove.log')
        # print(doc['count'])
        # print(doc['dups'][1:])

        post_detail_infos.remove({'_id':{'$in':doc['dups'][1:]}})

if __name__ == '__main__':
    main()
    exit(0)