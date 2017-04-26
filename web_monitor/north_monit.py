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

fdate = sp.check_output(['date','--date','-1 days','+%Y%m%d'])
fdate = fdate.replace('\n','')
yr = int(fdate[:4])
mo = int(fdate[4:6])
dy = int(fdate[6:])

date = "%i_%02d_%02d" %(yr,mo,dy)
dirlist = os.listdir('/home/augta/data/north/Monitor/%i%02d%02d/' %(yr,mo,dy))
dirlist = [k for k in dirlist if '.dat' in k]
dirlist.sort()

internal_temp = np.empty(0)
internal_humidity = np.empty(0)
outside_temp = np.empty(0)
ap = np.empty(0)
batt = np.empty(0)

for monitfile in dirlist:
	tmp = sp.check_output(['/home/augta/web_monitor/dmpmonit','-i',
	'/home/augta/data/north/Monitor/%i%02d%02d/%s' %(yr,mo,dy,monitfile),
	'-o','/dev/stdout'])
	tmp = tmp.split('\n')
	tmp_gps = [int(k.split(' ')[1]) for k in tmp if 'V-BATT ' in k]
	tmp_vbatt = [float(k.split(' ')[2]) for k in tmp if 'V-BATT ' in k]
	tmp_int_temp = [float(k.split(' ')[2]) for k in tmp if 'LSC-T ' in k]
	tmp_int_hum = [float(k.split(' ')[2]) for k in tmp if 'LSC-H ' in k]
	tmp_out_temp = [float(k.split(' ')[2]) for k in tmp if 'TPCB-T ' in k]
	tmp_out_ap = [float(k.split(' ')[2]) for k in tmp if 'TPCB-AP ' in k]
	N = len(tmp_gps)
	with open('/home/augta/web_monitor/north_batt.txt','a') as f:
		for i in range(0,N,12):
			f.write('%i %.3f\n' %(tmp_gps[i],tmp_vbatt[i]))
	with open('/home/augta/web_monitor/north_itemp.txt','a') as f:
		for i in range(0,N,12):
			f.write('%i %.3f\n' %(tmp_gps[i],tmp_int_temp[i]))
	with open('/home/augta/web_monitor/north_hum.txt','a') as f:
		for i in range(0,N,12):
			f.write('%i %.3f\n' %(tmp_gps[i],tmp_int_hum[i]))
	with open('/home/augta/web_monitor/north_otemp.txt','a') as f:
		for i in range(0,N,12):
			f.write('%i %.3f\n' %(tmp_gps[i],tmp_out_temp[i]))
	with open('/home/augta/web_monitor/north_ap.txt','a') as f:
		for i in range(0,N,12):
			f.write('%i %.3f\n' %(tmp_gps[i],tmp_out_ap[i]))
