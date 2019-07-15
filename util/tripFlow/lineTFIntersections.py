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

class LineTFIntersections(object):
	def __init__(self, PROP):
		super(LineTFIntersections, self).__init__()
		self.city = PROP['city']
		# self.INPUT_PATH = os.path.join(PROP['IDIRECTORY'], 'bj-byhour-tf')
		self.OUTPUT_PATH = os.path.join(PROP['ODIRECTORY'], self.city.lower()+'-byhour-res')
		self.index = PROP['index']
		self.suffix = PROP['suffix']
		self.dataType = 'angle'
		self.resByAng = PROP['resByAng']

		self.typeNum = 1  # 暂时为1
		self.dbLabel = [[] for x in xrange(0, self.typeNum)]
		self.dbInput = [[] for x in xrange(0, self.typeNum)]
		self.subInfo = [[] for x in xrange(0, self.typeNum)]

		self.eps = PROP['eps']
		self.min_samples = PROP['min_samples']
		self.dbscanBaseNum = 0
		self.locs = PROP['locs']
		self.LngSPLIT = PROP['LngSPLIT']
		self.LatSPLIT = PROP['LatSPLIT']
	
	def run(self):
		#noiseRate = self.iterateRes()
		noiseRate = self.iterateResWithoutFromTo()
		ofilename = self.outputToFile()

		return noiseRate, ofilename 

	def iterateRes(self):
		cateKeys = {0: 'from', 1: 'to'}
		
		for x in xrange(0, self.typeNum):
			accumulator = 0
			totalNum, noiseNum = 0, 0
			for gid, tripsArray in self.resByAng[cateKeys[x]].iteritems():
				tripsLen = len(tripsArray)
				totalNum += tripsLen
				tmpLngLat, tmpAngle, tmpSubInfo = [], [], []
				for index in xrange(0, tripsLen):
					linelist = tripsArray[index].split(',')

					# lng = float(linelist[0])
					# lat = float(linelist[1])
					gid = int(linelist[2])
					gdirStr = linelist[3]
					speed = linelist[4]
					direction = linelist[5]
					angle = int(float(linelist[6]))
					gidInfo = parseFormatGID(gid, 'e', self.LngSPLIT, self.LatSPLIT, self.locs)
					gLat = gidInfo['lat']
					gLng = gidInfo['lng']
					strength = float(linelist[7])
					
					tmpLngLat.append(linelist[0] + ',' + linelist[1])
					tmpAngle.append([angle, strength])
					subprops = "%s,%s,%s" % (gdirStr, speed, direction)
					tmpSubInfo.append("%d,%.6f,%.6f,%s" % (gid, gLng, gLat, subprops))

				# DBScan result
				dbres = self.lineCLusterCalculation(tmpAngle)

				if not dbres:
					continue

				noiseNum += dbres['noiseNum']
				self.dbLabel[x] += dbres['labels']

				self.dbInput[x] += tmpLngLat
				self.subInfo[x] += tmpSubInfo

				accumulator += 1
			
			noiseRate = float(noiseNum) / totalNum
			print '''
===	Angle Cluster Info	===
Number of dbscan clusters in all:	%d
Grid ID number: %d
Records(total):	%d
Noise Rate:	%f
===	Angle Cluster Info	===
''' % (self.dbscanBaseNum, accumulator, totalNum, noiseRate)

		return noiseRate


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

		accumulator = 0
		totalNum, noiseNum = 0, 0
		for gid, tripsArray in self.resByAng['all'].iteritems():
			tripsLen = len(tripsArray)
			totalNum += tripsLen
			tmpLngLat, tmpAngle, tmpSubInfo = [], [], []
			for index in xrange(0, tripsLen):
				linelist = tripsArray[index].split(',')

				# lng = float(linelist[0])
				# lat = float(linelist[1])
				gid = int(linelist[2])
				gdirStr = linelist[3]
				speed = linelist[4]
				direction = linelist[5]
				angle = int(float(linelist[6]))
				gidInfo = parseFormatGID(gid, 'e', self.LngSPLIT, self.LatSPLIT, self.locs)
				gLat = gidInfo['lat']
				gLng = gidInfo['lng']
				strength = float(linelist[7])

				tmpLngLat.append(linelist[0] + ',' + linelist[1])
				tmpAngle.append([angle, strength])
				subprops = "%s,%s,%s,%d" % (gdirStr, speed, direction, angle)
				tmpSubInfo.append("%d,%.6f,%.6f,%s" % (gid, gLng, gLat, subprops))

			# DBScan result
			dbres = self.lineCLusterCalculation(tmpAngle)

			if not dbres:
				continue

			noiseNum += dbres['noiseNum']
			self.dbLabel[0] += dbres['labels']

			self.dbInput[0] += tmpLngLat
			self.subInfo[0] += tmpSubInfo

			accumulator += 1

		noiseRate = float(noiseNum) / totalNum
		print '''
===	Angle Cluster Info	===
Number of dbscan clusters in all:	%d
Grid ID number: %d
Records(total):	%d
Noise Rate:	%f
===	Angle Cluster Info	===
''' % (self.dbscanBaseNum, accumulator, totalNum, noiseRate)

		return noiseRate
		
	def lineCLusterCalculation(self, angleArray):
		angleList = [0 for x in xrange(0, 720)]
		#print(angleArray)
		# visitedList = [0 for x in xrange(0, 720)]
		labelList = {}
		res = []
		arrayLen = len(angleArray)
		totalStrength = 0
		# print "DEBUG: arrayLen"
		# print arrayLen

		N = self.min_samples
		#print("min samples: %d" % (N))
		# print "Current rho: %f" % (rho)

		for x in xrange(0, arrayLen):
			[angle, weight] = angleArray[x]
			
			angleList[angle] += weight
			angleList[angle + 360] += weight

			totalStrength += weight

		rho = totalStrength * self.eps / 360  # 每度至少拥有的 trip 数量
		#print("trip number in each angle is: " + str(rho))
		
		initLinkList = []
		for x in xrange(0, 720):
			if angleList[x] != 0:
				initLinkList.append({
					'index': x,
					'data': angleList[x]
				})
		
		# print initLinkList
		if len(initLinkList) == 0:
			return False

		ALL = LinkList()
		ALL.initlist(initLinkList)
		listLen = ALL.getlength()
		sIndex = 0
		while(ALL.getitem(sIndex)['index'] < 180):
			sIndex += 1
		# eIndex = sIndex+1
		# while(ALL.getitem(eIndex)['index'] < 540):
		# 	eIndex += 1
		# eIndex -= 1

		cIndex = sIndex
		clusteID = 0
		# print "Start from %d" % cIndex
		while(cIndex < listLen):
			base = ALL.getitem(cIndex)
			tfNum, lIndex, rIndex = base['data'], cIndex, cIndex
			lAngle, rAngle = base['index'], base['index']

			if rAngle >= 540:
				break

			# 左右循环直至没有新元素加入则停止，并做好标记和删除工作
			cRho = tfNum / (rAngle - lAngle + 1)
			endFlag = True
			# 密度符合条件的情况下则一直向两边遍历
			while (cRho >= rho):
				tmplIndex, tmprIndex = lIndex, rIndex
				tmplAngle, tmprAngle = lAngle, rAngle
				tmptfNum = tfNum
				tRho = cRho
				while tmplIndex > 0:
					tmpItem = ALL.getitem(tmplIndex-1)
					tmpNum = tmpItem['data']
					tRho = (tmpNum + tmptfNum) / (rAngle - tmpItem['index'] + 1)
					if tRho >= rho:
						tmplIndex -= 1
						tmplAngle = tmpItem['index']
						cRho = tRho
						tmptfNum += tmpNum
						endFlag = False
					else:
						break
				
				while tmprIndex < (listLen-1):
					tmpItem = ALL.getitem(tmprIndex+1)
					tmpNum = tmpItem['data']
					tRho = (tmpNum + tmptfNum) / (tmpItem['index'] - lAngle + 1)
					if tRho >= rho:
						tmprIndex += 1
						tmprAngle = tmpItem['index']
						cRho = tRho
						tmptfNum += tmpNum
						endFlag = False
					else:
						break
					
				if endFlag:
					# 没有新增
					break
				else:
					lIndex, rIndex = tmplIndex, tmprIndex
					lAngle, rAngle = tmplAngle, tmprAngle
					tfNum = tmptfNum
					endFlag = True
				# print "rho iteration"
			
			# 满足 cluster 条件，否则放弃
			# print "tfNum: %d" % tfNum

			if tfNum >= N:
				# print "Current tfNum is %d, lIndex is %d, rIndex is %d, clusterID is %d" % (tfNum, lIndex, rIndex, clusteID)
				for x in xrange(rIndex, lIndex-1, -1):
					angle = ALL.getitem(x)['index'] % 360
					angle = str(angle)
					if angle not in labelList.keys():
						labelList[angle] = clusteID + self.dbscanBaseNum
					ALL.delete(x)
				
				lAngle %= 360
				rAngle %= 360
				i = lIndex
				x = lIndex
				while(x < ALL.getlength()):
					tmpItem = ALL.getitem(x)
					tmpAngle = tmpItem['index'] % 360
					notCross = tmpAngle >= lAngle and tmpAngle <= rAngle
					comeCross = rAngle < lAngle and (tmpAngle >= lAngle or tmpAngle <= rAngle)
					if notCross or comeCross:
						ALL.delete(x)
					else:
						x += 1
					
					# print "left to the last iteration"
				
				cIndex = lIndex
				x = 0
				while(x < lIndex):
					tmpItem = ALL.getitem(x)
					tmpAngle = tmpItem['index'] % 360
					notCross = tmpAngle >= lAngle and tmpAngle <= rAngle
					comeCross = rAngle < lAngle and (tmpAngle >= lAngle or tmpAngle <= rAngle)
					if notCross or comeCross:
						ALL.delete(x)
						cIndex -= 1
						lIndex -= 1
					else:
						x += 1
					
					# print "0 to left iteration"
				
				# 只有聚类成功才增加 clusteID
				clusteID += 1
			else:
				cIndex += 1

			# 扫尾工作
			listLen = ALL.getlength()

		# 返回结果计算
		noiseNum = 0
		for x in xrange(0, arrayLen):
			angle = str(angleArray[x][0])
			if angle in labelList.keys():
				res.append(labelList[angle])
			else:
				noiseNum += 1
				res.append(-1)
		
		# 更新 cluster ID 基数
		self.dbscanBaseNum += clusteID

		#print(labelList)
		return {
			'labels': res, 
			'noiseNum': noiseNum
		}

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
		