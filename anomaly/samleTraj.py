__author__ = 'lenovo'
import numpy as np

arr = np.load('distance.npy')
arr = [arr[i] for i in range(0,len(arr),5)]
np.save('sampleDistance.npy',arr)