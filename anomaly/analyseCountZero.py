__author__ = 'lenovo'
import numpy as np
import matplotlib.pyplot as pyplot
countZero = np.load('sampleDistance.npy')
#print(countZero)
#filterarr = [elem[0] for elem in countZero ]
#print(np.average(filterarr))
#print(len(filterarr))
#filterarr.sort()
pyplot.hist(countZero, 55, normed=True, histtype='step', cumulative=True)
pyplot.xlabel('variance')
pyplot.xlim(0, 12088)
pyplot.ylabel('Frenquency')
#pyplot.ylim(0, 30000)
pyplot.title('variance distribution from 7:00am to 10:00am')
pyplot.show()

