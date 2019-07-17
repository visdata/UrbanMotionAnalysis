#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Input Data Format
# [pointLng, pointLat, pointGid, speed, direction, angle]
# 
# Output Data Format
# map-matched vectors: [matched-pointLng, matched-pointLat, matched-pointGid, org-speed, matched-direction, matched-angle]

import os
import json
from math import sqrt, pow, acos, pi
from util.tripFlow.base import getFormatGID
from util.tripFlow.base import getGIDsByOffsets
from util.tripFlow.base import getRealDistance
from util.tripFlow.base import getGridIntersection
import math


class MapMatchingGridEdges(object):
	def __init__(self, PROP):
		super(MapMatchingGridEdges, self).__init__()
		self.resByCate = PROP['resByCate'];
		self.roadEdgesData = PROP['roadEdgesData'];
		self.LngSPLIT = PROP['LngSPLIT']
		self.LatSPLIT = PROP['LatSPLIT']
		self.locs = PROP['locs']

		self.gridSearchRange = 2
		self.angleMatchingRatio = 1
		self.distMatchingRatio = 1

		self.distZeroMatching = 100

	def run(self):
		# map matching 

		self.resByCateMapped = {}

		matchedGidNum = 0

		STARTTIME = time.time()

		for dir_key in self.resByCate.keys():

			print "Matching %d grids in %s direction:" % (len(self.resByCate[dir_key].keys()), dir_key)

			for id_key in self.resByCate[dir_key].keys():
				for vecStr in self.resByCate[dir_key][id_key]:
					linelist = vecStr.split(',')
					curPoint = [float(linelist[0]), float(linelist[1])]
					curGrid = getFormatGID(curPoint, self.LngSPLIT, self.LatSPLIT, self.locs)['gid']
					dirStr = str(linelist[3])
					speed = float(linelist[4]) 
					direction = str(linelist[5]) 
					curAngle = float(linelist[6]) 
					strength = float(linelist[7])

					matchedEdge = self.mapMatchingEdge(curPoint, curGrid, curAngle, self.roadEdgesData, self.gridSearchRange)

					if matchedEdge != None:

						matchedVecStr = "%.6f,%.6f,%d,%s,%f,%s,%.1f,%f" % (matchedEdge['gstart-point'][0], matchedEdge['gstart-point'][1], matchedEdge['gid'], dirStr, speed, direction, matchedEdge['angle'], strength)

						if matchedEdge['gid'] in self.resByCateMapped[dir_key].keys():
							self.resByCateMapped[dir_key][matchedEdge['gid']].append(matchedVecStr)
						else:
							self.resByCateMapped[dir_key][matchedEdge['gid']] = [matchedVecStr]

				matchedGidNum += 1
				if matchedGidNum % 10 == 0:
					ENDTIME = time.time()
					print "Match %d grids in %f seconds..." % (matchedGidNum, ENDTIME-STARTTIME)

		return self.resByCateMapped

	def mapMatchingEdge(self, point, gid, angle, roadEdgesData, gridSearchRange):

		candidateEdges = self.findCandidateEdges(gid, roadEdgesData, gridSearchRange)

		if len(candidateEdges) == 0:
			return None

		selectedEdgeWeight = 0
		selectedEdgeAngle = None
		selectedEdgeStartPoint = None

		for index in xrange(len(candidateEdges)):

			linelist = candidateEdges[index].split(',')

			roadStartPoint = [float(linelist[0]), float(linelist[1])]
			roadEndPoint = [float(linelist[2]), float(linelist[3])]
			roadAngle = float(linelist[4])

			curWeight = self.computeEdgeMatchingWeight(point, angle, roadStartPoint, roadEndPoint, roadAngle)
			if curWeight > selectedEdgeWeight:
				selectedEdgeWeight = curWeight
				selectedEdgeAngle = roadAngle
				selectedEdgeStartPoint = roadStartPoint
				selectedEdgeEndPoint = roadEndPoint

		matchedPoint = self.computeProjectionPoint(point, selectedEdgeStartPoint, selectedEdgeEndPoint, selectedEdgeAngle)
		matchedGid = getFormatGID(matchedPoint, self.LngSPLIT, self.LatSPLIT, self.locs)['gid']
		matchedAngle = selectedEdgeAngle;

		matchedGridStartPoint, matchedGridEndPoint = getGridIntersection(matchedPoint, matchedAngle, matchedGid, self.LngSPLIT, self.LatSPLIT, self.locs)

		matchedEdge = {}
		matchedEdge['point'] = matchedPoint
		matchedEdge['gid'] = matchedGid
		matchedEdge['angle'] = matchedAngle
		matchedEdge['gstart-point'] = matchedGridStartPoint
		matchedEdge['gend-point'] = matchedGridEndPoint

		return matchedEdge

	def findCandidateEdges(self, gid, roadEdgesData, gridSearchRange):

		candidateEdges = []
		candidateGrids = getGIDsByOffsets(gid, gridSearchRange, self.LngSPLIT, self.LatSPLIT, self.locs)

		for search_gid in candidateGrids:
			if search_gid in roadEdgesData.keys():
				for roadEdgeStr in roadEdgesData[search_gid]:
					candidateEdges.append(roadEdgeStr)

		return candidateEdges

	def computeEdgeMatchingWeight(self, point, angle, roadStartPoint, roadEndPoint, roadAngle):

		dist = self.computeProjectionDistance(point, roadStartPoint, roadEndPoint, roadAngle)
		distWeight = 0

		if dist > self.distZeroMatching * 2:
			distWeight = -1
		else:
			distWeight = (self.distZeroMatching - dist)/self.distZeroMatching
			
		angleWeight = math.cos(math.pi * (roadAngle - angle)/180)

		totalWeight = distWeight * self.distMatchingRatio + angleWeight * self.angleMatchingRatio

		return totalWeight

	def computeProjectionPoint(self, point, roadStartPoint, roadEndPoint, roadAngle):

		if roadAngle == 90 or roadAngle == 270:

			pointX = roadStartPoint[0]
			pointY = point[1]

			if (pointY - roadStartPoint[1]) * (pointY - roadEndPoint[1]) > 0:
				if abs(pointY - roadStartPoint[1]) > abs(pointY - roadEndPoint[1]):
					pointY = roadEndPoint[1]
				else:
					pointY = roadStartPoint[1]

			return [pointX, pointY]

		a = math.tan(math.pi * roadAngle/180)
		b = -1
		c = roadStartPoint[1]- a * roadStartPoint[0]

		pointX = (b * (b * point[0] - a * point[1]) - a * c)/(a * a + b * b)
		pointY = (a * (a * point[1] - b * point[0]) - b * c)/(a * a + b * b)

		if (pointX - roadStartPoint[0]) * (pointX - roadEndPoint[0]) > 0:
			if abs(pointX - roadStartPoint[0]) > abs(pointX - roadEndPoint[0]):
				pointX = roadEndPoint[0]
				pointY = roadEndPoint[1]
			else:
				pointX = roadStartPoint[0]
				pointY = roadStartPoint[1]

		return [pointX, pointY]

	def computeProjectionDistance(self, point, roadStartPoint, roadEndPoint, roadAngle):

		if roadAngle == 90 or roadAngle == 270:

			pointX = roadStartPoint[0]
			pointY = point[1]

			dist = getRealDistance(point[0], point[1], pointX, pointY)

			if (pointY - roadStartPoint[1]) * (pointY - roadEndPoint[1]) > 0:
				if abs(pointY - roadStartPoint[1]) > abs(pointY - roadEndPoint[1]):
					dist = dist + getRealDistance(pointX, pointY, roadEndPoint[0], roadEndPoint[1])					
				else:
					dist = dist + getRealDistance(pointX, pointY, roadStartPoint[0], roadStartPoint[1])					

			return dist

		a = math.tan(math.pi * roadAngle/180)
		b = -1
		c = roadStartPoint[1]- a * roadStartPoint[0]

		pointX = (b * (b * point[0] - a * point[1]) - a * c)/(a * a + b * b)
		pointY = (a * (a * point[1] - b * point[0]) - b * c)/(a * a + b * b)

		dist = getRealDistance(point[0], point[1], pointX, pointY)

		if (pointX - roadStartPoint[0]) * (pointX - roadEndPoint[0]) > 0:
			if abs(pointX - roadStartPoint[0]) > abs(pointX - roadEndPoint[0]):
				dist = dist + getRealDistance(pointX, pointY, roadEndPoint[0], roadEndPoint[1])
			else:
				dist = dist + getRealDistance(pointX, pointY, roadStartPoint[0], roadStartPoint[1])	
		
		return dist


		



