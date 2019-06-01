import sys;
from math import sqrt;
from scipy import stats;
import time;
import math;
import json;


readPath = "/datahouse/tripflow/ano_detect/200/bj-byhour-io/"
writePath = "/datahouse/hcc/bj-byhour-ano/";

startIndex = 0;
endIndex = 2087;

records_array = [];
count_zero = [[0, 0] for i in range(104000)];
zero_rate = 0.5


def avg(sequence):
    if len(sequence) < 1:
        return 0;
    seq = [float(i) for i in sequence];
    return sum(seq) / len(seq);


def stdev(sequence):
    if len(sequence) < 1:
        return 0;
    _avg = avg(sequence);
    sdsq = sum([(i - _avg) ** 2 for i in sequence]);
    return sqrt(sdsq);


def main():
    # load flowcount
    with open("/datahouse/tripflow/ano_detect/200/bj-flowcount/flowcount.json", 'r') as stream:
        flowCountDict = json.load(stream);
    flowCount = [];
    for x in xrange(87):
        flowCount.append(sum(flowCountDict[x]['flowCount']));
    df1 = [[] for i in range(90)];  #data_feature1, daily
    df2 = [[] for i in range(24)];  #data_feature2, hou
    #load all records
    for file_index in range(startIndex, endIndex + 1):
        filename = str(file_index % 24) + "-" + str(file_index);
        content = file(readPath + filename, 'r').read();
        records = content.split("\n");
        #f_count_zero = 0;
        #t_count_zero = 0;
        for k in range(len(records)):
            record = records[k];
            columns = record.split(",")
            if len(columns) == 3:
                grid_index = int(columns[0]);
                if columns[1] == '0':
                    count_zero[grid_index][0] = count_zero[grid_index][0] + 1;
                    #f_count_zero = f_count_zero + 1;
                if columns[2] == '0':
                    count_zero[grid_index][1] = count_zero[grid_index][1] + 1;
                    #t_count_zero = t_count_zero + 1;
        #count_zero.append([f_count_zero, t_count_zero]);
        records_array.append(records[:len(records) - 1]);

    #cal df1
    print count_zero;
    for i in range(90):
        if 24 * i > endIndex:
            break;
        for record_index in range(104000):
            stay_array = [];
            travel_array = [];
            total_array = [];
            for j in range(24):
                if j + 24 * i > endIndex:
                    break;
                if record_index < len(records_array[j + 24 * i]):
                    record = records_array[j + 24 * i][record_index];
                    columns = record.split(",");
                    stay_array.append(float(columns[1]));
                    travel_array.append(float(columns[2]));
                    total_array.append(float(columns[3]));
                    # if count_zero[j+24*i][0] > endIndex*zero_rate:
                    #     from_array.append(0.0);
                    # else:
                    #     from_array.append(float(columns[1]) / flowCount[i]);
                    # if count_zero[j+24*i][1] > endIndex*zero_rate:
                    #     to_array.append(0.0);
                    # else:
                    #     to_array.append(float(columns[2]) / flowCount[i]);
                else:
                    stay_array.append(0.0);
                    travel_array.append(0.0);
                    total_array.append(0.0)
            avg_s = avg(stay_array);
            stdev_s = stdev(stay_array);

            avg_t = avg(travel_array);
            stdev_t = stdev(travel_array);

            avg_a = avg(total_array)
            stdev_a = avg(total_array)

            df1[i].append([avg_s, stdev_s, avg_t, stdev_t, avg_a, stdev_a]);
            stay_array = []
            travel_array = []
            total_array = []

    #cal df2
    for i in range(24):
        for record_index in range(104000):
            stay_array = [];
            travel_array = [];
            total_array = [];
            j = 0;
            while j * 24 + i < endIndex + 1:
                if record_index < len(records_array[j * 24 + i]):
                    record = records_array[j * 24 + i][record_index];
                    columns = record.split(",");
                    # if count_zero[j * 24 + i][0] > endIndex*zero_rate:
                    #     from_array.append(0.0);
                    # else:
                    #     from_array.append(float(columns[1]) / flowCount[j]);
                    # if count_zero[j * 24 + i][1] > endIndex*zero_rate:
                    #     to_array.append(0.0);
                    # else:
                    #     to_array.append(float(columns[2]) / flowCount[j]);
                    stay_array.append(float(columns[1]));
                    travel_array.append(float(columns[2]));
                    total_array.append(float(columns[3]));
                else:
                    stay_array.append(0.0);
                    travel_array.append(0.0);
                    total_array.append(0.0)
                j = j + 1;

            avg_s = avg(stay_array);
            stdev_s = stdev(stay_array);

            avg_t = avg(travel_array);
            stdev_t = stdev(travel_array);

            avg_a = avg(total_array)
            stdev_a = avg(total_array)

            df2[i].append([avg_s, stdev_s, avg_t, stdev_t, avg_a, stdev_a]);
            stay_array = []
            travel_array = []
            total_array = []

    #iterate all records

    for file_index in range(startIndex, endIndex + 1):
        filename = str(file_index % 24) + "-" + str(file_index);
        resultFile = file(writePath + "ano-" + filename, 'w');
        for record_index in range(len(records_array[file_index])):
            columns = records_array[file_index][record_index].split(",");
            stay_ = float(columns[1]) / flowCount[file_index % 24];
            travel_ = float(columns[2]) / flowCount[file_index % 24];
            total_ = float(columns[3]) / flowCount[file_index % 24];
            if df1[file_index / 24][record_index][1] != 0 and count_zero[record_index][0] < endIndex * zero_rate:
                ano_f1 = -math.log10(stats.norm.pdf(
                    (stay_ - df1[file_index / 24][record_index][0]) / df1[file_index / 24][record_index][1], 0, 1));
                if stay_ < df1[file_index / 24][record_index][0]:
                    ano_f1 = -ano_f1;
            else:
                ano_f1 = 0.0;
            if df2[file_index % 24][record_index][1] != 0 and count_zero[record_index][0] < endIndex * zero_rate:
                ano_f2 = -math.log10(stats.norm.pdf(
                    (from_ - df2[file_index % 24][record_index][0]) / df2[file_index % 24][record_index][1], 0, 1));
                if from_ < df2[file_index % 24][record_index][0]:
                    ano_f2 = -ano_f2;
            else:
                ano_f2 = 0.0;
            if df1[file_index / 24][record_index][3] != 0 and count_zero[record_index][1] < endIndex * zero_rate:
                ano_t1 = -math.log10(stats.norm.pdf(
                    (to_ - df1[file_index / 24][record_index][2]) / df1[file_index / 24][record_index][3], 0, 1));
                if to_ < df1[file_index / 24][record_index][2]:
                    ano_t1 = -ano_t1;
            else:
                ano_t1 = 0.0;
            if df2[file_index % 24][record_index][3] != 0 and count_zero[record_index][1] < endIndex * zero_rate:
                ano_t2 = -math.log10(stats.norm.pdf(
                    (to_ - df2[file_index % 24][record_index][2]) / df2[file_index % 24][record_index][3], 0, 1));
                if to_ < df2[file_index % 24][record_index][2]:
                    ano_t2 = -ano_t2;
            else:
                ano_t2 = 0.0;
            resultFile.write(
                str(record_index) + "," + str(columns[1]) + "," + str(columns[2]) + "," + str(ano_f1) + "," + str(
                    ano_t1) + "," + str(ano_f2) + "," + str(ano_t2) + "\n");
        resultFile.close();


if __name__ == '__main__':
    start_time = time.time();
    main();
    print
    "Complete Time: " + str(time.time() - start_time);
		

		
			
