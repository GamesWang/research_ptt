
import re
import datetime
import time
from module_config import *

def logRecord(msg, logFile):
    with open(logFile, 'a') as f:
        cur_time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
        f.write('%s : %s\n' % (cur_time, msg))
    f.close()

def getAuthorByPostUrl(post_url):
    for doc in post_url_infos.find({'post_url': post_url}):
        return doc['author'].strip()

def getTitleByPostUrl(post_url):
    for doc in post_url_infos.find({'post_url': post_url}):
        return doc['title'].strip()

def getPostType(title):
    if title.startswith('Fw: '):
        return 'forward'
    elif title.startswith('Re: '):
        return 'reply'
    else:
        return 'post'

def parseTitle(title):
    if getPostType(title) == 'post':
        return title.strip()
    elif getPostType(title) == 'reply':
        return title.strip().replace('Re: ', '', 1)
    elif getPostType(title) == 'forward':
        return title.strip().replace('Fw: ', '', 1)

def bodyContentParse(input):
    return input.strip().replace('\n', ' ')

def getNickName(authrWithNick):
    m = re.match(r'.+ \((.*)\)', authrWithNick)
    if m is None:
        return None
    return m.group(1)

# input: Mon Oct 18 22:55:19 2004
# return: struct time format
def parseDateToStructTime(dateTime):
    d = time.strptime(dateTime.strip(), '%a %b %d %H:%M:%S %Y')
    f = time.strftime('%Y.%m.%d', d)
    return d

# input: Wed Jul  6 09:50:30 2016
# return: 2016.07.06
def parseDateToSimpleDate(dateTime):
    d = time.strptime(dateTime.strip(), '%a %b %d %H:%M:%S %Y')
    f = time.strftime('%Y.%m.%d', d)
    return f

if __name__ == '__main__':
    print(parseDateToStructTime('Mon Oct 18 22:55:19 2004'))
    print(parseDateToSimpleDate('Wed Jul  6 09:50:30 2016'))