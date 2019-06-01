#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import sys;
sys.path.append('../')
import string;
import time;
import json;
#from util.tripFlow.base import getFormatGID

def getFormatGID(point, LngSPLIT=0.0064, LatSPLIT=0.005, locs={
	'north': 41.0500,  # 41.050,
	'south': 39.4570,  # 39.457,
	'west': 115.4220,  # 115.422,
	'east': 117.5000,  # 117.500
}):
	"""
	[NEW] 根据经纬度计算城市网格编号

	Args:
		locs (TYPE): Description
		point (TYPE): [lng, lat]

	Returns:
		TYPE: Description
	"""
	if point[0] == '0' and point[1] == '0':
		return 0
	else:
		# LATNUM = int((locs['north'] - locs['south']) / SPLIT + 1)
		LNGNUM = int( (locs['east'] - locs['west']) / LngSPLIT + 1 )
		lngind = int( (float(point[0]) - locs['west']) / LngSPLIT )
		latind = int( (float(point[1]) - locs['south']) / LatSPLIT )

		return {
			'gid': lngind + latind * LNGNUM,
			'lngind': lngind,
			'latind': latind
		}
city = 'BJ'

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
		'TS':{
			'north': 40.3333,  # 41.050,
			'south': 35.9167,  # 39.457,
			'west': 117.50,  # 115.422,
			'east': 119.3167,  # 117.500
		}
	}

readPath = '/datahouse/tripflow/2019-30-800-'+city+'/'+city.lower()+'-byhour-res/';
writePath = '/datahouse/tripflow/2019-30-800-'+city+'/'+city.lower()+'-byhour-grid/';


startIndex = 1290;
endIndex = 1291;

# from_array=[0]*10000000;
#to_array=[0]*10000000;

MAX_INDEX = 0;
resDict = {};


def main():
    start_time = time.time();
    global MAX_INDEX;



    for file_index in range(startIndex, endIndex):
        resDict = {};

        filename_w = str(file_index % 24) + "-" + str(file_index) + '.json';

        filename_r = "tfres-angle-" + str(file_index) + "--1.00";

        content = file(readPath + filename_r, 'r').read();
        records = content.split("\n");
        for record_index in range(len(records) - 1):
            record = records[record_index];
            columns = record.split(",");
            # if int(columns[2]) > MAX_INDEX:
            #     MAX_INDEX = int(columns[2]);

            gridId = getFormatGID([float(columns[4]), float(columns[5])], 0.0064, 0.005, cityLatLngDict[city])["gid"];

            if resDict.has_key(gridId):
                resDict[gridId]["all"].append([float(columns[9]), 1])
            else:
                resDict[gridId] = {
                        "all": [[float(columns[9]),1]],
                        "lng": float(columns[4]),
                        "lat": float(columns[5])
                    }

        ofilename = str(startIndex % 24) + "-" + str(endIndex) + '.json';
        with open(writePath + filename_w, 'wb') as f:
            json.dump(resDict, f)
        f.close()

    MAX_INDEX = 0;

    print
    "Complete Time:" + str(time.time() - start_time);

if __name__ == '__main__':
    main()
