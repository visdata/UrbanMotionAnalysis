#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 

import os
import numpy as np
from sklearn.cluster import DBSCAN


class DBScanPOI(object):
	def __init__(self, PROP):
		super(DBScanPOI, self).__init__()
		
		self.INPUT_DIRECTORY = PROP['IDIRECTORY']
		self.OUTPUT_PATH = os.path.join(PROP['ODIRECTORY'], 'clusterPOI')
		self.PIDLngLatList = {}
		self.msNum = PROP['clusterNum']
		self.msFile = PROP['msFile']
		self.msOptSuffix = PROP['msOptSuffix']
		self.dbscanBaseNum = 0
		self.PIDList = [[] for x in xrange(0, PROP['clusterNum'])]  # 用于识别 PID 以及结果聚合
		self.PClusterVec = [[] for x in xrange(0, PROP['clusterNum'])]  # 用于聚类
		self.PClusterRes = []  

	def run(self, eps, min_samples):
		ipoifile = os.path.join(self.INPUT_DIRECTORY, 'baseData', 'mongoUTF8.csv')
		imsfile = os.path.join(self.INPUT_DIRECTORY, 'clusterPOI', self.msFile)
		self.constructPOILngLatList(ipoifile)
		self.constructPOIMatrix(imsfile)
		self.dbscanProcess(eps, min_samples)
		self.outputToFile("_eps_%f_sam_%d" % (eps, min_samples))
	
	def constructPOILngLatList(self, file):
		with open(file, 'rb') as f:
			for line in f:
				line = line.strip('\n')
				linelist = line.split(',')

				pid = linelist[0]
				lng = float(linelist[5])
				lat = float(linelist[6])
				self.PIDLngLatList[pid] = [lng, lat]
		f.close()

	def constructPOIMatrix(self, file):
		with open(file, 'rb') as f:
			for line in f:
				line = line.strip('\n')
				linelist = line.split(',')

				pid = linelist[0]
				cid = int(linelist[1])

				self.PIDList[cid].append(line)
				# print cid, pid
				self.PClusterVec[cid].append(self.PIDLngLatList[pid])
		f.close()
	
	def dbscanProcess(self, eps, min_samples):
		# ######################
		# Compute DBSCAN
		for x in xrange(0, self.msNum):
			X = self.PClusterVec[x]
			db = DBSCAN(eps=eps, min_samples=min_samples).fit(X)
			core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
			core_samples_mask[db.core_sample_indices_] = True
			labels = db.labels_

			A = np.array(self.PIDList[x])[:, np.newaxis]
			index = 0
			while index < len(labels):
				if labels[index] != -1:
					labels[index] += self.dbscanBaseNum
				index += 1
			C = np.array(labels)[:, np.newaxis]
			res = np.hstack((A, C))
			res = ["%s,%s" % (e[0], e[1]) for e in res]
			self.PClusterRes += res

			# print "PIDList [0]: %s, res [0]: %s" % (self.PIDList[x][0], res[0])

			# Number of clusters in labels, ignoring noise if present.
			n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
			self.dbscanBaseNum += n_clusters_

			print "MS No.%d, DS Cluster number: %d" % (x, n_clusters_)
		
		print "number of dbscan clusters in all: %d" % (self.dbscanBaseNum)
	
	def outputToFile(self, dsOptSuffix):
		"""
		通用输出文件函数
			:param self: 
			:param res: 
		"""
		res = self.PClusterRes
		ostream = '\n'.join(res)

		fileName = 'dbscanResult%s%s' % (self.msOptSuffix, dsOptSuffix)
		ofile = os.path.join(self.OUTPUT_PATH, fileName)
		with open(ofile, 'wb') as f:
			f.write(ostream)
		f.close()
