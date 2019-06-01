from math import atan2,sqrt,cos
import numpy as np


def averageDirection(angleArray,n):
    return sum(angleArray)/n


def angleDistance(angle):
   return angle

def std(angleArray, n, averageDir):
    sumValue = sum([pow(angleDistance(angle - averageDir), 2) for angle in angleArray])
    return sqrt(float(sumValue)/n)

def kurtosis(angleArray, n, averageDir, std):
    sumValue = sum([float(pow(angleDistance(angle - averageDir)/std, 4)) for angle in angleArray])
    return sumValue/n

def skewness(angleArray, n, averageDir, std):
    sumValue = sum([float(pow(angleDistance(angle - averageDir)/std, 3)) for angle in angleArray])
    return sumValue/n

def BCMetric(kurtosisValue, skewnessValue, n):
    return (pow(skewnessValue,2) + 1)/(kurtosisValue-3+float(3*pow(n-1,2))/((n-2)*(n-3)))

def BCCal(angleArry):
    arrLen = len(angleArry)
    averageDir = averageDirection(angleArry, arrLen)
    stdValue = std(angleArry,arrLen,averageDir)
    kurtosisValue = kurtosis(angleArry, arrLen, averageDir, stdValue)
    skewnessValie = skewness(angleArry,arrLen,averageDir,stdValue)

    print(averageDir, stdValue, kurtosisValue, skewnessValie)
    return BCMetric(kurtosisValue, skewnessValie, arrLen)

#anglearr = [0,0,0,0,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,180,0,0,0,0,0,0,0,0,0,0,0,0]
#anglearr = [[91.0, 1], [271.0, 1], [270.0, 1], [225.0, 1], [91.0, 1], [90.0, 1], [91.0, 1], [90.0, 1], [206.0, 1], [273.0, 1], [270.0, 1], [255.0, 1], [270.0, 1], [269.0, 1], [91.0, 1], [90.0, 1], [271.0, 1], [270.0, 1], [270.0, 1], [91.0, 1], [90.0, 1], [86.0, 1], [91.0, 1], [92.0, 1], [86.0, 1], [90.0, 1], [91.0, 1], [88.0, 1], [90.0, 1], [270.0, 1], [271.0, 1], [265.0, 1], [83.0, 1], [91.0, 1], [24.0, 1], [90.0, 1], [180.0, 1], [271.0, 1], [270.0, 1], [270.0, 1], [271.0, 1], [270.0, 1], [72.0, 1], [248.0, 1], [271.0, 1], [270.0, 1], [78.0, 1], [91.0, 1], [39.0, 1], [91.0, 1], [270.0, 1], [88.0, 1], [92.0, 1], [89.0, 1], [90.0, 1], [90.0, 1]]

anglearr = [[288.0, 1], [102.0, 1], [95.0, 1], [251.0, 1], [259.0, 1], [355.0, 1], [256.0, 1], [259.0, 1], [89.0, 1], [106.0, 1], [104.0, 1], [242.0, 1], [275.0, 1], [274.0, 1], [89.0, 1], [92.0, 1], [270.0, 1], [254.0, 1], [96.0, 1], [86.0, 1], [277.0, 1], [259.0, 1], [92.0, 1], [273.0, 1], [90.0, 1], [91.0, 1], [29.0, 1], [288.0, 1], [95.0, 1], [80.0, 1], [272.0, 1], [87.0, 1], [355.0, 1], [282.0, 1], [77.0, 1], [82.0, 1], [95.0, 1], [80.0, 1], [275.0, 1], [283.0, 1], [275.0, 1], [79.0, 1], [90.0, 1], [286.0, 1], [272.0, 1], [81.0, 1], [82.0, 1], [94.0, 1], [273.0, 1], [112.0, 1], [86.0, 1]]
anglearr = [elem[0] for elem in anglearr]
print(anglearr)
print(BCCal(anglearr))