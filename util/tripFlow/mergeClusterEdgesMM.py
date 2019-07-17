#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Input Data Format
# [clusterID, lng, lat, gid, gLng, gLat, from/to, speed, direction]
# 
# Output Data Format
# [gLng, gLat, gdirStr, speed, recordNum, dLng, dLat, seg]

import os
import math


class MergeClusterEdgesMM(object):
	def __init__(self, PROP):
		super(MergeClusterEdgesMM, self).__init__()
		self.city = PROP['city']
		self.INPUT_PATH = os.path.join(PROP['IDIRECTORY'], self.city.lower()+'-byhour-res')
		self.OUTPUT_PATH = os.path.join(PROP['ODIRECTORY'], self.city.lower()+'-byhour-res')
		self.index = PROP['index']
		self.suffix = PROP['suffix']
		self.dataType = PROP['dataType']
		self.res = []

	def run(self):
		ifile = os.path.join(self.OUTPUT_PATH, 'tfres-%s-%d-%s' % (self.dataType, self.index, self.suffix))
		#totalNum = self.iterateFile(ifile)
		totalNum = self.iterateFileWithoutFromTo(ifile)
		if len(self.res) != 0:
			# print "One edge is consisted of %d records averagely." % (totalNum/len(self.res))
			print '''
===	Edge Merging Info	===
Edges in total:	%d
Records used in clusters: %d
One edge is consisted of %d records averagely
===	Edge Merging Info	===
''' % (len(self.res), totalNum, totalNum/len(self.res))

		self.outputToFile()
		
	def iterateFileWithoutFromTo(self, ifile):
		count = 0
		with open(ifile, 'rb') as f:
			firstLine = True
			currentPeriod = {}

			for line in f:
				line = line.strip('\n')
				linelist = line.split(',')

				if linelist[0] == '-1':
					continue
				count += 1

				cid = int(linelist[0])
				lng = float(linelist[1])
				lat = float(linelist[2])
				gid = int(linelist[3])
				gLng = float(linelist[4])
				gLat = float(linelist[5])

				# gdirStr: from/to
				[gdirStr, speed, direction, angle] = linelist[6:10]

				id = str(gid)
				subid = str(cid)
				onerec = [cid, lng, lat, gid, gLng, gLat, gdirStr, speed, angle]

				# 第一行数据读入
				if firstLine:
					firstLine = False
					currentPeriod = {
						'id': id,
						'gidInfo': [gid, gLng, gLat],
						'count': 1,  # 没用上
						'data': {}
					}
					currentPeriod['data'][subid] = [onerec]
					continue

				# begin
				if id != currentPeriod['id']:
					# 计算存储边信息
					self.updateMergedRes(currentPeriod)

					# 清空 state 重置
					currentPeriod = {
						'id': id,
						'gidInfo': [gid, gLng, gLat],
						'count': 1,
						'data': {}
					}
					currentPeriod['data'][subid] = [onerec]
				else:
					currentPeriod['count'] += 1
					if subid in currentPeriod['data'].keys():
						currentPeriod['data'][subid].append(onerec)
					else:
						currentPeriod['data'][subid] = [onerec]
				# end
		f.close()

		return count

	def updateMergedRes(self, data):
		# 更新 self.res 函数

		[gid, gLng, gLat] = data['gidInfo']
		for key, val in data['data'].iteritems():
			recordNum = len(val)
			speed = 0.0

			lng = float(val[0][1])
			lat = float(val[0][2])
			angle = float(val[0][8])

			for x in xrange(0, recordNum):
				speed += float(val[x][7])

			speed /= recordNum
			
			onerec = "%.6f,%.6f,%s,%f,%d,%.6f,%.6f,%d,%.1f" % (gLng, gLat, 'all', speed, recordNum, lng, lat, self.index, angle)
			self.res.append(onerec)

	def outputToFile(self):
		"""
		通用输出文件函数
			:param self: 
			:param res: 
		"""

		ofilename = 'mcres-%s-%d-%s' % (self.dataType, self.index, self.suffix)
		ofile = os.path.join(self.OUTPUT_PATH, ofilename)
		with open(ofile, 'wb') as f:
			f.write('\n'.join(self.res))
		f.close()

		return ofilename
		