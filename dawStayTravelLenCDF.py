__author__ = 'lenovo'

import numpy as np
import matplotlib.pyplot as pyplot
stayarray = np.load('stay.npy')
stayarray.sort()
stayarray = [elem for elem in stayarray if elem < 207360 ]
travelArray = np.load('travel.npy')
lenth = len(stayarray)
print(stayarray)
cdf = []
for i in range(lenth):
    cdf.append((i+1)/lenth)

print(len(stayarray))

#pyplot.plot(stayarray,cdf)
pyplot.hist(stayarray, 20, normed=True, histtype='step', cumulative=True)
pyplot.xlabel('variance')
pyplot.xscale("log")
pyplot.xlim(1e3, 1e6)
pyplot.ylabel('Frenquency')
#pyplot.ylim(0, 1)
pyplot.title('variance distribution from 7:00am to 10:00am')
pyplot.show()