#!/bin/usr/env python
#-*- coding:utf-8 -*-

import datetime

def logRecord(msg, logFile):
    with open(logFile, 'a') as f:
        cur_time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
        f.write('%s : %s\n' % (cur_time, msg))
    f.close()

if __name__ == '__main__':
    main()
    exit(0)