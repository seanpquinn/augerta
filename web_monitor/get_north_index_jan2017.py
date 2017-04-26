# Copyright (c) Case Western Reserve University 2015
# This software is distributed under Apache License 2.0
# Consult the file LICENSE.txt
# Author: Sean Quinn spq@case.edu
# Dec 14 2016

# PYTHON 2
import os
import numpy as np
import subprocess as sp
import sys
import time
import datetime as dt

fdate = "20161215"
yr = int(fdate[:4])
mo = int(fdate[4:6])
dy = int(fdate[6:])

os.chdir('/home/augta/web_monitor/tmpevt')
# Expected layout in cwd
# tmpevt/
#		t2/	

# Ensure t2/ is clean before proceeding
files_in_t2 = os.listdir('t2/')
if len(files_in_t2) > 0:
  for y in files_in_t2:
    sp.call(['rm','t2/'+y])
else:
  print "Directory empty, no files to remove."

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
old_evt_str = ''
evt_str_counter = 0
with open('upload_local_data.sh','w') as F1, open('get_local_events.sh','w') as F2:
	F1.write('#!/bin/bash\n\n')
	F2.write('#!/bin/bash\n\n')
	F1.write(r"export RSYNC_PASSWORD='B!d86!wR#kL'" + '\n')
	if tal_list.size > 0:
		if tal_list.size == 1:
			new_tal = np.zeros(1,dtype='S500')
			new_tal[0] = tal_list
			tal_list = new_tal
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
				# If new data file, must transfer from the LSC
				evt_dat_str = tsp_list[fileind][:-3]+'dat'
				if evt_dat_str != old_evt_str:
					if evt_str_counter > 0:
						F2.write('rm %s\n' %old_evt_str)
					F1.write('rsync /data/Events/%i%02d%02d/%s lscupload@192.168.3.100::augersbc/\n' %(yr,mo,dy,evt_dat_str))
					evt_str_counter += 1
				F2.write('./getevt -i %i -o %02d_local.evt %s\n' %(ind_final,evt_counter,evt_dat_str))
				evt_counter += 1
				old_evt_str = evt_dat_str
			else:
				print "**** MISSING T2 DATA FOR GPS SECOND %i" %lsec
				evt_counter += 1
	F2.write('rm %s' %evt_dat_str)

sp.call(['cp','/home/augta/data/coincidence/%i_%02d_%02d.CTAG.gz' %(yr,mo,dy),'.'])
sp.call(['gunzip','%i_%02d_%02d.CTAG.gz' %(yr,mo,dy)])
tag_list = np.loadtxt('%i_%02d_%02d.CTAG'%(yr,mo,dy),usecols=(6,),dtype='S500',
	comments=None)
evt_counter = 0
denom = 20001
old_evt_str = ''
evt_str_counter = 0
with open('upload_global_data.sh','w') as F1, open('get_global_events.sh','w') as F2:
	F1.write('#!/bin/bash\n\n')
	F2.write('#!/bin/bash\n\n')
	F1.write(r"export RSYNC_PASSWORD='B!d86!wR#kL'" + '\n')
	if tag_list.size > 0:
		if tag_list.size == 1:
			new_tag = np.zeros(1,dtype='S500')
			new_tag[0] = tag_list
			tag_list = new_tag
		for x in tag_list:
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
				if evt_dat_str != old_evt_str:
					if evt_str_counter > 0:
						F2.write('rm %s\n' %old_evt_str)
					F1.write('rsync /data/Events/%i%02d%02d/%s lscupload@192.168.3.100::augersbc/\n' %(yr,mo,dy,evt_dat_str))
					evt_str_counter += 1
				F2.write('./getevt -i %i -o %02d_global.evt %s\n' %(ind_final,evt_counter,evt_dat_str))
				evt_counter += 1
				old_evt_str = evt_dat_str
			else:
				print "**** MISSING T2 DATA FOR GPS SECOND %i" %lsec
				evt_counter += 1
	F2.write('rm %s' %evt_dat_str)
sp.call(['cp','get_local_events.sh','/home/augta/data/north'])
sp.call(['cp','get_global_events.sh','/home/augta/data/north'])
sp.call(['cp','upload_local_data.sh','/home/augta/data/north'])
sp.call(['cp','upload_global_data.sh','/home/augta/data/north'])
# Temp folder cleanup
newlist = os.listdir('/home/augta/web_monitor/tmpevt/t2/')
for x in newlist:
	sp.call(['rm','/home/augta/web_monitor/tmpevt/t2/'+x])