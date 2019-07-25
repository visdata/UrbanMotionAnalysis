#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# treeMap ����
# 
# python treeMapCal.py -d /home/joe/Documents/git/fake -p /home/joe/Documents/git/fake -e 0.01 -m 40 [grid]
# [circle]
# 
# line
# python treeMapCal.py -d /datahouse/tao.jiang -p /datahouse/tao.jiang -e 2 -m 10


import sys
import time
import logging
from util.tripFlow.constructTreeMapMM import ConstructTreeMapMM

	
def processTask(x, stdindir, stdoutdir, tree_num, search_angle, seed_strength, tree_width, jump_length, seed_unit, grid_dirnum, delta, max_distance, grid_size, city):
	dataType = 'angle'
	LngSPLIT = 0.0064
	LatSPLIT = 0.005

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
		'TS':{
			'north': 40.3333,  # 41.050,
			'south': 35.9167,  # 39.457,
			'west': 117.50,  # 115.422,
			'east': 119.3167,  # 117.500
		}
	}

	locs = cityLatLngDict[city]
	if grid_size == 100:
		LatSPLIT = 0.001
		LngSPLIT = 0.00128
	if grid_size == 250:
		LatSPLIT = 0.0025
		LngSPLIT = 0.0032
	if grid_size == 1000:
		LatSPLIT = 0.01
		LngSPLIT = 0.0128
	if grid_size == 2000:
		LatSPLIT = 0.02
		LngSPLIT = 0.0256
	if grid_size == 4000:
		LatSPLIT = 0.04
		LngSPLIT = 0.0512
	if grid_size == 5000:
		LatSPLIT = 0.05
		LngSPLIT = 0.064

	custom_params = {
		'tree_num': tree_num,
		'search_angle': search_angle,
		'seed_strength': seed_strength,
		'max_curvation': 90,
		'tree_width': tree_width,
		'jump_length': jump_length,
		"seed_unit": seed_unit,
		"grid_dirnum": grid_dirnum,
		'max_distance': max_distance,
		'LngSPLIT': LngSPLIT,
		'LatSPLIT': LatSPLIT,
		'delta': delta,
		'city': city,
		'locs': locs
	}

	hotspot_dir = "from"
	if seed_unit == 'thub':
		hotspot_dir = 'to'

	PROP = {
		'index': x, 
		'IDIRECTORY': stdindir, 
		'ODIRECTORY': stdoutdir,
		'dataType': dataType,
		'hotspot_dir': hotspot_dir,
		'custom_params': custom_params
	}
	task = ConstructTreeMapMM(PROP)
	task.run()


def usage():
	# print "python treeMapCal.py -d /dir -p /dir -x 9 -n 0.03 -a 60 -s 0.3 -w 3 -l 3"

	# 'stdindir='
	# 'stdoutdir'
	# "index="
	# "tree_num"
	# "search_angle"
	# "seed_strength"
	# "tree_width"
	# "jump_length"
	# "seed_unit"
	# "grid_dirnum"
	# "delta"
	print "python treeMapCalMM.py /datahouse/tripflow/200 /datahouse/tripflow/200 9 0.03 60 0.1 1 3 basic -1 1 9999"


def main(argv):

	[indir, outdir, x, tree_num, search_angle, seed_strength, tree_width, jump_length, seed_unit, grid_dirnum, delta, max_distance, grid_size, city] = argv
	x = int(x)
	tree_num = float(tree_num)
	search_angle = int(search_angle)
	seed_strength = float(seed_strength)
	tree_width = int(tree_width)
	jump_length = int(jump_length)
	grid_dirnum = int(grid_dirnum)
	delta = float(delta)
	max_distance = float(max_distance)
	grid_size = int(grid_size)
	city = str(city)

	STARTTIME = time.time()
	print "Start approach at %s" % STARTTIME

	processTask(x, indir, outdir, tree_num, search_angle, seed_strength, tree_width, jump_length, seed_unit, grid_dirnum, delta, max_distance, grid_size, city)

	# @��������г��� END
	ENDTIME = time.time()
	print "END TIME: %s" % ENDTIME
	print "Total minutes: %f" % ((ENDTIME-STARTTIME)/60.0)


if __name__ == '__main__':
	logging.basicConfig(filename='logger-treemapflowcalMM.log', level=logging.DEBUG)
	main(sys.argv[1:])