#!/usr/bin/env python
#-*- coding:utf-8 -*-
from config import *
from datetime import datetime

def logRecord(msg):
    with open(LOG_FILE, 'a') as f:
        cur_time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        f.write("%s : %s\n" % (cur_time, msg))
    f.close()
