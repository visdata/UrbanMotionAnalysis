#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 

from math import radians, cos, sin, asin, sqrt, pi 
import math

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

def getGIDByIndex(id, x, y, LngSPLIT=0.0064, LatSPLIT=0.005, locs={
	'north': 41.0500,  # 41.050,
	'south': 39.4570,  # 39.457,
	'west': 115.4220,  # 115.422,
	'east': 117.5000,  # 117.500
}):
	LNGNUM = int( (locs['east'] - locs['west']) / LngSPLIT + 1 )
	
	return id + x + y * LNGNUM

def parseFormatGID(id, direction='n', LngSPLIT=0.0064, LatSPLIT=0.005, locs={
	'north': 41.0500,  # 41.050,
	'south': 39.4570,  # 39.457,
	'west': 115.4220,  # 115.422,
	'east': 117.5000,  # 117.500
}):
	"""
	[NEW] 根据城市网格编号还原经纬度信息，注意：经纬度为中心点信息并非西南角信息
		:param locs: 
		:param id: 
		:param SPLIT=0.05: 
	"""

	id = int(id)
	LNGNUM = int((locs['east'] - locs['west']) / LngSPLIT + 1)
	
	latind = int(id / LNGNUM)
	lngind = id - latind * LNGNUM
	
	lat = (locs['south'] + latind * LatSPLIT)
	lng = (locs['west'] + lngind * LngSPLIT)
	lngcen = (lng + LngSPLIT/2.0)
	latcen = (lat + LatSPLIT/2.0)
	dlineDict = {
		'n': lat + LatSPLIT,
		's': lat,
		'e': lng + LngSPLIT,
		'w': lng
	}

	return {
		'lat': latcen,
		'lng': lngcen,
		'nid': id,
		'pid': -1,
		'y': latind,
		'x': lngind,
		'dlinePoint': dlineDict[direction],
		'dlineDict': dlineDict
	}


def getDirection(fPoint, tPoint):
	# 获取方向信息
	# [Lng, Lat]
	fromLat = float(fPoint[1])
	fromLng = float(fPoint[0])
	toLat = float(tPoint[1])
	toLng = float(tPoint[0])

	absLat = abs(toLat-fromLat)
	absLng = abs(toLng-fromLng)

	if toLng >= fromLng and absLng > absLat:  # 向右半边运动
		return 'e'
	elif toLng < fromLng and absLng > absLat:
		return 'w'
	elif toLat >= fromLat and absLng < absLat:
		return 'n'
	else:
		return 's'

def cosVector(x, y):
	if len(x) != len(y):
		print 'error input,x and y is not in the same space'
		return None

	result1=0.0
	result2=0.0
	result3=0.0
	for i in xrange(0, len(x)):
		result1+=x[i]*y[i]   #sum(X*Y)
		result2+=x[i]**2     #sum(X*X)
		result3+=y[i]**2     #sum(Y*Y)

	return result1 / ((result2*result3)**0.5)

def getGIDsByOffsets(gid, maxOffset, LngSPLIT=0.0064, LatSPLIT=0.005, locs={
	'north': 41.0500,  # 41.050,
	'south': 39.4570,  # 39.457,
	'west': 115.4220,  # 115.422,
	'east': 117.5000,  # 117.500
}):
	"""
	[NEW] 根据中心格子gid，给出附近maxOffset内格子列表，共(2*maxOffset+1)^2个
	"""

	iter_Gids = []

	LNGNUM = int( (locs['east'] - locs['west']) / LngSPLIT + 1 )
	LATNUM = int( (locs['north'] - locs['south']) / LatSPLIT + 1 )

	latind = int(gid/LNGNUM)
	lngind = gid - latind * LNGNUM

	for iter_latind in range(max(latind - maxOffset, 0), min(latind + maxOffset+1, LATNUM)):
		for iter_lngind in range(max(lngind - maxOffset, 0), min(lngind + maxOffset+1, LNGNUM)):
			iter_Gids.append(iter_latind * LNGNUM + iter_lngind)

	return iter_Gids

def getGridIntersection(point, angle, gid, LngSPLIT=0.0064, LatSPLIT=0.005, locs={
	'north': 41.0500,  # 41.050,
	'south': 39.4570,  # 39.457,
	'west': 115.4220,  # 115.422,
	'east': 117.5000,  # 117.500
}):
		"""
		计算交叉点，所有点格式均为 [lng, lat]

		"""

		sGIPoint, eGIPoint = [], []

		gridInfo = parseFormatGID(gid, 'n', LngSPLIT, LatSPLIT, locs)
		
		dlines = ['n', 's', 'w', 'e']
		intersections = {}

		# 处理 竖线 特殊情况
		if angle == 90:
			sGIPoint=[point[0],gridInfo['dlineDict']['s']]
			eGIPoint=[point[0],gridInfo['dlineDict']['n']]
			return sGIPoint, eGIPoint
		elif angle == 270:
			sGIPoint=[point[0],gridInfo['dlineDict']['n']]
			eGIPoint=[point[0],gridInfo['dlineDict']['s']]
			return sGIPoint, eGIPoint

		#直线方程 ax+by+c = 0
		a = math.tan(math.pi * angle/180)
		b = -1
		c = point[1]- a * point[0]

		# 找交点
		for dline in dlines:
			
			if (dline == 'n' or dline == 's') and (a != 0):
				y = gridInfo['dlineDict'][dline]
				x = (-b * y - c)/a
				if (x >= gridInfo['dlineDict']['w']) and (x <= gridInfo['dlineDict']['e']):
					intersections[dline] = [x,y]
			elif dline == 'w' or dline == 'e':
				x = gridInfo['dlineDict'][dline]
				y = (-a * x - c)/b
				if (y > gridInfo['dlineDict']['s']) and (y < gridInfo['dlineDict']['n']):
					intersections[dline] = [x,y]

		keys = intersections.keys()
		if len(keys)!=2:
			print 'getGridIntersection obtains incorrect number of intersections: ' + str(len(keys))
			print 'point: %s, angle: %.1f, grid: %s'%(str(point), angle, str(gridInfo['dlineDict']))
		
		sGIPoint = intersections[keys[0]]
		eGIPoint = intersections[keys[1]]

		# 起始/终止点需要对调
		if (point[0]-sGIPoint[0]) * math.cos(math.pi * angle/180) < 0:
			return eGIPoint, sGIPoint

		return sGIPoint, eGIPoint

def lineIntersection(line1, line2):
    xdiff = [line1[0][0] - line1[1][0], line2[0][0] - line2[1][0]]
    ydiff = [line1[0][1] - line1[1][1], line2[0][1] - line2[1][1]]

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
       return False

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / float(div)
    y = det(d, ydiff) / float(div)
    return [x, y]
	