#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Input Format:
# id, time, lat, lng, state, sid, admin
# 
# Output Format:
# [hares-x]
# id, seg, hour, wday, gid, state, admin, from_gid, to_gid, from_aid, to_aid
# 
# [tripFlow-x] 
# hour, id, time, lat, lng, from_lat, from_lng, from_time, to_lat, to_Lng, to_time
# 
# 现使用处理方式为只过滤 travel 的数据

import logging
import os
from util.preprocess import getCityLocs, formatGridID, formatTime
from util.preprocess import getAdminNumber
from util.tripFlow.base import getRealDistance


class FileSegByHour(object):
	"""
	多进程计算类：按照日期对文件进行分类重写存储，相关字段预先处理，需同时指定基础输入目录和输出目录
		:param object: 
	"""
	def __init__(self, PROP):
		super(FileSegByHour, self).__init__()

		self.INDEX = PROP['INDEX']
		self.CITY = PROP['CITY'] 
		self.INPUT_PATH = PROP['IDIRECTORY']
		self.OUTPUT_PATH = os.path.join(PROP['ODIRECTORY'], 'ts-byday-tf')
		self.INUM = PROP['INUM']
		self.ONUM = PROP['ONUM']
		self.MAXDAY = PROP['MAXDAY']
		self.MATRIX = [[] for x in xrange(0, PROP['MAXDAY'])]
		self.COUNT = [0 for x in xrange(0, PROP['MAXDAY'])]
		self.SAFECOUNT = PROP['SAFECOUNT']
		self.len = 0
		self.deltaDistance = 700

		self.currentDatasets = {
			'fromLatLng': [0, 0],
			'fromAdmin': '',
			'toLatLng': [0, 0],
			'toAdmin': '',
			'fromTime': '',
			'toTime': '',
			'data': [],
			'stateId': 0
		}
	
	def run(self):
		logging.info('TASK-%d running...' % (self.INDEX))

		for x in xrange(0, 10000):
			number = self.INDEX + 20 * x
			if number > self.INUM:
				break

			#part-03999-trajectory_15-800
			ifilename = 'P2-part-%05d-trajectory_30-800' % number
			logging.info('Job-%d File-%s Operating...' % (self.INDEX, ifilename))
			self.iterateFileOnlyTravelNew(os.path.join(self.INPUT_PATH, ifilename))
			#self.iterateFile(os.path.join(self.INPUT_PATH, ifilename))

		# 捡完所有漏掉的记录，遍历输入文件
		for x in xrange(0, self.MAXDAY):
			if self.COUNT[x] == 0:
				continue

			ofile = os.path.join(self.OUTPUT_PATH, "rawdata-j%d-%d" % (self.INDEX, x))
			with open(ofile, 'ab') as stream:
				stream.write('\n'.join(self.MATRIX[x]) + '\n')
			stream.close()

		logging.info('Total travel num-%d' %(self.len))
		logging.info('End Job-%d' % (self.INDEX))

	def iterateFile(self, ifile):
		# stay travel 都处理的情况
		with open(ifile, 'rb') as stream:
			for line in stream:
				line = line.strip('\n')
				linelist = line.split(',')

				state = linelist[4]
				
				if state == 'S' or state == 'T' or line == '':
					continue

				# 分析日期
				tmp = formatTime(linelist[1])
				ydayCurrent = tmp['yday'] - 187
				
				wday = tmp['wday']
				hour = tmp['hour']
				seg = ydayCurrent * 24 + hour
				
				if ydayCurrent < 0 or ydayCurrent >= self.MAXDAY:
					continue
				
				# id = linelist[0]
				# admin = getAdminNumber(linelist[6])
				# gid = formatGridID(getCityLocs(self.CITY), [linelist[3], linelist[2]])
				# newLinePreStr = "%s,%d,%d,%d,%d" % (id, seg, hour, wday, gid)
                #
				# # 分状态处理原始数据
				# # S 时 currentDatasets 数据重置（重置前查看是否需要转存上一段 T 的数据）
				# # T 时对比当前 from 是否为初始状态，若为初始状态当前数据存在 from，否则存在 to
				# if state == 'T':
				# 	if self.currentDatasets['fromLatLng'][0] == 0:
				# 		self.currentDatasets['fromLatLng'] = [linelist[3], linelist[2]]
				# 		self.currentDatasets['fromAdmin'] = linelist[6]
				# 		self.currentDatasets['stateId'] = linelist[5]
				# 	else:
				# 		# 判断 stateId 是否一致
				# 		if linelist[5] != self.currentDatasets['stateId']:
				# 			self.updLastTravelRecs()
				# 		else:
				# 			self.currentDatasets['toLatLng'] = [linelist[3], linelist[2]]
				# 			self.currentDatasets['toAdmin'] = linelist[6]
				# 	tmp = "%s,T,%d" % (newLinePreStr, admin)
				# 	self.currentDatasets['data'].append([tmp, ydayCurrent])
				# else:
				# 	self.updLastTravelRecs()
                #
				# 	newline = "%s,S,%d,0,0,0,0" % (newLinePreStr, admin)
				# 	self.COUNT[ydayCurrent] += 1
				# 	self.MATRIX[ydayCurrent].append(newline)
                #
				# 	self.checkWriteOpt(ydayCurrent)


				id = linelist[0]
				admin = getAdminNumber(linelist[6])
				gid = formatGridID(getCityLocs(self.CITY), [linelist[3], linelist[2]])
				newLinePreStr = "%d,%s,%s,%s,%s" % (hour, id, linelist[1], linelist[2], linelist[3])

				# T 时对比当前 from 是否为初始状态，若为初始状态当前数据存在 from，否则存在 to
				# if state == 'T':
				# 	if self.currentDatasets['fromLatLng'][0] == 0:
				# 		self.currentDatasets['fromLatLng'] = [linelist[3], linelist[2]]
				# 		self.currentDatasets['fromAdmin'] = linelist[6]
				# 		self.currentDatasets['fromTime'] = linelist[1]
				# 		self.currentDatasets['stateId'] = linelist[5]
				# 	else:
				# 		# 判断 stateId 是否一致
				# 		if linelist[5] != self.currentDatasets['stateId']:
				# 			self.updLastTravelRecsOnlyTravel()
				# 		else:
				# 			self.currentDatasets['toLatLng'] = [linelist[3], linelist[2]]
				# 			self.currentDatasets['toAdmin'] = linelist[6]
				# 			self.currentDatasets['toTime'] = linelist[1]
				# 	# tmp = "%s,T,%d" % (newLinePreStr, admin)
				# 	self.currentDatasets['data'].append([newLinePreStr, ydayCurrent])
				# else:
				# 	self.updLastTravelRecs()
                #
				# 	newline = "%s,S,%d,0,0,0,0" % (newLinePreStr, admin)
				# 	self.COUNT[ydayCurrent] += 1
				# 	self.MATRIX[ydayCurrent].append(newline)
                #
				# 	self.checkWriteOpt(ydayCurrent)
				newline = "%s,U,%d,0,0,0,0" % (newLinePreStr, admin)
				self.COUNT[ydayCurrent] += 1
				self.MATRIX[ydayCurrent].append(newline)

				self.checkWriteOpt(ydayCurrent)

		stream.close()

	def iterateFileOnlyTravel(self, ifile):
    	# travel 情况
		with open(ifile, 'rb') as stream:

			for line in stream:
				line = line.strip('\n')
				linelist = line.split(',')

				state = linelist[4]
				
				if state == '-1' or line == '' or state == '0':
					continue

				self.len += 1

				# 分析日期
				tmp = formatTime(linelist[1])
				ydayCurrent = tmp['yday'] - 187
				
				wday = tmp['wday']
				hour = tmp['hour']
				seg = ydayCurrent * 24 + hour
				
				if ydayCurrent < 0 or ydayCurrent >= self.MAXDAY:
					continue
				
				id = linelist[0]
				#admin = getAdminNumber(linelist[6])
				#gid = formatGridID(getCityLocs(self.CITY), [linelist[3], linelist[2]])
				newLinePreStr = "%d,%s,%s,%s,%s" % (hour, id, linelist[1], linelist[2], linelist[3])

				# T 时对比当前 from 是否为初始状态，若为初始状态当前数据存在 from，否则存在 to


				if self.currentDatasets['fromLatLng'][0] == 0:
					self.currentDatasets['fromLatLng'] = [linelist[3], linelist[2]]
					#self.currentDatasets['fromAdmin'] = linelist[6]
					self.currentDatasets['fromTime'] = linelist[1]
					self.currentDatasets['stateId'] = linelist[5]
				else:
					# 判断 stateId 是否一致
					if linelist[5] != self.currentDatasets['stateId']:
						self.updLastTravelRecsOnlyTravel()

					else:
						self.currentDatasets['toLatLng'] = [linelist[3], linelist[2]]
						#self.currentDatasets['toAdmin'] = linelist[6]
						self.currentDatasets['toTime'] = linelist[1]
				# tmp = "%s,T,%d" % (newLinePreStr, admin)
				self.currentDatasets['data'].append([newLinePreStr, ydayCurrent])


				
		stream.close()

	def iterateFileOnlyTravelNew(self, ifile):
    	# travel 情况
		recordsPassed = []
		with open(ifile, 'rb') as stream:

			for line in stream:
				line = line.strip('\n')
				linelist = line.split(',')

				recordsPassed.append(linelist)


		for index in range(0, len(recordsPassed)):

				linelist = recordsPassed[index]
				state = linelist[4]

				if state == '-1' or line == '' or state == '0':
					continue

				self.len += 1

				# 分析日期
				tmp = formatTime(linelist[1])
				ydayCurrent = tmp['yday'] - 187

				wday = tmp['wday']
				hour = tmp['hour']
				seg = ydayCurrent * 24 + hour

				if ydayCurrent < 0 or ydayCurrent >= self.MAXDAY:
					continue

				id = linelist[0]
				#admin = getAdminNumber(linelist[6])
				#gid = formatGridID(getCityLocs(self.CITY), [linelist[3], linelist[2]])
				newLinePreStr = "%d,%s,%s,%s,%s" % (hour, id, linelist[1], linelist[2], linelist[3])

				# T 时对比当前 from 是否为初始状态，若为初始状态当前数据存在 from，否则存在 to

				# 找到左边的方向
				record = recordsPassed[index-1]
				if record[0] == id and record[1] != linelist[1] and (int(linelist[1]) - int(record[1])) <= 3600:
					self.currentDatasets['fromLatLng'] = [str(record[3]), str(record[2])]
					self.currentDatasets['fromTime'] = record[1]

				# for i in range(index-1, -1, -1):
				# 	record = recordsPassed[i]
				# 	if record[0] != id:
				# 		break
				# 	if record[1] == linelist[1]:
				# 		continue
				# 	if getRealDistance(record[3], record[2], linelist[3], linelist[2]) > self.deltaDistance:
				# 		self.currentDatasets['fromLatLng'] = [str(record[3]), str(record[2])]
				# 		self.currentDatasets['fromTime'] = record[1]
				# 		break
				# 	else:
				# 		continue

				# if self.currentDatasets['fromLatLng'][0] == 0:
				# 	self.currentDatasets['fromLatLng'] = [str(recordsPassed[index-1][3]), str(record[2])]
				# 	self.currentDatasets['fromTime'] = record[1]



				#找到右边的方向
				record = recordsPassed[index + 1]
				if record[0] == id and record[1] != linelist[1] and (int(record[1]) - int(linelist[1])) <= 3600:
					self.currentDatasets['toLatLng'] = [str(record[3]), str(record[2])]
					self.currentDatasets['toTime'] = record[1]
				# for j in range(index + 1, len(recordsPassed)):
				# 	record = recordsPassed[j]
				# 	if record[0] != id:
				# 		break
				# 	if record[1] == linelist[1]:
				# 		continue
				# 	if getRealDistance(record[3], record[2], linelist[3], linelist[2]) > self.deltaDistance:
				# 		self.currentDatasets['toLatLng'] = [str(record[3]), str(record[2])]
				# 		self.currentDatasets['toTime'] = record[1]
				# 		break
				# 	else:
				# 		continue

				self.currentDatasets['data'].append([newLinePreStr, ydayCurrent])
				self.updLastTravelRecsOnlyTravel()

		stream.close()

	def checkWriteOpt(self, ydayCurrent):
		# 计数存储，看情况写入文件
		if self.COUNT[ydayCurrent] >= self.SAFECOUNT:
			ofile = os.path.join(self.OUTPUT_PATH, "rawdata-j%d-%d" % (self.INDEX, ydayCurrent))
			with open(ofile, 'ab') as stream:
				stream.write('\n'.join(self.MATRIX[ydayCurrent]) + '\n')
			stream.close()

			self.COUNT[ydayCurrent] = 0
			self.MATRIX[ydayCurrent] = []

	def updLastTravelRecs(self):
		if self.currentDatasets['fromAdmin'] == '':
			return 0
		# 		
		fromGid = formatGridID(getCityLocs(self.CITY), self.currentDatasets['fromLatLng'])
		toGid = formatGridID(getCityLocs(self.CITY), self.currentDatasets['toLatLng'])
		fromAdmin = getAdminNumber(self.currentDatasets['fromAdmin'])
		toAdmin = getAdminNumber(self.currentDatasets['toAdmin'])
		supStr = "%d,%d,%d,%d" % (fromGid, toGid, fromAdmin, toAdmin)

		# 遍历记录
		for each in self.currentDatasets['data']:
			ydayCurrent = each[1]
			newline = "%s,%s" % (each[0], supStr)

			self.COUNT[ydayCurrent] += 1
			self.MATRIX[ydayCurrent].append(newline)
			self.checkWriteOpt(ydayCurrent)

		# 重置
		self.currentDatasets['fromLatLng'] = [0, 0]
		self.currentDatasets['fromAdmin'] = ''
		self.currentDatasets['data'] = []

	def updLastTravelRecsOnlyTravel(self):
		if self.currentDatasets['toLatLng'][0] == 0 or self.currentDatasets['fromLatLng'][0] == 0:
			return 0
		#print(self.currentDatasets['data'])
		#self.len += len(self.currentDatasets['data'])

		fromLatLng = ','.join(self.currentDatasets['fromLatLng'])
		toLatLng = ','.join(self.currentDatasets['toLatLng'])
		supStr = "%s,%s,%s,%s" % (fromLatLng, self.currentDatasets['fromTime'], toLatLng, self.currentDatasets['toTime'])

		# 遍历记录
		for each in self.currentDatasets['data']:
			ydayCurrent = each[1]
			newline = "%s,%s" % (each[0], supStr)

			self.COUNT[ydayCurrent] += 1
			self.MATRIX[ydayCurrent].append(newline)
			self.checkWriteOpt(ydayCurrent)

		# 重置
		self.currentDatasets['fromLatLng'] = [0, 0]
		self.currentDatasets['toLatLng'] = [0, 0]
		self.currentDatasets['fromAdmin'] = ''
		self.currentDatasets['fromTime'] = ''
		self.currentDatasets['data'] = []