# Copyright (c) Case Western Reserve University 2017
# This software is distributed under Apache License 2.0
# Consult the file LICENSE.txt
# Author: Sean Quinn spq@case.edu
# Feb 20 2017

#PYTHON 2
import os
import numpy as np
import subprocess as sp
import sys
import time
import datetime as dt
import math

secsInWeek = 604800 
secsInDay = 86400 
gpsEpoch = (1980, 1, 6, 0, 0, 0)  # (year, month, day, hh, mm, ss)

def UTCFromGps(gpsWeek, SOW, leapSecs=18):
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

fdate = sp.check_output(['date','--date','-1 day','+%Y%m%d'])
fdate = fdate.replace('\n','')
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
sp.call(['cp','/home/augta/data/north/Events/%s/muon_list.txt' %fdate,'.'])
muon_list = np.loadtxt('muon_list.txt',dtype='S100')
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

used_evt_files = []
with open('get_events_local.sh','w') as F1:
	F1.write('#!/bin/bash\n\n')
	if tal_list.size > 0:
		if tal_list.size == 1:
			new_tal = np.zeros(1,dtype='S500')
			new_tal[0] = tal_list
			tal_list = new_tal
		for x in tal_list:
			lsec = int(x.split('.')[0])
			micro = float(x.split('.')[1])
			micro = micro / 1e6
			roi = np.where(big_t2_sec == lsec)[0]
			if len(roi) > 0:
				roi_micro = abs(big_t2_micro[roi] - micro)
				ind = roi[roi_micro.argmin()]
				fileind = ind / denom
				ind_final = ind - fileind * denom
				# If new data file, must transfer from the LSC
				evt_dat_str = tsp_list[fileind][:-3]+'dat'
				F1.write('./getevt -i %i -o %02d_local.evt %s\n' %(ind_final,evt_counter,evt_dat_str))
				evt_counter += 1
				#Add used file to list. Used to figure out which muons to download
				used_evt_files.append(lsec)
			else:
				print "**** MISSING T2 DATA FOR GPS SECOND %i" %lsec
				evt_counter += 1

sp.call(['cp','/home/augta/data/coincidence/%i_%02d_%02d.CTAG.gz' %(yr,mo,dy),'.'])
sp.call(['gunzip','%i_%02d_%02d.CTAG.gz' %(yr,mo,dy)])
tag_list = np.loadtxt('%i_%02d_%02d.CTAG'%(yr,mo,dy),usecols=(6,),dtype='S500',
	comments=None)
evt_counter = 0
denom = 20001

with open('get_events_global.sh','w') as F1:
	F1.write('#!/bin/bash\n\n')
	if tag_list.size > 0:
		if tag_list.size == 1:
			new_tag = np.zeros(1,dtype='S500')
			new_tag[0] = tag_list
			tag_list = new_tag
		for x in tag_list:
			lsec = int(x.split('.')[0])
			micro = float(x.split('.')[1])
			micro = micro / 1e6
			roi = np.where(big_t2_sec == lsec)[0]
			if len(roi) > 0:
				roi_micro = abs(big_t2_micro[roi] - micro)
				ind = roi[roi_micro.argmin()]
				fileind = ind / denom
				ind_final = ind - fileind * denom
				evt_dat_str = tsp_list[fileind][:-3]+'dat'
				F1.write('./getevt -i %i -o %02d_global.evt %s\n' %(ind_final,evt_counter,evt_dat_str))
				evt_counter += 1
				#Add used file to list. Used to figure out which muons to download
				used_evt_files.append(lsec)
			else:
				print "**** MISSING T2 DATA FOR GPS SECOND %i" %lsec
				evt_counter += 1

# Remove repeats, only need unique values
used_evt_files_set = set(used_evt_files)
used_evt_files = list(used_evt_files_set)

#Now determine the right muon file to get, need to compare time strings
muon_files = []
used_evt_files.sort()
last_file = ''
for j in used_evt_files:
	week = j / secsInWeek
	sow = j - week * secsInWeek
	evt_time = UTCFromGps( week, sow)
	evt_time = "%i-%02d-%02d-%02d:%02d:%02d" %evt_time
	evt_time = dt.datetime.strptime(evt_time,'%Y-%m-%d-%H:%M:%S')
	for k in range(len(muon_list)-1):
		#Test if date is between muon files. If so, grab first file.
		T1 = muon_list[k].split('.')[0]
		T1 = dt.datetime.strptime(T1,'%Y%m%d_%H%M%S')
		T2 = muon_list[k+1].split('.')[0]
		T2 = dt.datetime.strptime(T2,'%Y%m%d_%H%M%S')
		if evt_time > T1 and evt_time < T2:
			last_file = muon_list[k]
		else:
			continue
	if len(last_file) > 0:
		muon_files.append(last_file)

#Create transfer script for that day

#Remove duplicate entries from muon_files
muon_files = list(set(muon_files))
muon_files.sort() 
with open('get_muons_all.sh','w') as F:
	F.write('#!/bin/bash\n\n')
	F.write('username=augertaupload\n')
	F.write('remoteip=129.22.134.40\n\n')
	for j in muon_files:
		line = 'rsync -rt --perms --chmod=Fug=rw,o=r'
		dirstr = ' /data/Muons/%s/%s' %(fdate,j)
		line += dirstr
		dest = ' $username@$remoteip::augerta/north/Muons/%s/\n'%fdate
		line += dest
		#Shell script instructions
		#F.write('EXITFLAG=1\n')
		#F.write('while [ $EXITFLAG -ne 0 ]; do\n')
		F.write(line)
		#F.write('EXITFLAG=$?\n')
		F.write('sleep 2s\n')
		#F.write('done\n')
		#F.write('sleep 1s\n\n')

sp.call(['cp','get_events_global.sh','/home/augta/data/north'])
sp.call(['cp','get_events_local.sh','/home/augta/data/north'])
sp.call(['cp','get_muons_all.sh','/home/augta/data/north'])
# Temp folder cleanup
newlist = os.listdir('/home/augta/web_monitor/tmpevt/t2/')
for x in newlist:
	sp.call(['rm','/home/augta/web_monitor/tmpevt/t2/'+x])
