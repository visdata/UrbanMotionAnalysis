#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Input Data Format
# [pointLng, pointLat, pointGid, speed, direction, angle]
# 
# Output Data Format
# Road network edges on the map: [start-pointLng, start-pointLat, end-pointLng, end-pointLat, road-edge-angle]

import os
import json
from math import sqrt, pow, acos, pi
import math

def processTask(stdoutdir, locs, city, gridSize, LngSPLIT, LatSPLIT):

	self.roadNetworkEdges = {}

	LNGNUM = int( (locs['east'] - locs['west']) / LngSPLIT + 1 )
	LATNUM = int( (locs['north'] - locs['south']) / LatSPLIT + 1 )

	for gid = xrange(0, LNGNUM*LATNUM):

		self.roadNetworkEdges[gid] = []

		latind = int(gid / LNGNUM)
		lngind = gid - latind * LNGNUM
		
		lat = (locs['south'] + latind * LatSPLIT)
		lng = (locs['west'] + lngind * LngSPLIT)
		
		lngcen = (lng + LngSPLIT/2.0)
		latcen = (lat + LatSPLIT/2.0)

		# emulated road edge from west to east
		roadNetworkEdgeVecStr = "%f,%f,%f,%f,%.1f" % (lngcen - LngSPLIT/2.0, latcen, lngcen + LngSPLIT/2.0, latcen, 0)
		self.roadNetworkEdges[gid].append(roadNetworkEdgeVecStr)

		# emulated road edge from east to west
		roadNetworkEdgeVecStr = "%f,%f,%f,%f,%.1f" % (lngcen + LngSPLIT/2.0, latcen, lngcen - LngSPLIT/2.0, latcen, 180)
		self.roadNetworkEdges[gid].append(roadNetworkEdgeVecStr)
		
		# emulated road edge from south to north
		roadNetworkEdgeVecStr = "%f,%f,%f,%f,%.1f" % (lngcen, latcen - LatSPLIT/2.0, lngcen, latcen + LatSPLIT/2.0, 90)
		self.roadNetworkEdges[gid].append(roadNetworkEdgeVecStr)

		# emulated road edge from north to south
		roadNetworkEdgeVecStr = "%f,%f,%f,%f,%.1f" % (lngcen, latcen + LatSPLIT/2.0, lngcen, latcen - LatSPLIT/2.0, 270)
		self.roadNetworkEdges[gid].append(roadNetworkEdgeVecStr)

	# JSON
	ofile = os.path.join(stdoutdir, 'road-network-edges-%s-%d.json' % (city, gridSize))
	with open(ofile, 'wb') as f:
		json.dump(self.roadNetworkEdges, f)
	f.close()

	return {
		'roadNetworkEdges': self.roadNetworkEdges
	}


	

def usage():
	print "(by default parameters set explicitly in the code) python testRoadNetworkEdges.py -p /dir-of-map -c 'BJ'"


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
		argsArray = ["help", 'stdoutdir=', 'city=']
		opts, args = getopt.getopt(argv, "hp:c:", argsArray)
	except getopt.GetoptError as err:
		print str(err)
		usage()
		sys.exit(2)

	stdoutdir = '/datahouse/tripflow/2019-30-800-'+city

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
			sys.exit()
		elif opt in ("-e", "--city"):
			city = str(arg)
			stdoutdir = '/datahouse/tripflow/2019-30-800-'+city
		elif opt in ('-p', '--stdoutdir'):
			stdoutdir = arg
		

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

	processTask(stdoutdir, cityLatLngDict[city], city, gridSize, LngSPLIT, LatSPLIT)

	# @多进程运行程�?END
	ENDTIME = time.time()
	print "END TIME: %s" % ENDTIME
	print "Total minutes: %f" % ((ENDTIME-STARTTIME)/60.0)


if __name__ == '__main__':
	logging.basicConfig(filename='logger-testroadnetworkedges.log', level=logging.DEBUG)
	main(sys.argv[1:])