'''
way指的是road的一个个分段，osm中way是由node的id组成，需要转换为对应的经纬度
'''
import json

filename1 = 'interpreter_node.json'
filename2 = 'interpreter_way.json'

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
for way in ways:
	temp = []
	for index in range(len(way['nd']) - 1):
		temp.append([float(node_dict[way['nd'][index]['ref']][0]),
			float(node_dict[way['nd'][index]['ref']][1]),
			float(node_dict[way['nd'][index+1]['ref']][0]),
			float(node_dict[way['nd'][index+1]['ref']][1])])
	way_dict[way['id']] = temp
# print(len(way_dict))
# print(way_dict['4231223'])
ifile.close()
with open('way.json', 'w') as ofile:
	json.dump(way_dict, ofile)