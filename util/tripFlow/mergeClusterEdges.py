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


class MergeClusterEdges(object):
	def __init__(self, PROP):
		super(MergeClusterEdges, self).__init__()
		self.city = PROP['city']
		self.INPUT_PATH = os.path.join(PROP['IDIRECTORY'], self.city.lower()+'-byhour-res')
		self.OUTPUT_PATH = os.path.join(PROP['ODIRECTORY'], self.city.lower()+'-byhour-res')
		self.index = PROP['index']
		self.suffix = PROP['suffix']
		self.dataType = PROP['dataType']
		self.res = []

	def run(self):
		ifile = os.path.join(self.INPUT_PATH, 'tfres-%s-%d-%s' % (self.dataType, self.index, self.suffix))
		#totalNum = self.iterateFile(ifile)
		totalNum = self.iterateFileWithoutFromTo(ifile)
		if len(self.res) != 0:
			# print "One edge is consisted of %d records averagely." % (totalNum/len(self.res))
			print '''
===	Edge Merging Info	===
Edges in total:	%d
Records used in clusters:	%d
One edge is consisted of %d records averagely
===	Edge Merging Info	===
''' % (len(self.res), totalNum, totalNum/len(self.res))

		self.outputToFile()
		
	def iterateFile(self, ifile):
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
				gLat = float(linelist[5])
				gLng = float(linelist[4])

				# gdirStr: from/to
				[gdirStr, speed, direction] = linelist[6:9]

				id = "%d-%s" % (gid, direction) if self.dataType == 'direction' else str(gid)
				subid = "%d-%s" % (cid, gdirStr)
				onerec = [cid, lng, lat, gid, gLng, gLat, gdirStr, speed]
				
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
				[gdirStr, speed, direction] = linelist[6:9]

				id = "%d-%s" % (gid, direction) if self.dataType == 'direction' else str(gid)
				subid = "%d" % (cid)
				onerec = [cid, lng, lat, gid, gLng, gLat, gdirStr, speed]

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
			gdirStr = val[0][6]
			speed = 0.0
			dLng, dLat = 0.0, 0.0

			for x in xrange(0, recordNum):
				gdirStr = val[x][6]
				speed += float(val[x][7])

				tLng = val[x][1] - val[x][4]
				tLat = val[x][2] - val[x][5]
				diff = {
					'from': [tLng, tLat],
					'to': [tLng, tLat]
				}
				dLng += diff[gdirStr][0]
				dLat += diff[gdirStr][1]

			dDis = math.sqrt(math.pow(dLat, 2) + math.pow(dLng, 2))
			if dDis == 0:
				print(data)
			dLng /= dDis
			dLat /= dDis
			speed /= recordNum
			
			onerec = "%.6f,%.6f,%s,%f,%d,%f,%f,%d" % (gLng, gLat, gdirStr, speed, recordNum, dLng, dLat, self.index)
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
		