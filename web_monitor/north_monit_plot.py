import time
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, date2num
import numpy as np
import subprocess as sp
import time
import sys
import os
from itertools import groupby

secsInWeek = 604800 
secsInDay = 86400 
gpsEpoch = (1980, 1, 6, 0, 0, 0)  # (year, month, day, hh, mm, ss)

def UTCFromGps(gpsWeek, SOW, leapSecs=17):
	"""converts gps week and seconds to UTC 
	see comments of inverse function! 
	SOW = seconds of week 
	gpsWeek is the full number (not modulo 1024) 
	""" 
	secFract = SOW % 1 
	epochTuple = gpsEpoch + (-1, -1, 0)  
	t0 = time.mktime(epochTuple) - time.timezone  #mktime is localtime, correct for UTC 
	tdiff = (gpsWeek * secsInWeek) + SOW - leapSecs 
	t = t0 + tdiff 
	(year, month, day, hh, mm, ss, dayOfWeek, julianDay, daylightsaving) = time.gmtime(t) 
	#use gmtime since localtime does not allow to switch off daylighsavings correction!!! 
	return (year, month, day, hh, mm, ss + secFract)

data_dir = '/home/augta/web_monitor/'
file_list = ['north_batt.txt','north_itemp.txt','north_hum.txt',
	'north_otemp.txt','north_ap.txt']
label_list = ['Voltage (V)','Temperature (deg. C)','Percent humidity',
	'Temperature (deg. C)','Atmospheric Pressure (mmHg)']

q = 0
for f in file_list:
	x = np.loadtxt(data_dir + f, usecols=(0,), dtype=int)
	y = np.loadtxt(data_dir + f, usecols=(1,))
	if 'otemp' in f:
		y[y>1000] = 0.
	n = len(x)
	x_str = [0]*n
	for i in range(n):
		gps_int = x[i]
		week = gps_int / secsInWeek
		sow = gps_int - week*secsInWeek
		utc = UTCFromGps(week,sow)
		x_str[i] = "%i-%02d-%02d %02d:%02d:%02d" %utc
	if n > 154:
		y = y[-154:]
		x_str = x_str[-154:]
		n = len(y)
	x_index = np.arange(n)
	plt.plot(x_index,y,'.--')
	plt.xticks(x_index[::10],x_str[::10],rotation=90,fontsize='large')
	plt.yticks(fontsize='large')
	plt.ylabel(label_list[q],fontsize='large')
	plt.tight_layout()
	img_name = f.split('.')[0]
	plt.savefig('/var/www/html/monitor/img/%s.png' %img_name,frameon=1)
	plt.close('all')
	q += 1