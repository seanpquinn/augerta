import os
import numpy as np
import subprocess as sp
import sys
import time
import datetime as dt

now = time.localtime()
yr = now.tm_year
mo = now.tm_mon
dy = now.tm_mday - 1
yr = 2016
mo = 12
dy = 16
fdate = "%i%02d%02d" %(yr,mo,dy)
os.chdir('/home/augta/web_monitor/tmpevt')
# Expected layout in cwd
# tmpevt/
#		t2/	

sp.call(['cp','/home/augta/data/north/Events/%s/evt_list.txt' %fdate,'.'])
evt_dat_list = np.loadtxt('evt_list.txt',dtype='S100')
os.chdir('t2')
dirlist = os.listdir('/home/augta/data/north/Events/%s' %fdate,)
tsp_list = [j for j in dirlist if '.tsp' in j]
tsp_list.sort()
for m in tsp_list:
	sp.call(['cp','/home/augta/data/north/Events/%s/%s' %(fdate,m),'.'])
# Rename .tsp file to match .dat file so the correct
#file name is given for the event retrieval script
tsp_k = 0
for k in tsp_list:
	tsp_time = k.split('.')[0]
	tsp_time = dt.datetime.strptime(tsp_time,'%Y%m%d_%H%M%S')
	for j in evt_dat_list:
		evt_time = j.split('.')[0]
		evt_time = dt.datetime.strptime(evt_time,'%Y%m%d_%H%M%S')
		tdiff = evt_time - tsp_time
		if abs(tdiff.total_seconds()) < 5:
			new_tsp = j.replace('.dat','.tsp')
			tsp_list[tsp_k] = new_tsp
			tsp_k += 1
			break
today = fdate
sp.call(['cp','../make_t2.sh','.'])
sp.call(['cp','../testtsp','.'])

sp.call(['./make_t2.sh','%s' %today])
big_t2_sec = np.loadtxt('%s.T2' %today,delimiter='.',dtype=int,usecols=(0,))
big_t2_micro = np.loadtxt('%s.T2' %today,delimiter='.',dtype=float,usecols=(1,))
big_t2_micro = big_t2_micro / 1e8

sp.call(['cp','/home/augta/data/coincidence/%i_%02d_%02d.CTAL.gz' %(yr,mo,dy),'.'])
sp.call(['gunzip','%i_%02d_%02d.CTAL.gz' %(yr,mo,dy)])
tal_list = np.loadtxt('%i_%02d_%02d.CTAL'%(yr,mo,dy),usecols=(1,),dtype=str)
evt_counter = 0
denom = 20001
with open('get_events_local.sh','w') as F:
	F.write('#!/bin/bash\n\n')
	for x in tal_list:
		lsec = int(x.split('.')[0])
		micro = float(x.split('.')[1])
		micro = micro / 1e6
		roi = np.where(big_t2_sec == lsec - 1)[0]
		if len(roi) > 0:
			roi_micro = abs(big_t2_micro[roi] - micro)
			ind = roi[roi_micro.argmin()]
			fileind = ind / denom
			ind_final = ind - fileind * denom
			evt_dat_str = tsp_list[fileind][:-3]+'dat'
			F.write('./getevt -i %i -o %02d_local.evt %s\n' %(ind_final,evt_counter,evt_dat_str))
			evt_counter += 1
		else:
			print "**** MISSING T2 DATA FOR GPS SECOND %i" %lsec
			evt_counter += 1
