import sys;
from math import sqrt;
from scipy import stats;
import time;
import math;
import json;
import numpy as np;


readPath = "/datahouse/tripflow/Anomaly/tj-byhour-statics/"
writePath = "/datahouse/tripflow/Anomaly/tj-byhour-ano/";

startIndex = 0;
endIndex = 1;

records_array = [];

#count_zero = np.load('countZero.npy')
#count_total_zero = [0 for i in range(104000)]
zero_rate = 0.5
avg_travel_num = 5
avg_total_num = 30


def avg(sequence):
    if len(sequence) < 1:
        return 0;
    seq = [float(i) for i in sequence];
    return sum(seq) / len(seq);


def stdev(sequence):
    if len(sequence) < 1:
        return 0;
    _avg = avg(sequence);
    sdsq = sum([(i - _avg) ** 2 for i in sequence])/len(sequence);
    return sqrt(sdsq);

def getAvgWithoutSelf(avgnum, n, num):
    return float(avgnum * n - num)/float(n-1)

def getStdWithoutSelf(avgnum, stdnum, n, num):
    return sqrt(float((stdnum**2)*n - (num-avgnum)**2)/float(n-1))

def EVT_score_compute_by_vector(m_star, raw_value, mean, std_var):
    mahalanobis_distance = (np.abs(raw_value - mean) / std_var)
    h_star = mahalanobis_distance

    mean_m = np.sqrt(2 * np.log(m_star)) - (
    (np.log(np.log(m_star)) + np.log(2 * np.pi)) / (2 * np.sqrt(2 * np.log(m_star))))
    # mean_m = np.sqrt(2*np.log(m_star))-((np.log(np.log(m_star))+np.log(2*np.pi))/(2*np.sqrt(2*np.log(m_star))))
    #print mean_m
    std_m = 1.0/np.sqrt(2 * np.log(m_star))
    #std_m = np.sqrt(2*np.log(m_star))
    #print std_m

    y_m = (h_star - mean_m) / std_m
    #print y_m

    p_v = np.exp(-np.exp(-y_m))
    #print p_v
    #expected_highest_anomaly_score = 1.2
    expected_highest_anomaly_score = 8
    #score = np.minimum(np.eye(raw_value.shape[0]),((-np.log(1-p_v))/expected_highest_anomaly_score))
    score = np.minimum(1, ((-np.log(1 - p_v)) / expected_highest_anomaly_score))
    #print(score)
    for i in range(len(score)):
        if raw_value[i] < mean:
            score[i] = -score[i]
    return score


