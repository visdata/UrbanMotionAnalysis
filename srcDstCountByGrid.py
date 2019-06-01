import sys;
import string;
import time;
from util.tripFlow.base import getFormatGID

readPath = '/datahouse/tripflow/SRCDST-TJ/tj-byhour-tf/';
writePath = '/datahouse/tripflow/SRCDST-TJ/tj-byhour-res/';

startIndex = 0;
endIndex = 2087;

# from_array=[0]*10000000;
#to_array=[0]*10000000;

MAX_INDEX = 0;


def main():
    start_time = time.time();
    global MAX_INDEX;
    from_array = [0] * 10000000;
    to_array = [0] * 10000000;


    for file_index in range(startIndex, endIndex + 1):
        filename_r = "traveldata-" + str(file_index);
        filename_w = str(file_index % 24) + "-" + str(file_index);

        content = file(readPath + filename_r, 'r').read();
        records = content.split("\n");

        for record_index in range(len(records) - 1):
            record = records[record_index];
            columns = record.split(",");
            gridId = getFormatGID([columns[4], columns[3]],0.0064,0.005, {
			'north': 40.2500,
			'south': 38.5667,
			'west': 116.7167,
			'east': 118.3233,
			})["gid"]

            if gridId > MAX_INDEX:
                MAX_INDEX = gridId;
            if columns[5] == "src":
                from_array[gridId] = from_array[gridId] + 1;
            elif columns[5] == "dst":
                to_array[gridId] = to_array[gridId] + 1;

        resultFile = file(writePath + filename_w, 'w');

        for i in range(MAX_INDEX + 1):
            resultFile.write(str(i) + "," + str(from_array[i]) + "," + str(to_array[i]) + "\n");
            from_array[i] = 0;
            to_array[i] = 0;
        resultFile.close();
        MAX_INDEX = 0;
    # filename_w = str(4017) + "-" + str(4017);
    # resultFile = file(writePath + filename_w, 'w');
    # for i in range(MAX_INDEX + 1):
    #     resultFile.write(str(i) + "," + str(from_array[i]) + "," + str(to_array[i]) + "\n");
    #     from_array[i] = 0;
    #     to_array[i] = 0;
    # resultFile.close();
    # MAX_INDEX = 0;

    print "Complete Time:" + str(time.time() - start_time);

if __name__ == '__main__':
    main()
