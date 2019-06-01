__author__ = 'lenovo'
import time
def formatTime(timestr):
	dateObj = time.localtime(int(timestr))

	return {
		'hour': dateObj[3],
		'yday': dateObj[7],
		'wday': dateObj[6]
	}

print(formatTime(1473911530)['yday']-187)