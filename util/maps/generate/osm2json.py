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
def process_element(elem):
	elem_data = etree.tostring(elem)
	elem_dict = xmltodict.parse(elem_data,attr_prefix="",cdata_key="")
	#print(elem_dict)
	
	if (elem.tag == "node"): 
		elem_jsonStr = json.dumps(elem_dict["node"])
		fnode.write(elem_jsonStr + "\n")
	elif (elem.tag == "way"): 
		elem_jsonStr = json.dumps(elem_dict["way"])
		fway.write(elem_jsonStr + "\n")
	elif (elem.tag == "relation"): 
		elem_jsonStr = json.dumps(elem_dict["relation"])
		frelation.write(elem_jsonStr + "\n")

# 遍历所有对象，然后调用process_element处理。
# 迭代处理，func为迭代的element处理函数。
def fast_iter(context, func, maxline):
	placement = 0
	try:
		for event, elem in context:
			placement += 1
			if (maxline > 0):  # 最多的转换对象限制，大数据调试时使用于抽样检查。 
				print(etree.tostring(elem))
				if (placement >= maxline): break

			func(elem)  #处理每一个元素,调用process_element.      
			elem.clear()
			while elem.getprevious() is not None:
			   del elem.getparent()[0]
	except Exception as ex:
		print(time.time(),", Error:",ex)
		
	del context

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
	frelation = open(stdinfile + "_relation.json","w+")

	context = etree.iterparse(stdinfile,tag=["node","way","relation"])
	fast_iter(context, process_element, maxline)
		
	fnode.close()
	fway.close()
	frelation.close()

	ENDTIME = time.time()
	print ("END TIME: %s" % ENDTIME)
	print ("Total minutes: %f" % ((ENDTIME-STARTTIME)/60.0))

if __name__ == '__main__':
	main(sys.argv[1:])