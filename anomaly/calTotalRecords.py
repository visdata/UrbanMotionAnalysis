# -*- coding: utf-8 -*-
__author__ = 'lenovo'

# calculate stay/travel/all device number of each grid

import time
import multiprocessing
from multiprocessing import Process
import os
import json
res = [0 for j in range(87)]



filelist  = ['part-'+format(n, '05d')+'-trajectory_30-800' for n in range(0, 10000)]

input_path = '/datahouse/yurl/TalkingData/data/P3-SS-BJ/'
output_path = '/datahouse/tripflow/Anomaly/bj-flowcount'

def getFormatGID(point, LngSPLIT=0.0064, LatSPLIT=0.005, locs={
	'north': 41.0500,  # 41.050,
	'south': 39.4570,  # 39.457,
	'west': 115.4220,  # 115.422,
	'east': 117.5000,  # 117.500
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
        for line in f:
            records = line.split('|')
            for record in records:
                columns = record.split(',')
                timestamp = int(columns[1])
                ydayCurrent = formatTime(timestamp)['yday'] - 187
                if len(columns) < 5:
                    continue
                elif columns[4] == '1' and ydayCurrent >=0 and ydayCurrent<= 86:
                    res[ydayCurrent] += 1

    f.close()

def writeRes():
    # with open(os.path.join(output_path, "flowcountByday.json"), 'wb') as output:
    #     output.write(json.dumps(res));
    print(res)



if __name__ == "__main__":
    starttime = time.time()
    for filename in filelist:
        iterateFile(filename);

    writeRes()
    print("spend time: " + str(time.time()-starttime) + "s")
