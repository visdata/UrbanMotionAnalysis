# -*- coding: utf-8 -*-
__author__ = 'lenovo'

# calculate stay/travel/all device number of each grid

import time
import multiprocessing
import os
import json
from multiprocessing import Process
#res = [[[j, 0, 0, 0] for j in range(104000)] for i in range(2088)]

res = [0 for i in range(87)]

filelist  = ['rawdata-'+str(n) for n in range(87)]

input_path = '/datahouse/tripflow/2019-30-800-TJ/tj-byday-tf/'
output_path = '/datahouse/tripflow/Anomaly/tj-byhour-statics/'

def getFormatGID(point, LngSPLIT=0.0064, LatSPLIT=0.005, locs={
			'north': 40.2500,  # 40.1500,
			'south': 38.5667,  # 38.340,
			'west': 116.7167,  # 116.430,
			'east': 118.3233,  # 118.1940
			}):
	"""
	[NEW] 根据经纬度计算城市网格编号

	Args:
		locs (TYPE): Description
		point (TYPE): [lng, lat]

	Returns:
		TYPE: Description
	"""
	if point[0] == '0' and point[1] == '0':
		return 0
	else:
		# LATNUM = int((locs['north'] - locs['south']) / SPLIT + 1)
		LNGNUM = int( (locs['east'] - locs['west']) / LngSPLIT + 1 )
		lngind = int( (float(point[0]) - locs['west']) / LngSPLIT )
		latind = int( (float(point[1]) - locs['south']) / LatSPLIT )

		return {
			'gid': lngind + latind * LNGNUM,
			'lngind': lngind,
			'latind': latind
		}

def formatTime(timestr):
	"""格式化时间戳

	Args:
		timestr (TYPE): Description

	Returns:
		TYPE: Description
	"""
	dateObj = time.localtime(int(timestr))

	return {
		'hour': dateObj[3],
		'yday': dateObj[7],
		'wday': dateObj[6]
	}


def iterateFile(filename):
    print(filename)

    fileName_r = input_path + filename

    with open(fileName_r, 'rb') as f:
        records = f.readlines()

    #c_uid = -1
    #stay_hour_gid_uid_dict = {}
    travel_hour_gid_uid_dict = {}
    #total_hour_gid_uid_dict = {}


    for record in records:
        columns = record.split(',')

        uid = columns[1]
        # if uid != c_uid:
        #     stay_hour_gid_uid_dict = {}
        #     travel_hour_gid_uid_dict = {}
        #     total_hour_gid_uid_dict = {}

        #latitude, longtitude = float(columns[2]), float(columns[3])
        time_second = int(columns[2])
        #gid = getFormatGID([longtitude, latitude])['gid']
        #stat = int(columns[4])

        #hour = formatTime(time_second)['hour']
        ydayCurrent = formatTime(time_second)['yday'] - 187
        if ydayCurrent < 0 or ydayCurrent >= 87:
            continue
        #hourSeg = ydayCurrent * 24 + hour

        key = str(uid)

        # if stat == 0 and not stay_hour_gid_uid_dict.has_key(key):
        #     res[hourSeg][gid][1] += 1
        #     stay_hour_gid_uid_dict[key] = True
        #     if not total_hour_gid_uid_dict.has_key(key):
        #         res[hourSeg][gid][3] += 1
        #         total_hour_gid_uid_dict[key] = True

        if not travel_hour_gid_uid_dict.has_key(key):
            res[ydayCurrent] += 1
            travel_hour_gid_uid_dict[key] = True


        # if stat == -1 and not total_hour_gid_uid_dict.has_key(key):
        #     res[hourSeg][gid][3] += 1
        #     total_hour_gid_uid_dict[key] = True

        #c_uid = uid

    f.close()

def writeRes():
     with open(os.path.join(output_path, "travelcountbyday_tj.json"), 'wb') as output:
        output.write(json.dumps(res));
    # for hourId in range(len(res)):
    #     hour = hourId % 24
    #     filename_w = str(hour) + '-' + str(hourId)
    #     wfile = file(output_path+filename_w,'w')
    #
    #     hourRec = res[hourId]
    #
    #     for i in range(len(hourRec)-1, -1, -1):
    #         if hourRec[i][1] == 0 and hourRec[i][2] == 0 and hourRec[i][3] == 0:
    #             continue
    #         else:
    #             break
    #     hourRec = hourRec[:i+1]
    #
    #     for i in range(len(hourRec)):
    #         hourRec[i] = '%d,%d,%d,%d' %(hourRec[i][0],hourRec[i][1],hourRec[i][2],hourRec[i][3])
    #
    #     #hourRec = [','.join(elem) for elem in hourRec]
    #
    #     wfile.write('\n'.join(hourRec))




if __name__ == "__main__":
    starttime = time.time()
    # pool = multiprocessing.Pool(processes=12)
    # pool.map(iterateFile, filelist)
    # jnum = 12
    # jobs = []
    # for x in xrange(0, jnum):
    #     jobs.append(Process(target=iterateFile, args=(x)))
    #     jobs[x].start()
    for filename in filelist:
        iterateFile(filename);

    writeRes()
    print("spend time: " + str(time.time()-starttime) + "s")