def main():
    # load flowcount
    with open("/datahouse/tripflow/Anomaly/bj-flowcount/flowcount.json", 'r') as stream:
        flowCountDict = json.load(stream);
    flowCount = [];
    for x in xrange(87):
        flowCount.append(sum(flowCountDict[x]['flowCount']));
    df1=[[] for i in range(90)];

    df2=[[] for i in range(24)];	#data_feature2

    for file_index in range(0, 2088):
        filename=str(file_index%24)+"-"+str(file_index);
        content=file(readPath+filename, 'r').read();
        records=content.split("\n");
        records_array.append(records[:len(records)-1]);
        # for k in range(len(records)):
        #     record = records[k];
        #     columns = record.split(",")
        #     if len(columns) == 4:
        #         grid_index = int(columns[0]);
        #         # if columns[1] == '0':
        #         #     count_zero[grid_index][0] = count_zero[grid_index][0] + 1;
        #         if columns[2] == '0':
        #             count_zero[grid_index][0] = count_zero[grid_index][0] + 1;
        #         # if columns[3] == '0':
        #         #     count_zero[grid_index][2] = count_zero[grid_index][2] + 1;

    np.save('recordsArray.npy',records_array)
    #records_array = np.load('recordsArray.npy')
    #count_total_zero = np.load('count_total_zero.npy')
    # for records in records_array:
    #     for record in records:
    #         columns = record.split(",")
    #         grid_index = int(columns[0]);
    #         if columns[3] == '0':
    #             count_total_zero[grid_index] = count_total_zero[grid_index] + 1;
    # np.save('count_total_zero.npy', count_total_zero)
    #cal df1
    # for i in range(90):
    #     if 24 * i > 2087:
    #         break;
    #     for record_index in range(104000):
    #         stay_array = [];
    #         travel_array = [];
    #         total_array = []
    #         for j in range(24):
    #             if j + 24 * i > 2087:
    #                 break;
    #             if record_index < len(records_array[j + 24 * i]):
    #                 record = records_array[j + 24 * i][record_index];
    #                 columns = record.split(",");
    #                 stay_array.append(float(columns[1]));
    #                 travel_array.append(float(columns[2]));
    #                 total_array.append(float(columns[3]));
    #             else:
    #                 stay_array.append(0.0);
    #                 travel_array.append(0.0);
    #                 total_array.append(0.0);
    #
    #         avg_s = avg(stay_array);
    #         stdev_s = stdev(stay_array);
    #
    #         avg_t = avg(travel_array);
    #         stdev_t = stdev(travel_array);
    #
    #         avg_a = avg(total_array)
    #         stdev_a = avg(total_array)
    #         n = len(stay_array)
    #         df1[i].append([avg_s, stdev_s, avg_t, stdev_t, avg_a, stdev_a, n]);


    #print(records_array)
    for i in range(24):
        for record_index in range(104000):
            stay_array = [];
            travel_array = [];
            total_array = []
            j = 7;
            while j * 24 + i < 2088:
                if record_index < len(records_array[j * 24 + i]):
                    record = records_array[j * 24 + i][record_index];
                    columns = record.split(",");
                    stay_array.append(float(columns[1]));
                    travel_array.append(float(columns[2]));
                    total_array.append(float(columns[3]));
                else:
                    stay_array.append(0.0);
                    travel_array.append(0.0);
                    total_array.append(0.0);
                j = j + 1;

            #print(stay_array)
            avg_s = avg(stay_array);
            stdev_s = stdev(stay_array);

            avg_t = avg(travel_array);
            stdev_t = stdev(travel_array);

            avg_a = avg(total_array)
            stdev_a = avg(total_array)

            df2[i].append([avg_s, stdev_s, avg_t, stdev_t, avg_a, stdev_a, stay_array, travel_array, total_array]);
    #np.save('df2.npy',df2)
    # iterate all records
    for file_index in range(startIndex, endIndex + 1):
        filename = str(file_index % 24) + "-" + str(file_index);
        resultFile = file(writePath + "ano-" + filename, 'w');
        for record_index in range(len(records_array[file_index])):
            columns = records_array[file_index][record_index].split(",");
            stay_ = float(columns[1]);
            travel_ = float(columns[2]);
            total_ = float(columns[3]);

            raw_value_list = [stay_]
            raw_value_vector = np.array(raw_value_list, dtype=np.float64)

            ano_s1 = 0.0
            # if df1[file_index / 24][record_index][1] != 0:
            #     ano_s1 = EVT_score_compute_by_vector(24, raw_value_vector, getAvgWithoutSelf(df1[file_index / 24][record_index][0],df1[file_index / 24][record_index][6], stay_),
            #                                          getStdWithoutSelf(df1[file_index / 24][record_index][0], df1[file_index / 24][record_index][1],df1[file_index / 24][record_index][6], stay_))[0]
            # else:
            #     ano_s1 = 0.87


            ano_s2 = 0.0;
            # arr = df2[file_index % 24][record_index][6]
            # index = arr.index(stay_)
            # arr = arr[0:index]+arr[index+1:]
            # std_s = stdev(arr)
            # if std_s != 0:
            #     ano_s2 = EVT_score_compute_by_vector(87, raw_value_vector, avg(arr),std_s)[0]
            # else:
            #     #ano_s2 = 0.0
            #     new_avg = avg(arr)
            #     if new_avg == 0:
            #         ano_s2 = 0.0;
            #     else:
            #         ano_s2 = (stay_-new_avg)/new_avg



            raw_value_list = [travel_]
            raw_value_vector = np.array(raw_value_list, dtype=np.float64)
            ano_t1 = 0.0;
            # if df1[file_index / 24][record_index][3] != 0:
            #     ano_t1 = EVT_score_compute_by_vector(24, raw_value_vector, df1[file_index / 24][record_index][2],
            #                                          df1[file_index / 24][record_index][3])[0]
            # else:
            #     ano_t1 = 0.0;


            #ano_t2 = 0.0;
            arr = df2[file_index % 24][record_index][7]
            index = arr.index(travel_)
            arr = arr[0:index]+arr[index+1:]
            std_t = stdev(arr)
            #std_t = getStdWithoutSelf(df2[file_index / 24][record_index][2], df2[file_index / 24][record_index][3], 87, travel_)
            if  df2[file_index % 24][record_index][2] < avg_travel_num:
                ano_t2 = 0.0
            elif std_t != 0:
                ano_t2 = EVT_score_compute_by_vector(79, raw_value_vector, avg(arr), std_t)[0]
            else:
                new_avg = avg(arr)
                if new_avg == 0:
                    ano_t2 = 0.0;
                else:
                    ano_t2 = (travel_-new_avg)/new_avg

            raw_value_list = [total_]
            raw_value_vector = np.array(raw_value_list, dtype=np.float64)
            ano_a1 = 0.0
            # if df1[file_index / 24][record_index][3] != 0:
            #     ano_a1 = EVT_score_compute_by_vector(24, raw_value_vector, df1[file_index / 24][record_index][4],
            #                                          df1[file_index / 24][record_index][5])[0]
            # else:
            #     ano_a1 = 0.0;

            ano_a2 = 0.0;
            arr = df2[file_index % 24][record_index][8]
            index = arr.index(total_)
            arr = arr[0:index]+arr[index+1:]
            std_a = stdev(arr)
            #std_a = getStdWithoutSelf(df2[file_index / 24][record_index][4], df2[file_index / 24][record_index][5],87, total_)

            if df2[file_index % 24][record_index][4] < avg_total_num:
               ano_t2 = 0.0
            elif std_a != 0:
                ano_a2 = EVT_score_compute_by_vector(79, raw_value_vector,avg(arr),std_a)[0]
            else:
                #ano_a2 = 0.0;
                new_avg = avg(arr)
                if new_avg == 0:
                    ano_a2 = 0.0;
                else:
                    ano_a2 = (total_-new_avg)/new_avg

            resultFile.write(
                str(record_index) + "," + str(columns[1]) + "," + str(columns[2]) + "," + str(ano_s1) + "," + str(
                    ano_t1) + "," + str(ano_a1) + "," + str(ano_s2) + "," + str(ano_t2) + "," + str(ano_a2) + "\n");

        #resultFile.write(str(record_index)+","+str(columns[1])+","+str(columns[2])+","+str(ano_s1)+","+str(ano_t1)+","+str(ano_a1)+","+str(ano_s2)+","+str(ano_t2)+","+str(ano_a2)+"\n");

        resultFile.close();

if __name__ == '__main__':
    start_time = time.time();
    main();
    print "Complete Time: " + str(time.time() - start_time);





