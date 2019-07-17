#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Input Data Format
# [lng, lat, gid, from/to, speed, direction, angle, strength]
# 
# Output data format
# 分方向分 Grid 聚集的结果
# [clusterID, lng, lat, gid, gLng, gLat, from/to, speed, direction]

import os
from util.tripFlow.base import parseFormatGID
from util.tripFlow.LinkList import LinkList

class LineTFAggregationsMM(object):
	def __init__(self, PROP):
		super(LineTFAggregationsMM, self).__init__()
		self.city = PROP['city']
		# self.INPUT_PATH = os.path.join(PROP['IDIRECTORY'], 'bj-byhour-tf')
		self.OUTPUT_PATH = os.path.join(PROP['ODIRECTORY'], self.city.lower()+'-byhour-res-mapped')
		self.index = PROP['index']
		self.suffix = PROP['suffix']
		self.dataType = 'angle'
		self.resByAng = PROP['resByAng']

		self.typeNum = 1  # 暂时为1
		self.dbLabel = [[] for x in xrange(0, self.typeNum)]
		self.dbInput = [[] for x in xrange(0, self.typeNum)]
		self.subInfo = [[] for x in xrange(0, self.typeNum)]

		self.min_samples = PROP['min_samples']
		self.locs = PROP['locs']
		self.LngSPLIT = PROP['LngSPLIT']
		self.LatSPLIT = PROP['LatSPLIT']
	
	def run(self):
		noiseRate = self.iterateResWithoutFromTo()
		ofilename = self.outputToFile()

		return noiseRate, ofilename 

	def iterateResWithoutFromTo(self):

		cateKeys = {0: 'from', 1: 'to'}

		self.resByAng['all'] = {}

		# merge from and to
		for gid, tripsArray in self.resByAng['from'].iteritems():
			self.resByAng['all'][gid] = tripsArray

		for gid, tripsArray in self.resByAng['to'].iteritems():
			if self.resByAng['all'].has_key(gid):
				self.resByAng['all'][gid].extend(tripsArray)
			else:
				self.resByAng['all'][gid] = tripsArray

		accumulator, clusterNum = 0, 0
		totalNum, noiseNum = 0, 0
		for gid, tripsArray in self.resByAng['all'].iteritems():
			tripsLen = len(tripsArray)
			totalNum += tripsLen
			tmpLngLat, tmpSubInfo, tmpLngLatAngle, labels = [], [], [], []
			mapLngLatAngle = {}

			for index in xrange(0, tripsLen):
				linelist = tripsArray[index].split(',')

				startLng = float(linelist[0])
				startLat = float(linelist[1])
				gid = int(linelist[2])
				gdirStr = linelist[3]
				speed = linelist[4]
				direction = linelist[5]
				angle = float(linelist[6])
				gidInfo = parseFormatGID(gid, 'e', self.LngSPLIT, self.LatSPLIT, self.locs)
				gLat = gidInfo['lat']
				gLng = gidInfo['lng']

				tmpLngLat.append("%.6f,%.6f" % (startLng, startLat))
				subprops = "%s,%s,%s,%d" % (gdirStr, speed, direction, angle)
				tmpSubInfo.append("%d,%.6f,%.6f,%s" % (gid, gLng, gLat, subprops))

				clusterKey = "%.6f,%.6f,%.1f" % (startLng, startLat, angle)
				tmpLngLatAngle.append(clusterKey)
				
				if clusterKey in mapLngLatAngle.keys():
					mapLngLatAngle[clusterKey] = mapLngLatAngle[clusterKey] + 1
				else:
					mapLngLatAngle[clusterKey] = 1

			# Aggregation by tmpLngLatAngle

			clusterIndex = 0
			clusterMap = {}

			for clusterKey in mapLngLatAngle.keys():
				if mapLngLatAngle[clusterKey] >= self.min_samples:
					clusterMap[clusterKey] = clusterIndex
					clusterIndex = clusterIndex + 1
					clusterNum = clusterNum + 1
				else:
					clusterMap[clusterKey] = -1
					noiseNum += mapLngLatAngle[clusterKey]

			for index in xrange(0, tripsLen):
				labels.append(clusterMap[tmpLngLatAngle[index]])

			self.dbLabel[0] += labels
			self.dbInput[0] += tmpLngLat
			self.subInfo[0] += tmpSubInfo

			accumulator += 1

		noiseRate = float(noiseNum) / totalNum
		print '''
===	Angle Cluster Info	===
Number of clusters in total: %d
Grid ID number: %d
Records(total):	%d
Noise Rate:	%f
===	Angle Cluster Info	===
''' % (clusterNum, accumulator, totalNum, noiseRate)

		return noiseRate
		
	def outputToFile(self):
		ores = []
		i = 0
		for i in xrange(0, self.typeNum):
			for j in xrange(0, len(self.dbLabel[i])):
				label = self.dbLabel[i][j]
				lngLatStr = self.dbInput[i][j]
				subInfoStr = self.subInfo[i][j]
				onerecStr = "%s,%s,%s" % (label, lngLatStr, subInfoStr)
				ores.append(onerecStr)

		ofilename = 'tfres-%s-%d-%s' % (self.dataType, self.index, self.suffix)
		ofile = os.path.join(self.OUTPUT_PATH, ofilename)
		with open(ofile, 'wb') as f:
			f.write('\n'.join(ores))
		f.close()

		return ofilename
		