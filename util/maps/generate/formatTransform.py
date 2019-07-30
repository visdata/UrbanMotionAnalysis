'''
路网格式转换，由{GridID:[[road1],[road2]...]}转换为{GridID:[road1', road2']},其中
road1格式：startLon,startLat,endLon,endLat,angle
road1'格式(字符串)："startLon,startLat,endLon,endLat,angle"
'''
import json
import time

filename = 'mroad.json'
ISOTIMEFORMAT="%Y-%m-%d %X"
roads = {}
with open(filename, 'r') as ifile:
	roads = json.loads(ifile.read())
convert_roads = {}
count  = 0
for k, v in roads.items():
	convert_roads.update({k:[]})
	for part in v:
		line = str(part[0]) + ',' + str(part[1]) + ',' + str(part[2]) + ',' + str(part[3]) + ',' + str(part[4])
		convert_roads[k].append(line)
		count = count + 1
	'''
	if count > 10:
		break
	'''
	if count%10000 == 0:
		print(time.strftime( ISOTIMEFORMAT),", process%d"%count)
# print(convert_roads)
filename = 'road-network.json'
with open(filename, 'w') as ofile:
	json.dump(convert_roads, ofile)
print(time.strftime( ISOTIMEFORMAT),", Finished.")