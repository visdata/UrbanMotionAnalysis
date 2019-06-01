__author__ = 'hcc'

# -*- coding: utf-8 -*-
#
#
#

import numpy as np
import matplotlib.pyplot as plt
import multiprocessing

filelist = ['P2-part-'+format(n, '05d')+'-trajectory_30-800' for n in range(0, 10000,100)]

input_path = '/datahouse/tripflow/labelData-30-800-BJ/'
output_path = '/datahouse/tripflow/statics/'

stayLenArray = []
travelLenArray = []
file_name_w_s = 'stay.npy'
file_name_w_t = 'travel.npy'

def stay_travel_len_cal(filename):
    print('prcessing file '+filename)
    file_name_r = input_path + filename


    with open(file_name_r) as f:
        records = f.readlines()

    c_uid = -1
    c_stat = -2
    c_time = -1
    tmpTimestampArray = []
    for record in records:
        columns = record.split(',')

        uid = columns[0]
        timestamp =int(columns[1])
        stat = int(columns[4])

        if stat == -1:
            if len(tmpTimestampArray) > 1:
                if c_stat == 0 and tmpTimestampArray[1] - tmpTimestampArray[0] != 0:
                    stayLenArray.append(tmpTimestampArray[1]-tmpTimestampArray[0])
                if c_stat == 1 and tmpTimestampArray[1] - tmpTimestampArray[0] != 0:
                    travelLenArray.append(tmpTimestampArray[1]-tmpTimestampArray[0])
            tmpTimestampArray = []
            c_stat = stat
            c_uid =uid
            c_time = timestamp
            continue


        if timestamp - c_time > 1800 and c_time != -1:
            if len(tmpTimestampArray) > 1:
                if c_stat == 0 and tmpTimestampArray[1] - tmpTimestampArray[0] != 0:
                    stayLenArray.append(tmpTimestampArray[1]-tmpTimestampArray[0])
                if c_stat == 1 and tmpTimestampArray[1] - tmpTimestampArray[0] != 0:
                    travelLenArray.append(tmpTimestampArray[1]-tmpTimestampArray[0])
            tmpTimestampArray = [timestamp]
            c_stat = stat
            c_uid =uid
            c_time = timestamp
            continue


        if uid == c_uid:
            if c_stat == stat:
                tmpTimestampArray = [tmpTimestampArray[0], timestamp]
            else:
                if c_stat == -2:
                    tmpTimestampArray.append(timestamp)
                else:
                    if len(tmpTimestampArray) > 1:
                        if c_stat == 0 and tmpTimestampArray[1] - tmpTimestampArray[0] != 0:
                            stayLenArray.append(tmpTimestampArray[1]-tmpTimestampArray[0])
                        if c_stat == 1 and tmpTimestampArray[1] - tmpTimestampArray[0] != 0:
                            travelLenArray.append(tmpTimestampArray[1]-tmpTimestampArray[0])
                    tmpTimestampArray = [timestamp]
        else:
            if c_uid == -1:
                tmpTimestampArray.append(timestamp)
            else:
                if len(tmpTimestampArray) > 1:
                    if c_stat == 0 and tmpTimestampArray[1] - tmpTimestampArray[0] != 0:
                            stayLenArray.append(tmpTimestampArray[1]-tmpTimestampArray[0])
                    if c_stat == 1 and tmpTimestampArray[1] - tmpTimestampArray[0] != 0:
                        travelLenArray.append(tmpTimestampArray[1]-tmpTimestampArray[0])
                tmpTimestampArray = [timestamp]

        c_uid= uid
        c_stat = stat
        c_time = timestamp




if __name__ == "__main__":
    # pool = multiprocessing.Pool(processes=15)
    # pool.map(stay_travel_len_cal, filelist)

    for file in filelist:
        stay_travel_len_cal(file)
    print(stayLenArray)
    print(travelLenArray)
    np.save(file_name_w_s, stayLenArray)
    np.save(file_name_w_t, travelLenArray)