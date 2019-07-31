'''
生成路网，格式为{GridID：[[road1],[road2]...]}, road1格式：startLon,startLat,endLon,endLat,angle
'''
import json
import math
import time

# 计算角度

#计算角度
def angleFromTo(fromLon, fromLat, toLon, toLat):

	vecX = toLon - fromLon
	vecY = toLat - fromLat
	vecDis = math.sqrt(pow(vecY, 2) + pow(vecX, 2))

	if vecDis == 0:
		return 0

	angleLng = vecX / vecDis
	angleLat = vecY / vecDis

	angle = math.acos(angleLng) * 180 / math.pi
	if angleLat < 0 and angle > 0.1:
		angle = 360 - angle

	return angle

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

MAX_UNIT = 20
MAX_UNIT_BY_RADIAN = math.sqrt(0.0064 * 0.0064 + 0.005 * 0.005) / MAX_UNIT # 进行插值的粒度阈值

ifilename = '/datahouse/tripflow/maps/BJ/org/way.json'
ISOTIMEFORMAT="%Y-%m-%d %X"
roads = {}
print(time.strftime(ISOTIMEFORMAT),", Start.")

with open(ifilename, 'r') as ifile:
	roads = json.loads(ifile.read())

num_trips = 0
for k, v in roads.items():
	num_trips = num_trips + len(v)
print('num of ways to process: %d'%num_trips)

count = 0
roadsInGrid = {}

for k, v in roads.items():
	for part in v:
		count = count + 1

		gridIDDict = {}

		gridIDs = getFormatGID([part[0], part[1]])
		gridIDt = getFormatGID([part[2], part[3]])
		
		angle = angleFromTo(part[0], part[1], part[2], part[3])
		angle_op = (angle - 180)%360
		trip = [part[0], part[1], part[2], part[3], angle]
		trip_op = [part[2], part[3], part[0], part[1], angle_op]

		gridIDDict[gridIDs['gid']] = 1
		gridIDDict[gridIDt['gid']] = 1

		# 利用插值处理中间可能经过的格子
		startLng = part[0]
		startLat = part[1]
		endLng = part[2]
		endLat = part[3]
		segDist = math.sqrt((part[0]- part[2])*(part[0]- part[2])+(part[1]- part[3])*(part[1]- part[3]))

		interLength = int(segDist/MAX_UNIT_BY_RADIAN)

		for offset in range(1, interLength+1):
			ratio = (MAX_UNIT_BY_RADIAN * offset)/segDist
			midLng = startLng + (endLng-startLng) * ratio
			midLat = startLat + (endLat-startLat) * ratio
			gridIDm = getFormatGID([midLng, midLat])
			gridIDDict[gridIDm['gid']] = 1

		# 处理所有经过格子
		for gridID in gridIDDict:
			if gridID in roadsInGrid.keys():
				roadsInGrid[gridID].append(trip)
				roadsInGrid[gridID].append(trip_op)
			else:
				roadsInGrid.update({gridID:[trip]})
				roadsInGrid[gridID].append(trip_op)
	
	if count%10000 == 0:
		print(time.strftime( ISOTIMEFORMAT),", process %d"%count)

print('num of grid: %d'%len(roadsInGrid.keys()))
num_road = 0
for k, v in roadsInGrid.items():
	num_road = num_road + len(v)
print('num of roads: %d'%num_road)

'''
路网格式转换，由{GridID:[[road1],[road2]...]}转换为{GridID:[road1', road2']},其中
road1格式：startLon,startLat,endLon,endLat,angle
road1'格式(字符串)："startLon,startLat,endLon,endLat,angle"
'''

roads = roadsInGrid
convert_roads = {}
count  = 0
for k, v in roads.items():
	convert_roads.update({k:[]})
	for part in v:
		line = str(part[0]) + ',' + str(part[1]) + ',' + str(part[2]) + ',' + str(part[3]) + ',' + str(part[4])
		convert_roads[k].append(line)
		count = count + 1

	if count%10000 == 0:
		print(time.strftime(ISOTIMEFORMAT),", format transformation: %d"%count)

ofilename = '/datahouse/tripflow/maps/BJ/org/road-network.json'
with open(ofilename, 'w') as ofile:
	json.dump(convert_roads, ofile)
print(time.strftime( ISOTIMEFORMAT),", Finished.")