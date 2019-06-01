#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Input Format:
# id, time, lat, lng, state, sid, admin
# 
# Output Format:
# [hares-x]
# id, seg, hour, wday, gid, state, admin, from_gid, to_gid, from_aid, to_aid
# 
# [tripFlow-x] 
# hour, id, time, lat, lng, from_lat, from_lng, from_time, to_lat, to_Lng, to_time
# 
# 现使用处理方式为只过滤 travel 的数据

import logging
import os
from util.preprocess import getCityLocs, formatGridID, formatTime
from util.preprocess import getAdminNumber
from util.tripFlow.base import getRealDistance


class CountTravelNum(object):
    """
    多进程计算类：按照日期对文件进行分类重写存储，相关字段预先处理，需同时指定基础输入目录和输出目录
        :param object:
    """

    def __init__(self, PROP):
        super(CountTravelNum, self).__init__()

        self.INDEX = PROP['INDEX']
        self.CITY = PROP['CITY']
        self.INPUT_PATH = PROP['IDIRECTORY']
        self.OUTPUT_PATH = os.path.join(PROP['ODIRECTORY'], 'bj-byday-tf')
        self.INUM = PROP['INUM']
        self.ONUM = PROP['ONUM']
        self.MAXDAY = PROP['MAXDAY']
        self.MATRIX = [[] for x in xrange(0, PROP['MAXDAY'])]
        self.COUNT = [0 for x in xrange(0, PROP['MAXDAY'])]
        self.SAFECOUNT = PROP['SAFECOUNT']
        self.len = 0
        self.deltaDistance = 700

        self.currentDatasets = {
        'fromLatLng': [0, 0],
        'fromAdmin': '',
        'toLatLng': [0, 0],
        'toAdmin': '',
        'fromTime': '',
        'toTime': '',
        'data': [],
        'stateId': 0
        }

    def run(self):
        logging.info('TASK-%d running...' % (self.INDEX))

        for x in xrange(0, 10000, 50):
            number = self.INDEX + 20 * x
            if number > self.INUM:
                break
            ifilename = 'P2-part-%05d-trajectory_30-800' % number;

            print('Job-%d File-%s Operating...' % (self.INDEX, ifilename))
            self.iterateFileOnlyTravelNew(os.path.join(self.INPUT_PATH, ifilename))
            print(self.COUNT)


    def iterateFileOnlyTravelNew(self, ifile):
        with open(ifile, 'rb') as stream:
            for line in stream:
                line = line.strip('\n')
                linelist = line.split(',')
                state = linelist[4]
                tmp = formatTime(linelist[1])
                ydayCurrent = tmp['yday'] - 187

                if state == '1' and ydayCurrent >= 0 and ydayCurrent <= 86:
                    self.COUNT[ydayCurrent] = self.COUNT[ydayCurrent] + 1