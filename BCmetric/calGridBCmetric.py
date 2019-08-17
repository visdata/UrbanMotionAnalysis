# -*- coding: utf-8 -*-
__author__ = 'lenovo'


from matplotlib import pyplot
from math import floor
import math
import simplejson
import json
import numpy
import time
from  util import BCCal




def comp(x):
    count = 0;
    for i in range(2, len(x)):
        count += int(x[i][1])
    return count

city = 'BJ'
INPUT_PATH = '/datahouse/tripflow/2019-30-800-'+city+'/'+city.lower()+'-byhour-grid/'
OUTPUT_PATH = '/datahouse/tripflow/2019-30-800-'+city+'/'+city.lower()+'-byhour-bc-sorted/'

startIndex = 9
endIndex = 10

startTime = time.time()

for i in range(startIndex, endIndex):
    total = 0
    count_zero = 0
    hourId = i
    fileName = str(hourId % 24) + "-" + str(hourId) + '.json';
    ofileName = str(hourId % 24) + "-" + str(hourId);

    d = []
    d1 = []
    fromArray = []
    toArray = []
    fromDict = []
    maxGridIndex = 0


    with open(INPUT_PATH + fileName, 'r') as f:
        obj = simplejson.load(f)
        for key in obj:
            #print('grid' + key + 'to is: ' + str(len(obj[key]["to"])))
            if key > maxGridIndex:
                maxGridIndex  = key

            if len(obj[key]["all"]) > 3:

                try:
                    total  += 1
                    angleArray = [ele[0] for ele in obj[key]["all"]]
                    tmp = [key, BCCal(angleArray)]
                    tmp.extend(obj[key]["all"])
                    toArray.append(tmp)
                    if BCCal(angleArray) > 1:
                        count_zero += 1

                except ZeroDivisionError, e:
                    continue


        toArray.sort(key=comp)

        fromArray.sort(key=comp)

        with open(OUTPUT_PATH + ofileName+"-all.json", 'wb') as tofile:
            json.dump(toArray, tofile)
        tofile.close()
        print(count_zero)
        print(total)
        print(float(count_zero)/total)

    f.close()

endTime = time.time()
print "CalBC seconds: %f" % (endTime-startTime)