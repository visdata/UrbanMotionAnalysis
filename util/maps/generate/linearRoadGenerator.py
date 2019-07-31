'''
way指的是road的一个个分段，osm中way是由node的id组成，需要转换为对应的经纬度
'''
import json
from math import radians, cos, sin, asin, sqrt, pi, pow, acos
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

#计算角度
def angleFromTo(fromLon, fromLat, toLon, toLat):

	vecX = toLon - fromLon
	vecY = toLat - fromLat
	vecDis = sqrt(pow(vecY, 2) + pow(vecX, 2))

	if vecDis == 0:
		return 0

	angleLng = vecX / vecDis
	angleLat = vecY / vecDis

	angle = acos(angleLng) * 180 / pi
	if angleLat < 0 and angle > 0.1:
		angle = 360 - angle

	return angle

def angleDist(angle1, angle2):
	dist = abs(angle1-angle2)
	if dist > 180:
		dist = 360-dist
	return dist

# 角度变化固定为逆时针; minAngle起始角度, maxAngle按给逆时针顺序的终止角度
def putAngleToRange(curAngle, curMinAngle, curMaxAngle, angleRangeBound):

	newMinAngle = curMinAngle
	newMaxAngle = curMaxAngle
	success = True

	# 跨越0度
	if abs(curMaxAngle-curMinAngle)>angleRangeBound:
		# 在当前range内部
		if curAngle <= curMaxAngle or curAngle >= curMinAngle:
			return newMinAngle, newMaxAngle, success
		
		# 不在当前range内部
		if (curAngle-curMaxAngle) <= (curMinAngle - curAngle):
			newMaxAngle = curAngle
		else:
			newMinAngle = curAngle

		# 超过bound
		if (360-abs(newMaxAngle-newMinAngle))>angleRangeBound:
			success = False
			newMinAngle = curAngle
			newMaxAngle = curAngle
	# 不跨越0度
	else:
		# 在当前range内部
		if curAngle <= curMaxAngle and curAngle >= curMinAngle:
			return newMinAngle, newMaxAngle, success
		
		# 不在当前range内部
		if angleDist(curAngle, curMaxAngle) <= angleDist(curMinAngle, curAngle):
			newMaxAngle = curAngle
		else:
			newMinAngle = curAngle

		# 超过bound
		if (360-abs(newMaxAngle-newMinAngle))>angleRangeBound and abs(newMaxAngle-newMinAngle)>angleRangeBound:
			success = False
			newMinAngle = curAngle
			newMaxAngle = curAngle

	return newMinAngle, newMaxAngle, success


angleRangeBound = 10
minDistBound = 500

segNumDict = {}
segDistDict = {}

reportPercentages = [1, 5, 10, 50, 100, 500, 1000]

filename1 = '/datahouse/tripflow/maps/BJ/org/interpreter_node.json'
filename2 = '/datahouse/tripflow/maps/BJ/org/interpreter_way.json'

ofilename = '/datahouse/tripflow/maps/BJ/org/way.json'

# 提取node信息
ifile = open(filename1, 'r')
nodes = [json.loads(x.rstrip()) for x in ifile.readlines()]
node_dict = {}
for node in nodes:
	node_dict[node['id']] = [round(float(node['lon']),6), round(float(node['lat']),6)]
# print(node_dict)
ifile.close()

ifile = open(filename2)
ways = [json.loads(x.rstrip()) for x in ifile.readlines()]
# print(ways[1]['id'])
# print(node_dict[ways[1]['nd'][0]['ref']])
# print(node_dict[ways[1]['nd'][1]['ref']])
way_dict = {}
# 把way中的id转换为对应id的node的经纬度数值

numOfWays = 0
numOfSegs = 0
numOfValidSegs = 0
sumDist = 0

