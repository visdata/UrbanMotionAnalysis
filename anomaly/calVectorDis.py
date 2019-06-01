#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#from util.tripFlow.base import getRealDistance
import numpy as np

from math import radians, cos, sin, asin, sqrt

def getRealDistance(lon1, lat1, lon2, lat2):  # 经度1，纬度1，经度2，纬度2 （十进制度数）
	"""
	Calculate the great circle distance between two points
	on the earth (specified in decimal degrees)
	"""
	# 将十进制度数转化为弧度
	lon1 = float(lon1)
	lat1 = float(lat1)
	lon2 = float(lon2)
	lat2 = float(lat2)

	lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

	# haversine公式
	dlon = lon2 - lon1
	dlat = lat2 - lat1
	a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
	c = 2 * asin(sqrt(a))
	r = 6371  # 地球平均半径，单位为公里
	return c * r * 1000.0
inputDir = "/datahouse/tripflow/2019-30-800-BJ/bj-byhour-tf/"
starthourid = 0;
endhourid = 24

res = []
for hourId in range(starthourid, endhourid):
    filename = "traveldata-"+str(hourId)

    ifile = inputDir + filename
    print(ifile)

    with open(ifile, 'rb') as f:
        records = f.readlines()

    for record in records:
        columns = record.split(',')

        res.append(getRealDistance(float(columns[4]), float(columns[3]), float(columns[5]), float(columns[6])))
        res.append(getRealDistance(float(columns[4]), float(columns[3]), float(columns[8]), float(columns[9])))

    f.close()

np.save('distance.npy', res)