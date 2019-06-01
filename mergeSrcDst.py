__author__ = 'lenovo'
# merge 7,8,9, 17,18,19


# 23,385044,1475161225,39.90723,116.45485,dst
# 23,1338467,1475163136,39.89888,116.66258,src
# 23,1720138,1475161225,40.0033,116.40127,src
# 23,1849304,1475164192,39.91667,116.11279,src
# 23,1849304,1475164192,39.91667,116.11279,dst
# 23,1910973,1475162934,39.86825,116.36176,src
# 23,1910973,1475162934,39.86658,116.35802,dst
# 23,2486485,1475162648,39.98419,116.3808,dst
# 23,4715751,1475163322,39.84465,116.3479,src
# 23,4715751,1475163322,40.00897,116.34595,dst
# 23,5034586,1475162154,39.83362,116.25628,dst
# 23,5096657,1475161373,39.87622,116.32081,dst
# travelhourid, deviceId, stayrecordTimestamp, latlngofstayrecord, src/dst
import sys;
import string;
import time;
from util.tripFlow.base import getFormatGID

readPath = '/datahouse/tripflow/SRCDST-BJ/bj-byhour-tf/';
writePath = '/datahouse/tripflow/SRCDST-BJ/bj-byhour-res/';

startIndex = 175;
endIndex = 177;

# from_array=[0]*10000000;
#to_array=[0]*10000000;

MAX_INDEX = 0;


def main():
    start_time = time.time();
    global MAX_INDEX;
    from_array = [0] * 10000000;
    to_array = [0] * 10000000;


    srcStayRecordDict = {}
    dstStayRecordDict = {}
    for file_index in range(startIndex, endIndex + 1):
        filename_r = "traveldata-" + str(file_index);
        filename_w = str(file_index % 24) + "-" + str(file_index);

        content = file(readPath + filename_r, 'r').read();
        records = content.split("\n");

        for record_index in range(len(records) - 1):
            record = records[record_index];
            columns = record.split(",");
            gridId = getFormatGID([columns[4], columns[3]])["gid"]

            key = str(columns[1])+'-'+str(columns[2])

            if gridId > MAX_INDEX:
                MAX_INDEX = gridId;
            if columns[5] == "src" and not srcStayRecordDict.has_key(key):
                srcStayRecordDict[key] = True
                from_array[gridId] = from_array[gridId] + 1;
            elif columns[5] == "dst" and not dstStayRecordDict.has_key(key):
                dstStayRecordDict[key] = True
                to_array[gridId] = to_array[gridId] + 1;

        #resultFile = file(writePath + filename_w, 'w');

        # for i in range(MAX_INDEX + 1):
        #     resultFile.write(str(i) + "," + str(from_array[i]) + "," + str(to_array[i]) + "\n");
        #     from_array[i] = 0;
        #     to_array[i] = 0;
        # resultFile.close();
        # MAX_INDEX = 0;
    filename_w = str(4175) + "-" + str(4175);
    resultFile = file(writePath + filename_w, 'w');
    for i in range(MAX_INDEX + 1):
        resultFile.write(str(i) + "," + str(from_array[i]) + "," + str(to_array[i]) + "\n");
        from_array[i] = 0;
        to_array[i] = 0;
    resultFile.close();
    MAX_INDEX = 0;

    print "Complete Time:" + str(time.time() - start_time);

if __name__ == '__main__':
    main()
