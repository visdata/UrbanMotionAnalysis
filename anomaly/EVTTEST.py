import numpy as np
from math import sqrt
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
    return sqrt(float(stdnum**2*n - (num-avgnum)**2)/float(n-1))

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

    expected_highest_anomaly_score = 1.2
    #score = np.minimum(np.eye(raw_value.shape[0]),((-np.log(1-p_v))/expected_highest_anomaly_score))
    score = np.minimum(1, ((-np.log(1 - p_v)) / expected_highest_anomaly_score))
    for i in range(len(score)):
        if raw_value[i] < mean:
            score[i] = -score[i]
    return score



arr = [80, 80, 80, 80, 81, 81, 80, 80, 80, 80, 81]
n = len(arr)
mean = avg(arr)
std = stdev(arr)
v= np.array([5], dtype=np.float64)
print(EVT_score_compute_by_vector(n, v, mean, std))