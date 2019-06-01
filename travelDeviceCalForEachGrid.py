# -*- coding: utf-8 -*-
#
# Input Format:
# [tripFlow-x]
# hour, id, time, lat, lng, from_lat, from_lng, from_time, to_lat, to_Lng, to_time
#
# Output Format:
# [hares-x]???
# id, seg, hour, wday, gid, state, admin, from_gid, to_gid, from_aid, to_aid
#
#

__author__ = 'lenovo'

import os
import json
from util.tripFlow.base import getFormatGID
from util.tripFlow.base import parseFormatGID

INPUT_PATH = "/datahouse/tripflow/200/bj-byhour-tf"
OUTPUT_PATH = "/datahouse/tripflow/test/bj-byhour-td"


start_index = 1
end_index = 2088


for hourId in range(start_index, end_index):
    ifilename = "traveldata-" + str(hourId)
    ofilename = str(hourId % 24) + "-" + str(hourId)

    ifile = os.path.join(INPUT_PATH, ifilename)

    res = [0] * 104000
    #遍历
    with open(ifile, 'rb') as f:
        devIdDict = {}
        for line in f:
            linelist = line.split(',')

            lat = linelist[3]
            lng = linelist[4]

            gid = getFormatGID([lng, lat])['gid']
            devId = int(linelist[1])

            if devIdDict.has_key(gid):
                if devId not in devIdDict[gid]:
                    devIdDict[gid].append(devId)
                    res[gid] += 1
            else:
                devIdDict[gid] = [devId]
                res[gid] += 1
            #res[gid] += 1
    f.close()
    # 写入文件
    preline=[[] for j in xrange(len(res))];

    ofile = os.path.join(OUTPUT_PATH, ofilename)
    with open(ofile, 'wb') as output:
        for index in xrange(len(res)):
            dirDict = parseFormatGID(index);
            preline[index].append(int(index));
            preline[index].append(float(dirDict['lng']));
            preline[index].append(float(dirDict['lat']));
            preline[index].append(int(res[index]));
            output.write(str(index)+","+str(dirDict['lng'])+","+str(dirDict['lat'])+","+str(res[index])+"\n");
    output.close()
    ojsonFile = os.path.join(OUTPUT_PATH, ofilename+".json")
    with open(ojsonFile, 'wb') as foutput:
        foutput.write(json.dumps(preline));
    foutput.close()