for way in ways:
	tempWay = []

	way_length = len(way['nd'])

	if way_length <= 1:
		continue

	numOfWays+=1

	startLon = float(node_dict[way['nd'][0]['ref']][0])
	startLat = float(node_dict[way['nd'][0]['ref']][1])

	endLon = float(node_dict[way['nd'][1]['ref']][0])
	endLat = float(node_dict[way['nd'][1]['ref']][1])

	curAngle = angleFromTo(startLon, startLat, endLon, endLat)

	curStartIndex = 0
	curEndIndex = 1

	curMaxAngle = curAngle
	curMinAngle = curAngle

	for index in range(1, way_length - 1):

		startLon = float(node_dict[way['nd'][index]['ref']][0])
		startLat = float(node_dict[way['nd'][index]['ref']][1])

		endLon = float(node_dict[way['nd'][index+1]['ref']][0])
		endLat = float(node_dict[way['nd'][index+1]['ref']][1])

		curAngle = angleFromTo(startLon, startLat, endLon, endLat)

		curMinAngle, curMaxAngle, success = putAngleToRange(curAngle, curMinAngle, curMaxAngle, angleRangeBound)

		if success:
			curEndIndex = index + 1
		else:
			# output the current segment
			startLon = float(node_dict[way['nd'][curStartIndex]['ref']][0])
			startLat = float(node_dict[way['nd'][curStartIndex]['ref']][1])

			endLon = float(node_dict[way['nd'][curEndIndex]['ref']][0])
			endLat = float(node_dict[way['nd'][curEndIndex]['ref']][1])

			dist = getRealDistance(startLon, startLat, endLon, endLat)
			distIndex = str(math.ceil(dist/10))
			
			if dist >= minDistBound:
				tempWay.append([startLon, startLat, endLon, endLat])
				numOfValidSegs+=1

			if distIndex in segNumDict:
				segNumDict[distIndex] += 1
			else:
				segNumDict[distIndex] = 1

			if distIndex in segDistDict:
				segDistDict[distIndex] += dist
			else:
				segDistDict[distIndex] = dist

			numOfSegs+=1
			sumDist+=dist

			curStartIndex = curEndIndex
			curEndIndex = index + 1

			
	# output the last segment
	startLon = float(node_dict[way['nd'][curStartIndex]['ref']][0])
	startLat = float(node_dict[way['nd'][curStartIndex]['ref']][1])

	endLon = float(node_dict[way['nd'][curEndIndex]['ref']][0])
	endLat = float(node_dict[way['nd'][curEndIndex]['ref']][1])

	dist = getRealDistance(startLon, startLat, endLon, endLat)
	distIndex = str(math.ceil(dist/10))

	if dist >= minDistBound:
		tempWay.append([startLon, startLat, endLon, endLat])
		numOfValidSegs+=1

	if distIndex in segNumDict:
		segNumDict[distIndex] += 1
	else:
		segNumDict[distIndex] = 1

	if distIndex in segDistDict:
		segDistDict[distIndex] += dist
	else:
		segDistDict[distIndex] = dist

	numOfSegs+=1
	sumDist+=dist

	if len(tempWay)>0:
		way_dict[way['id']] = tempWay

	if numOfWays%10000==0:
		print("Process %d ways..."%numOfWays)

print("Num of road segments: %d"%numOfSegs)
print("Num of valid ways: %d"%len(way_dict.keys()))
print("Num of valid road segments: %d"%numOfValidSegs)

for boundDistIndex in reportPercentages:
	boundDist = boundDistIndex * 10

	boundNumSum = 0
	for distIndex in segNumDict:
		if int(distIndex)<=boundDistIndex:
			boundNumSum+=segNumDict[distIndex]

	boundDistSum = 0
	for distIndex in segDistDict:
		if int(distIndex)<=boundDistIndex:
			boundDistSum+=segDistDict[distIndex]

	print("Segment distance <= %d by count: %.4f"%(boundDist, float(boundNumSum)/numOfSegs))
	print("Segment distance <= %d by dist : %.4f"%(boundDist, float(boundDistSum)/sumDist))

ifile.close()
with open(ofilename, 'w') as ofile:
	json.dump(way_dict, ofile)