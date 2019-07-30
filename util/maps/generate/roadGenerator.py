'''
生成路网，格式为{GridID：[[road1],[road2]...]}, road1格式：startLon,startLat,endLon,endLat,angle
'''
import json
import math
import time

# 计算角度
def angle(v1):
    dx1 = v1[2] - v1[0]
    dy1 = v1[3] - v1[1]
    angle1 = math.atan2(dy1, dx1)
    angle1 = float(angle1 * 180/math.pi)
    included_angle = angle1%360
    return round(included_angle, 1)

#计算gridID
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


MAXUNIT = 100 # 进行插值的粒度阈值
filename = 'mergeWay.json'
ISOTIMEFORMAT="%Y-%m-%d %X"
roads = {}
print(time.strftime( ISOTIMEFORMAT),", Start.")
with open(filename, 'r') as ifile:
	roads = json.loads(ifile.read())
# print('num of roads: %d'%len(roads))
num_trips = 0
for k, v in roads.items():
	num_trips = num_trips + len(v)
print('num of trips: %d'%num_trips)
count = 0
roadsInGrid = {}
for k, v in roads.items():
	for part in v:
		gridIDs = getFormatGID([part[0], part[1]])
		gridIDt = getFormatGID([part[2], part[3]])
		count = count + 1
		agl = angle(part)
		agl_op = (agl - 180)%360
		trip = [part[0], part[1], part[2], part[3], agl]
		trip_op = [part[0], part[1], part[2], part[3], agl_op]
		# 处理起始点和终点
		if gridIDs['gid'] in roadsInGrid.keys():
			roadsInGrid[gridIDs['gid']].append(trip)
			roadsInGrid[gridIDs['gid']].append(trip_op)
		else:
			roadsInGrid.update({gridIDs['gid']:[trip]})
			roadsInGrid[gridIDs['gid']].append(trip_op)
		if int(gridIDt['gid']) == int(gridIDs['gid']):
			continue# do nothing , don't count twice
		elif gridIDt['gid'] in roadsInGrid.keys():
			roadsInGrid[gridIDt['gid']].append(trip)
			roadsInGrid[gridIDt['gid']].append(trip_op)
		else:
			roadsInGrid.update({gridIDt['gid']:[trip]})
			roadsInGrid[gridIDt['gid']].append(trip_op)
		# 利用插值处理中间可能经过的区域	
		lonUnit = (part[2] - part[0]) / MAXUNIT
		latUnit = (part[3] - part[1]) / MAXUNIT
		IDlist = []
		for n in range(1, MAXUNIT):
			gridID = getFormatGID([part[0]+n*lonUnit, part[1]+n*latUnit])
			if gridID['gid'] == gridIDs['gid'] or gridID['gid'] == gridIDt['gid'] or gridID['gid'] in IDlist:
				# 保证同一条路不在grid上重复出现
				continue
			elif gridID['gid'] in roadsInGrid.keys():
				roadsInGrid[gridID['gid']].append(trip)
				roadsInGrid[gridID['gid']].append(trip_op)
				IDlist.append(gridID['gid'])
			else:
				roadsInGrid.update({gridID['gid']:[trip]})
				roadsInGrid[gridID['gid']].append(trip_op)
				IDlist.append(gridID['gid'])
	if count%100000 == 0:
		print(time.strftime( ISOTIMEFORMAT),", process %d"%count)
print('num of grid: %d'%len(roadsInGrid))
num_road = 0
for k, v in roadsInGrid.items():
	num_road = num_road + len(v)
print('num of roads: %d'%num_road)
filename = 'mroad.json'
with open(filename, 'w') as ofile:
	json.dump(roadsInGrid, ofile)
print(time.strftime( ISOTIMEFORMAT),", Finished.")