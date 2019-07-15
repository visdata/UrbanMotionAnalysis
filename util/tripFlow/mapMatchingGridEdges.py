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
import math


class MapMatchingGridEdges(object):
	def __init__(self, PROP):
		super(MapMatchingGridEdges, self).__init__()
		self.resByCate = PROP['resByCate'];
    
	def run(self):
		# map matching 
		
		return {
			'count': self.singleDirectionCount,
			'res': res
		}
		