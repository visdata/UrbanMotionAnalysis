# -*- coding: utf-8 -*-
__author__ = 'lenovo'


from util.tripFlow.base import getFormatGID
from util.tripFlow.base import getDirection
from util.tripFlow.extractGridEdges import ExtractGridEdges


tPoint = [161.12, 40.35]
fPoint = [161.57, 39.79]

PROP = {
		'index': 9,
		'delta': -1,
		'IDIRECTORY': '/datahouse',
		'ODIRECTORY': '/datahouse',
		'subfix': 1
	}
task = ExtractGridEdges(PROP)
direction = getDirection(fPoint, tPoint)
fromGid = getFormatGID(fPoint)['gid']
toGid = getFormatGID(tPoint)['gid']
print(direction)
speed = 2.3
task.updateResByLine(fPoint, tPoint, fromGid, toGid,direction, speed)

print(task.resByCate['from'])
print(task.resByCate['to'])

#证明from和to的方向是一样的