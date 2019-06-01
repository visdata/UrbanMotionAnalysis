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

#Todo：改变时间，写记录时写入多个时间段

class SrcDstJudge(object):
    """
    多进程计算类：按照日期对文件进行分类重写存储，相关字段预先处理，需同时指定基础输入目录和输出目录
        :param object:
    """

    def __init__(self, PROP):
        super(SrcDstJudge, self).__init__()

        self.INDEX = PROP['INDEX']
        self.CITY = PROP['CITY']
        self.INPUT_PATH = PROP['IDIRECTORY']
        self.OUTPUT_PATH = os.path.join(PROP['ODIRECTORY'], 'tj-byday-tf')
        self.INUM = PROP['INUM']
        self.ONUM = PROP['ONUM']
        self.MAXDAY = PROP['MAXDAY']
        self.MATRIX = [[] for x in xrange(0, PROP['MAXDAY'])]
        self.COUNT = [0 for x in xrange(0, PROP['MAXDAY'])]
        self.SAFECOUNT = PROP['SAFECOUNT']
        self.DELTATIME = 12000  # 起点和终点判定的时间阈值 2h
        self.res = []
        self.srccount = 0
        self.dstcount = 0
        self.MIN_TIME_INTERVAL = 1800
        self.travelrecordcount = 0

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

        for x in xrange(0, 10000):
            number = self.INDEX + 20 * x
            if number > self.INUM:
                break

            # part-03999-trajectory_15-800
            ifilename = 'P2-part-%05d-trajectory_30-800' % number
            print('Job-%d File-%s Operating...' % (self.INDEX, ifilename))
            self.iterateFileOnlyTravel(os.path.join(self.INPUT_PATH, ifilename))
        # self.iterateFile(os.path.join(self.INPUT_PATH, ifilename))

        # 捡完所有漏掉的记录，遍历输入文件
        for x in xrange(0, self.MAXDAY):
            if self.COUNT[x] == 0:
                continue

            ofile = os.path.join(self.OUTPUT_PATH, "rawdata-j%d-%d" % (self.INDEX, x))
            with open(ofile, 'ab') as stream:
                stream.write('\n'.join(self.MATRIX[x]) + '\n')
            stream.close()

        # logging.info('Total travel num-%d' %(self.len))
        print('src num-%d' %(self.srccount))
        if self.travelrecordcount!=0:
            print('ratio: ' + str(float(self.srccount)/self.travelrecordcount))
        print('dst num-%d' %(self.dstcount))
        if self.travelrecordcount!=0:
            print('ratio: ' + str(float(self.dstcount)/self.travelrecordcount))
        logging.info('End Job-%d' % (self.INDEX))


    def iterateFileOnlyTravelNew(self, ifile):

        with open(ifile, 'rb') as stream:
            self.recordsPassed = [];
            self.lastDeviceID = -1;
            self.indexDstDict = {};
            self.indexSrcDict = {};
            for line in stream:
                # print(line)
                # if line == '':
                # 	continue
                line = line.strip('\n')
                linelist = line.split(',');
                id = linelist[0];

                if self.lastDeviceID != id and self.lastDeviceID != -1:
                    for index in range(len(self.recordsPassed)):
                        record = self.recordsPassed[index];
                        stateRecord = record[4];

                        if stateRecord == '-1' or line == '' or stateRecord == '0':
                            continue

                        tmp = formatTime(record[1])
                        ydayCurrent = tmp['yday'] - 187
                        if ydayCurrent < 0 or ydayCurrent >= self.MAXDAY:
                            continue

                        self.travelrecordcount += 1
                        #只针对travel的记录找寻起点和终点
                        # 先找起点
                        for i in range(index - 1, -1, -1):
                            if self.recordsPassed[i][4] == '1' or self.recordsPassed[i][4] == '-1':
                                continue
                            if int(record[1]) - int(self.recordsPassed[i][1]) > self.DELTATIME:
                                break
                            if int(record[1]) - int(self.recordsPassed[i][1]) <= self.DELTATIME:
                                if self.indexSrcDict.has_key(i):
                                    break
                                else:
                                    self.indexSrcDict[i] = True
                                    tmpRecord = self.recordsPassed[i]
                                    tmp = formatTime(tmpRecord[1])
                                    ydayCurrent = tmp['yday'] - 187
                                    if ydayCurrent < 0 or ydayCurrent >= self.MAXDAY:
                                        continue
                                    hour = tmp['hour']
                                    self.srccount += 1
                                    newLinePreStr = "%d,%s,%s,%s,%s,%s" % (
                                    hour, self.lastDeviceID, tmpRecord[1], tmpRecord[2], tmpRecord[3], "src")
                                    self.res.append([newLinePreStr, ydayCurrent])
                                    break

                        # 寻找终点
                        for j in range(index + 1, len(self.recordsPassed)):
                            if self.recordsPassed[j][4] == '1' or self.recordsPassed[j][4] == '-1':
                                continue
                            if int(self.recordsPassed[j][1]) - int(record[1]) > self.DELTATIME:
                                break
                            else:
                                if self.indexDstDict.has_key(j):
                                    break
                                else:
                                    self.indexDstDict[j] = True
                                    tmpRecord = self.recordsPassed[j]
                                    tmp = formatTime(tmpRecord[1])
                                    ydayCurrent = tmp['yday'] - 187
                                    if ydayCurrent < 0 or ydayCurrent >= self.MAXDAY:
                                        continue
                                    hour = tmp['hour']
                                    self.dstcount += 1
                                    newLinePreStr = "%d,%s,%s,%s,%s,%s" % (
                                    hour, self.lastDeviceID, tmpRecord[1], tmpRecord[2], tmpRecord[3], "dst")
                                    self.res.append([newLinePreStr, ydayCurrent])
                                    break

                    # 重置

                    self.recordsPassed = [];
                    self.indexSrcDict = {};
                    self.indexDstDict = {};


                self.lastDeviceID = id
                self.recordsPassed.append(linelist);
