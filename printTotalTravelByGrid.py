import numpy as np
import matplotlib.pyplot as pyplot

arr = np.load('travelByGrid_9.npy')
# for i in range(24):
#     arrtmp = arr[i]
#     np.save('travelByGrid_'+str(i)+'.npy', arrtmp)

# arr_12 = arr[12]
# np.save('travelByGrid_12.npy', arr_12)

pyplot.hist(arr, 20, normed=True, histtype='step', cumulative=True)
pyplot.xlabel('variance')
pyplot.xlim(0, 20)
pyplot.ylabel('Frenquency')
#pyplot.ylim(0, 30000)
pyplot.title('9:00')
pyplot.show()