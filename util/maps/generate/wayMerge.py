import json
import math
import time
from geopy.distance import geodesic

# 计算角度
def angle(v1):
	dx1 = v1[2] - v1[0]
	dy1 = v1[3] - v1[1]
	angle1 = math.atan2(dy1, dx1)
	angle1 = float(angle1 * 180/math.pi)
	included_angle = angle1%360
	return round(included_angle, 1)

MAXDEGREE = 5 # 待合并的两条路段角度差值的误差范围
MINDIS = 500 # 路段长度的阈值
filename = 'way.json'
ISOTIMEFORMAT="%Y-%m-%d %X"
roads = {}
merge_roads = {}
merge_count = 0
print(time.strftime( ISOTIMEFORMAT),", Start.")
with open(filename, 'r') as ifile:
	roads = json.loads(ifile.read())
# 合并操作
for k, v in roads.items():
	start_index = 0
	while(start_index<len(v)):
		agl = angle(v[start_index])
		for cur_index in range(start_index, len(v)):
			cur_agl = angle(v[cur_index])
			merge_trip = [v[start_index][0], v[start_index][1], v[cur_index-1][2], v[cur_index-1][3]]
			if geodesic((merge_trip[1],merge_trip[0]),(merge_trip[3],merge_trip[2])).m > MINDIS and abs(agl - cur_agl)>MAXDEGREE:
				# print(merge_trip)
				# 满足合并要求，进行合并
				if k not in merge_roads.keys():
					merge_roads.update({k:[merge_trip]})
				else:
					merge_roads[k].append(merge_trip)
				start_index = cur_index
				merge_count = merge_count + 1
				break
			if cur_index == len(v) - 1:
				# 处理没有满足合并要求的部分
				merge_trip = [v[start_index][0], v[start_index][1], v[cur_index][2], v[cur_index][3]]
				if k not in merge_roads.keys():
					merge_roads.update({k:[merge_trip]})
				else:
					merge_roads[k].append(merge_trip)
				start_index = cur_index + 1
				merge_count = merge_count + 1
				break
		if (merge_count+1)%100000==0:
			print(time.strftime( ISOTIMEFORMAT),", Processing %d."%(merge_count+1))

filename = 'mergeWay.json'
with open(filename, 'w') as ofile:
	json.dump(merge_roads, ofile)
print(time.strftime( ISOTIMEFORMAT),", Finish.")


