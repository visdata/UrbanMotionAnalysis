'''
处理osm文件，从xml格式中提取way和node
'''
from pprint import *
import json
import time
from lxml import etree
import xmltodict
import sys
import getopt

# 将指定tag的对象提取，写入json文件。 
def process_element(fnode, fway, elem, tag_dict):

	valid_way_dict = {"highway":1, "railway":1, "waterway":1, "aerialway":1, "subway":1}

	elem_data = etree.tostring(elem)
	elem_dict = xmltodict.parse(elem_data,attr_prefix="",cdata_key="")
	#print(elem_dict)

	parse_node_num, parse_way_num, parse_valid_way_num = 0, 0, 0
	
	if (elem.tag == "node"):
		parse_node_num += 1
		elem_jsonStr = json.dumps(elem_dict["node"])
		fnode.write(elem_jsonStr + "\n")
	elif (elem.tag == "way"):
		parse_way_num += 1
		valid_way = False

		if "tag" in elem_dict["way"]:
			tags = elem_dict["way"]["tag"]

			if "k" in tags:
				tag_key = str(tags["k"]).lower()
				if tag_key not in tag_dict:
					tag_dict[tag_key] = 1

				if tag_key in valid_way_dict:
					valid_way = True
			else:
				for index in range(len(tags)):
					
					tag_key = str(tags[index]["k"]).lower()
					if tag_key not in tag_dict:
						tag_dict[tag_key] = 1

					if tag_key in valid_way_dict:
						valid_way = True

		if valid_way:
			parse_valid_way_num += 1
			elem_jsonStr = json.dumps(elem_dict["way"])
			fway.write(elem_jsonStr + "\n")

	return parse_node_num, parse_way_num, parse_valid_way_num

# 遍历所有对象，然后调用process_element处理。
# 迭代处理，func为迭代的element处理函数。
def fast_iter(context, maxline, fnode, fway, tag_dict):
	placement = 0
	total_parse_node_num, total_parse_way_num, total_parse_valid_way_num = 0, 0, 0
	try:
		for _, elem in context:
			
			parse_node_num, parse_way_num, parse_valid_way_num = process_element(fnode, fway, elem, tag_dict)  #处理每一个元素,调用process_element.    
			total_parse_node_num+=parse_node_num
			total_parse_way_num+=parse_way_num
			total_parse_valid_way_num+=parse_valid_way_num
			placement += 1

			if placement%100000==0:
				print("Process %d lines..."%placement)

			if (maxline > 0 and placement >= maxline):  # 最多的转换对象限制，大数据调试时使用于抽样检查。
				break 

	except Exception as ex:
		print(time.time(),", Error:",ex.message)
		
	return total_parse_node_num, total_parse_way_num, total_parse_valid_way_num

def usage():
	print ("(by default parameters set explicitly in the code) python3 osm2json.py -s /dir-of-input -l 'maxline'")


def main(argv):
	
	try:
		argsArray = ["help", 'stdinfile=', 'line=']
		opts, args = getopt.getopt(argv, "hs:l:", argsArray)
	except getopt.GetoptError as err:
		print (str(err))
		usage()
		sys.exit(2)

	# 需要处理的osm文件名，自行修改。
	stdinfile = '/datahouse/tripflow/maps/BJ/org/interpreter'
	maxline = 0  #抽样调试使用，最多转换的对象，设为0则转换文件的全部。

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
			sys.exit()
		elif opt in ("-l", "--line"):
			maxline = int(arg)
		elif opt in ('-s', '--stdinfile'):
			stdinfile = arg

	STARTTIME = time.time()
	print ("Start at %s" % STARTTIME)

	fnode = open(stdinfile + "_node.json","w+")
	fway = open(stdinfile + "_way.json","w+")
	tag_dict = {}

	# context = etree.iterparse(stdinfile,tag=["node","way"])
	context = etree.iterparse(stdinfile,tag=["way"])
	parse_node_num, parse_way_num, parse_valid_way_num = fast_iter(context, maxline, fnode, fway, tag_dict)
		
	fnode.close()
	fway.close()

	ENDTIME = time.time()
	print ("END TIME: %s" % ENDTIME)
	print ("Total minutes: %f" % ((ENDTIME-STARTTIME)/60.0))
	print ("Tag name list: %s" % tag_dict.keys())
	print ("parse_node_num: %d"%parse_node_num)
	print ("parse_way_num: %d"%parse_way_num)
	print ("parse_valid_way_num: %d (%.2f%%)"%(parse_valid_way_num, float(parse_valid_way_num)*100/(parse_way_num+0.000001)))

if __name__ == '__main__':
	main(sys.argv[1:])