# print(self.recordsPassed);
#print(self.lastDeviceID)
        stream.close();
        self.updLastTravelRecsOnlyTravel()


    def iterateFileOnlyTravel(self, ifile):
        print(ifile)
        with open(ifile) as f:
            records = f.readlines()
            
        c_uid = -1
        segments, tjt = [], []
        recordCount = -1
        self.indexSrcDict = {};
        self.indexDstDict = {};
        labeled_segments, stats = [], []

        # divide the records into to segments
        for record in records:
            columns = record.split(',')
            recordCount += 1

            uid = columns[0]
            time_second = int(columns[1])
            latitude, longtitude = float(columns[2]), float(columns[3])
            stat = int(columns[4])
            # if stat != 1:
            #     c_uid = uid
            #     continue

            #print(uid, c_uid)
            if uid == c_uid:
                tjt.append([uid, time_second, latitude, longtitude, stat, recordCount])
            else:
                # new uid
                #print('new uid')
                #print(record)
                if c_uid != -1:
                    tjt = [elem for elem in tjt if elem[4] == 1]
                    # the current uid is valid, segment the trajectory of the current uid (c_uid)
                    # sort the trajectory by time
                    tjt.sort(key=lambda x: x[1])

                    # truncate the trajectory into segments at every time interval larger than Delta_T, stored in segments
                    # the first index of the current segment
                    l = 0
                    for r in xrange(1, len(tjt)):
                        time_interval = tjt[r][1] -  tjt[r-1][1]
                        if time_interval > self.MIN_TIME_INTERVAL:
                            segments.append(tjt[l:r])
                            l = r

                    if l < len(tjt):
                        segments.append(tjt[l:])

                    #print(segments)
                    for seg in segments:
                        #find the source place
                        firstTravelRecord = seg[0]
                        firstTravelSegIndex = firstTravelRecord[5]
                        #print('index is %d'%firstTravelSegIndex)
                        for i in range(firstTravelSegIndex - 1, -1, -1):
                            current_record = records[i].split(',')
                            if int(current_record[4]) == 1:
                                break
                            if int(current_record[4]) == -1:
                                continue
                            if int(firstTravelRecord[1]) - int(current_record[1]) > self.DELTATIME:
                                break
                            if int(firstTravelRecord[1])- int(current_record[1]) <= self.DELTATIME:
                                if self.indexSrcDict.has_key(i):
                                    break
                                else:
                                    self.indexSrcDict[i] = True
                                    c_hour = -1
                                    for j in range(len(seg)):
                                        tmpRecord = seg[j]
                                        tmp = formatTime(tmpRecord[1])
                                        ydayCurrent = tmp['yday'] - 187
                                        if ydayCurrent < 0 or ydayCurrent >= self.MAXDAY:
                                            continue
                                        hour = tmp['hour']
                                        if hour != c_hour:
                                            self.srccount += 1
                                            newLinePreStr = "%d,%s,%s,%s,%s,%s" % (
                                            hour, current_record[0], tmpRecord[1], current_record[2], current_record[3], "src")
                                            self.res.append([newLinePreStr, ydayCurrent])
                                        c_hour = hour
                                    break


                         # 寻找终点
                        lastTravelRecord = seg[len(seg) - 1]
                        #print(lastTravelRecord)
                        lastTravelSegIndex = lastTravelRecord[5]
                        for j in range(lastTravelSegIndex + 1, len(records)):
                            current_record = records[j].split(',')
                            if int(current_record[4]) == 1:
                                break
                            if int(current_record[4]) == -1:
                                continue

                            if int(current_record[1]) - int(lastTravelRecord[1]) > self.DELTATIME:
                                break
                            else:
                                if self.indexDstDict.has_key(j):
                                    break
                                else:
                                    #print(current_record)
                                    self.indexDstDict[j] = True
                                    c_hour = -1
                                    for i in range(len(seg)):
                                        tmpRecord = seg[i]
                                        tmp = formatTime(tmpRecord[1])
                                        ydayCurrent = tmp['yday'] - 187
                                        if ydayCurrent < 0 or ydayCurrent >= self.MAXDAY:
                                            continue
                                        hour = tmp['hour']
                                        if c_hour != hour:
                                            self.dstcount += 1
                                            newLinePreStr = "%d,%s,%s,%s,%s,%s" % (
                                            hour, current_record[0], tmpRecord[1], current_record[2], current_record[3], "dst")
                                            self.res.append([newLinePreStr, ydayCurrent])
                                        c_hour = hour
                                    break

                    segments, tjt = [], []
                    self.indexSrcDict = {};
                    self.indexDstDict = {};
             # refresh the arrays to only store the first record of the new trajectory (uid)
            tjt.append([uid, time_second, latitude, longtitude,stat, recordCount])
            c_uid = uid

        self.updLastTravelRecsOnlyTravel()


    def checkWriteOpt(self, ydayCurrent):
        # 计数存储，看情况写入文件
        if self.COUNT[ydayCurrent] >= self.SAFECOUNT:
            ofile = os.path.join(self.OUTPUT_PATH, "rawdata-j%d-%d" % (self.INDEX, ydayCurrent))
            with open(ofile, 'ab') as stream:
                stream.write('\n'.join(self.MATRIX[ydayCurrent]) + '\n')
            stream.close()

            self.COUNT[ydayCurrent] = 0
            self.MATRIX[ydayCurrent] = []


    def updLastTravelRecsOnlyTravel(self):
        #print(self.res)

        # 遍历记录
        # for each in self.res:
        #     ydayCurrent = each[1]
        #     newline = "%s" % (each[0])
        #
        #     self.COUNT[ydayCurrent] += 1
        #     self.MATRIX[ydayCurrent].append(newline)
        #     self.checkWriteOpt(ydayCurrent)

        # 重置
        self.res = []