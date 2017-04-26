import time
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
import numpy as np
import subprocess as sp
import time
import sys
import os
from itertools import groupby

secsInWeek = 604800 
secsInDay = 86400 
gpsEpoch = (1980, 1, 6, 0, 0, 0)  # (year, month, day, hh, mm, ss)

fdate = sp.check_output(['date','--date','yesterday','+%Y%m%d'])
fdate = fdate.replace('\n','')
yr = int(fdate[:4])
mo = int(fdate[4:6])
dy = int(fdate[6:])

file_name = "%i_%02d_%02d.TAL.gz" %(yr,mo,dy)

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

data_dir = '/home/augta/data/ta/'

data = np.loadtxt(data_dir + file_name, dtype='S50')

gps_str = [int(k.split('.')[0]) for k in data]

counts = np.array([len(list(group)) for key, group in groupby(gps_str)])

gps_sec = [list(group)[0] for key, group in groupby(gps_str)]

start_time = gps_sec[0]

gps_str_np = np.array(gps_str)

# Time stamps are not evenly sampled over each hour

avg_hourly_counts = np.zeros(24)
std_hourly_counts = np.zeros(24)

gps_hours = np.arange(start_time,start_time + 24*3600, 3600)
utc_hours = np.empty(24,dtype='S50')

for i in range(24):
	gps_int = gps_hours[i]
	week = gps_int / secsInWeek
	sow = gps_int - week*secsInWeek
	utc = UTCFromGps(week,sow)
	utc_hours[i] = "%i-%02d-%02d %02d:%02d:%02d" %utc

for i in range(24):
	tmp = gps_str_np[gps_str_np > start_time + i * 3600]
	tmp = tmp[tmp < start_time + (i+1)*3600]
	tmp_counts = [len(list(group)) for key, group in groupby(tmp)]
	avg_hourly_counts[i] = np.mean(tmp_counts)
	std_hourly_counts[i] = np.std(tmp_counts)

x=np.arange(0.5,24.5,1)
xlab = np.arange(0,24,1)
fig,ax=plt.subplots()
plt.errorbar(x,avg_hourly_counts,yerr=std_hourly_counts,marker='s',
	linestyle='--',fillstyle='none')
plt.xticks(xlab,utc_hours,rotation=90,fontsize='large')
minorLocator = AutoMinorLocator()
ax.yaxis.set_minor_locator(minorLocator)
plt.ylim(ymin=0)
plt.yticks(fontsize='large')
plt.ylabel('Frequency [Hz]',fontsize='large')
plt.xlabel('Time [UTC]',fontsize='large')
plt.tight_layout()
plt.savefig('/var/www/html/monitor/img/daily_ta_local.png',frameon=1)
plt.close('all')

with open('/home/augta/web_monitor/ta_local_hourly.txt','a') as f:
	for i in range(24):
		f.write('%s %.3f %.3f\n' %(utc_hours[i],avg_hourly_counts[i],
			std_hourly_counts[i]))

# Make plot of last two weeks (if data available)
hourly_file = '/home/augta/web_monitor/ta_local_hourly.txt'
yyyymmdd,hhmmss = np.loadtxt(hourly_file,unpack=True,usecols=(0,1),dtype='S50')
t = np.zeros(len(hhmmss),dtype='S100')
for i in range(len(t)):
	t[i] = yyyymmdd[i] + ' ' + hhmmss[i]

avg,std = np.loadtxt(hourly_file,unpack=True,usecols=(2,3))
# There are 336 hours in 2 weeks
# If we have < 336 entries, use the entire array
if len(avg) < 336:
	xlab = t[::4]
	N = len(avg)
	xpos = np.arange(0.5,N,4)
	x = np.arange(0,N,4)
	fig,ax=plt.subplots()
	plt.errorbar(np.arange(N),avg,yerr=std,marker='s',
	linestyle='--',fillstyle='none')
	plt.xticks(xpos,xlab,rotation=90,fontsize='large')
	minorLocator = AutoMinorLocator()
	ax.yaxis.set_minor_locator(minorLocator)
	plt.ylim(ymin=0)
	plt.yticks(fontsize='large')
	plt.ylabel('Frequency [Hz]',fontsize='large')
	plt.xlabel('Time [UTC]')
	plt.tight_layout()
	plt.savefig('/var/www/html/monitor/img/weekly_ta_local.png',frameon=1)
	plt.close('all')
else:
	t = t[-336:]
	avg = avg[-336:]
	std = std[-336:]
	xlab = t[::12]
	N = len(avg)
	xpos = np.arange(0.5,N,12)
	x = np.arange(0,N,12)
	fig,ax=plt.subplots()
	plt.errorbar(np.arange(N),avg,yerr=std,marker='s',
	linestyle='--',fillstyle='none')
	plt.xticks(xpos,xlab,rotation=90,fontsize='large')
	minorLocator = AutoMinorLocator()
	ax.yaxis.set_minor_locator(minorLocator)
	plt.ylim(ymin=0)
	plt.yticks(fontsize='large')
	plt.ylabel('Frequency [Hz]',fontsize='large')
	plt.xlabel('Time [UTC]')
	plt.tight_layout()
	plt.show(fig)
	plt.savefig('/var/www/html/monitor/img/weekly_ta_local.png',frameon=1)
	plt.close('all')
