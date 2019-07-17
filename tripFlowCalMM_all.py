#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# tripFlow 计算
# 
# python tripFlowCal.py -d /home/joe/Documents/git/fake -p /home/joe/Documents/git/fake -e 0.01 -m 40 [grid]
# [circle]
# 
# line
# python tripFlowCal.py -d /datahouse/tao.jiang -p /datahouse/tao.jiang -e 2 -m 10

import sys
import time
import logging
import getopt
from util.tripFlow.extractGridEdgesMM import ExtractGridEdgesMM
from util.tripFlow.dbscanTFIntersections import DBScanTFIntersections
from util.tripFlow.mergeClusterEdgesMM import MergeClusterEdgesMM
from util.tripFlow.lineTFAggregationsMM import LineTFAggregationsMM
			
def processTask(x, eps, K, delta, stdindir, stdoutdir, locs, city, LngSPLIT, LatSPLIT, gridSize):
	suffix = "%.2f" % (delta)
	PROP = {
		'index': x, 
		'delta': delta,
		'gridSize': gridSize,
		'IDIRECTORY': stdindir, 
		'ODIRECTORY': stdoutdir,
		'suffix': suffix,
		'locs': locs,
		'city': city,
		'LngSPLIT': LngSPLIT,
		'LatSPLIT': LatSPLIT
	}
	task = ExtractGridEdgesMM(PROP)
	res = task.run()
	
	count = res['count']
	min_samples = 2

	resByCate = res['res']['resByCate']
	dataType = 'angle'  # 确定是按照方向聚类还是角度聚�?direction, category
		
	clusterPROP = {
		'index': x, 
		'ODIRECTORY': stdoutdir,
		'resByAng': resByCate,
		'dataType': dataType,
		'eps': eps,
		'min_samples': min_samples,
		'suffix': suffix,
		'locs': locs,
		'city':city,
		'LngSPLIT': LngSPLIT,
		'LatSPLIT': LatSPLIT
	}

	print '''
		===	Cluster Parameters	===
		index	= %d
		stdindir	= %s
		stdoutdir	= %s
		min_samples	= %d
		===	Cluster Parameters	===
		''' % (x, stdindir, stdoutdir, min_samples)

	clusterTask = LineTFAggregationsMM(clusterPROP)
	noiseRate, clusterofilename = clusterTask.run()

	mergePROP = {
		'index': x,
		'IDIRECTORY': stdindir,
		'ODIRECTORY': stdoutdir,
		'dataType': dataType,
		'suffix': suffix,
		'city':city
	}
	mergeTask = MergeClusterEdgesMM(mergePROP)
	mergeTask.run()

def usage():
	# /datahouse/zhtan/datasets/VIS-rawdata-region/
	print "(by default parameters set explicitly in the code) python tripFlowCal.py -d /datasets -p /datasets -e 2 -x 18 -k 24000"


def main(argv):
	cityLatLngDict = {
		'BJ':{
			'north': 41.0500,  # 41.050,
			'south': 39.4570,  # 39.457,
			'west': 115.4220,  # 115.422,
			'east': 117.5000,  # 117.500
		},
		'TJ': {
			'north': 40.2500,  # 40.1500,
			'south': 38.5667,  # 38.340,
			'west': 116.7167,  # 116.430,
			'east': 118.3233,  # 118.1940
			},
		#117°30'—119°19'、38°55'—40°20'
		'TS':{
			'north': 40.3333,  # 41.050,
			'south': 35.9167,  # 39.457,
			'west': 117.50,  # 115.422,
			'east': 119.3167,  # 117.500
		}
	}

	gridSizeDict = {
		500: [0.0064, 0.005],
		100: [0.00128, 0.001],
		250: [0.0032, 0.0025],
		1000:[0.0128, 0.01],
		2000:[0.0256, 0.02],
		4000:[0.0512, 0.04],
		5000:[0.064, 0.05]
	}

	gridSize = 500
	LngSPLIT = gridSizeDict[gridSize][0]
	LatSPLIT = gridSizeDict[gridSize][1]
	city = 'BJ'
	try:
		argsArray = ["help", 'stdindir=', 'stdoutdir=', "eps=", "min_samples=", "index=", "delta=", "kval="]
		opts, args = getopt.getopt(argv, "hd:p:e:m:x:t:k:", argsArray)
	except getopt.GetoptError as err:
		print str(err)
		usage()
		sys.exit(2)

	stdindir = '/datahouse/tripflow/2019-30-800-'+city
	stdoutdir = '/datahouse/tripflow/2019-30-800-'+city

	if gridSize != 500:
		stdoutdir = '/datahouse/hcc/grid-' + str(gridSize)
	# if gridSize == 100:
	# 	stdoutdir = '/datahouse/hcc/grid-100'
	# if gridSize == 250:
	# 	stdoutdir = '/datahouse/hcc/grid-250'
	# if gridSize == 1000:
	# 	stdoutdir = '/datahouse/hcc/grid-1000'
	# if gridSize == 2000:
	# 	stdoutdir = '/datahouse/hcc/grid-2000'
	# if gridSize == 4000:
	# 	stdoutdir = '/datahouse/hcc/grid-4000'

	# stdindir = '/datahouse/tripflow/2019-30-1200'
	# stdoutdir = '/datahouse/tripflow/2019-30-1200'
	#eps = 2 initial
	#eps = 4 bj, tj
	#eps = 3 #from shil
	eps = 2 #grid = 100
	# min_samples = 10
	delta = -1
	# x = 9
	#K = 24000 initial
	K=60000
	#bj tj the first three days
	#K = 12000 #bj tj
	#K = 10000 ts

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
			sys.exit()
		elif opt in ("-d", "--stdindir"):
			stdindir = arg
		elif opt in ('-p', '--stdoutdir'):
			stdoutdir = arg
		elif opt in ("-e", "--eps"):
			eps = float(arg)
		# elif opt in ('-m', '--min_samples'):
		# 	min_samples = int(arg)
		# elif opt in ('-x', '--index'):
		# 	x = int(arg)
		elif opt in ('-t' '--delta'):
			delta = float(arg)
		elif opt in ('-k' '--kval'):
			K = int(arg)				

	STARTTIME = time.time()
	print "Start approach at %s" % STARTTIME

	# print '''
	# ===	Cluster Opts	===
	# stdindir	= %s
	# stdoutdir	= %s
	# eps		= %f
	# min_samples	= %d
	# ===	Cluster Opts	===
	# ''' % (stdindir, stdoutdir, eps, min_samples)

	# process for the time offset [startX, endX]

	startX = 1736
	endX = 1736

	for i in xrange(startX,endX+1):
		processTask(i, eps, K, delta, stdindir, stdoutdir, cityLatLngDict[city], city, LngSPLIT, LatSPLIT, gridSize)


	#processTask(x, eps, K, delta, stdindir, stdoutdir)

	# @多进程运行程�?END
	ENDTIME = time.time()
	print "END TIME: %s" % ENDTIME
	print "Total minutes: %f" % ((ENDTIME-STARTTIME)/60.0)


if __name__ == '__main__':
	logging.basicConfig(filename='logger-tripflowcal.log', level=logging.DEBUG)
	main(sys.argv[1:])