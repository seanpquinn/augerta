import time
import math
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
from sklearn.neighbors import KernelDensity
from sklearn.grid_search import GridSearchCV

fdate = sp.check_output(['date','--date','-1 day','+%Y%m%d'])
fdate = fdate.replace('\n','')
yr = int(fdate[:4])
mo = int(fdate[4:6])
dy = int(fdate[6:])

secsInWeek = 604800 
secsInDay = 86400 
gpsEpoch = (1980, 1, 6, 0, 0, 0)  # (year, month, day, hh, mm, ss)

#*****NOTICE*****: LEAPSEC MUST BE CHANGED TO 18 ON JAN 1 2017
def gpsFromUTC(year, month, day, hour, minute, sec, leapSecs=18): 
	"""converts UTC to GPS second

	Original function can be found at: http://software.ligo.org/docs/glue/frames.html

	GPS time is basically measured in (atomic) seconds since  
	January 6, 1980, 00:00:00.0  (the GPS Epoch) 

	The GPS week starts on Saturday midnight (Sunday morning), and runs 
	for 604800 seconds.  

	Currently, GPS time is 17 seconds ahead of UTC
	While GPS SVs transmit this difference and the date when another leap 
	second takes effect, the use of leap seconds cannot be predicted.  This 
	routine is precise until the next leap second is introduced and has to be 
	updated after that.

	SOW = Seconds of Week 
	SOD = Seconds of Day 

	Note:  Python represents time in integer seconds, fractions are lost!!! 
	""" 
	secFract = sec % 1 
	epochTuple = gpsEpoch + (-1, -1, 0) 
	t0 = time.mktime(epochTuple) 
	t = time.mktime((year, month, day, hour, minute, sec, -1, -1, 0))  
	# Note: time.mktime strictly works in localtime and to yield UTC, it should be 
	#       corrected with time.timezone 
	#       However, since we use the difference, this correction is unnecessary. 
	# Warning:  trouble if daylight savings flag is set to -1 or 1 !!! 
	t = t + leapSecs
	tdiff = t - t0
	gpsSOW = (tdiff % secsInWeek)  + secFract
	gpsWeek = int(math.floor(tdiff/secsInWeek))
	gpsDay = int(math.floor(gpsSOW/secsInDay))
	gpsSOD = (gpsSOW % secsInDay)
	gps_tuple = (gpsWeek, gpsSOW, gpsDay, gpsSOD)
	return int(gps_tuple[0] * secsInWeek + gps_tuple[1])

def get_calib(evt_utc_time,mu_list):
	#Convert event utc time stamp to datetime
	evt_ds = datetime.datetime.strptime(evt_utc_time,'%Y/%m/%d_%H:%M:%S')
	evt_gps = gpsFromUTC(evt_ds.year,evt_ds.month,evt_ds.day,evt_ds.hour,
		evt_ds.minute,evt_ds.second)
	#A30 base line
	a30_bl = 512
	mu_file = ''
	for i in range(len(mu_list)-1):
		mu_ds_t1 = datetime.datetime.strptime(mu_list[i].split('.')[0],'%Y%m%d_%H%M%S')
		mu_ds_t2 = datetime.datetime.strptime(mu_list[i+1].split('.')[0],'%Y%m%d_%H%M%S')
		if evt_ds > mu_ds_t1 and evt_ds < mu_ds_t2:
			mu_file = mu_list[i]
			mu_gps_start = mu_ds_t1
		elif i == len(mu_list)-2 and evt_ds > mu_ds_t2:
			mu_file = mu_list[i+1]
			mu_gps_start = mu_ds_t2
		else:
			continue
	if len(mu_file) > 0:	
		mu_ds_t1 = mu_gps_start
		mu_gps = gpsFromUTC(mu_ds_t1.year,mu_ds_t1.month,mu_ds_t1.day,mu_ds_t1.hour,
			mu_ds_t1.minute,mu_ds_t1.second)
		start_index = (evt_gps - mu_gps) - 60
		mu_full_path = '/home/augta/data/north/Muons/%s/'%fdate+mu_file
		out_file = '/home/augta/web_monitor/tmp/muon_tmp.txt'
		sp.call(['./anamu','-i','%s' %mu_full_path,'-o','%s' %out_file,
			'--first','%i' %start_index,'--last','%i' %(start_index + 60)])
		mu_data = np.loadtxt(out_file,usecols=(1,))
		#Construct pulse height and charge histograms
		peaks = np.zeros(3840)
		charge = np.zeros(3840)
		for i in range(3840):
			tmp_trace = mu_data[i*63:(i+1)*63] - 511.5
			peak_loc = tmp_trace.argmax()
			peaks[i] = peak_loc + 1
			charge[i] = tmp_trace.sum()
	return charge,peaks

fname = "%i%02d%02d" %(yr,mo,dy)
os.chdir('/home/augta/web_monitor')
muon_dir = '/home/augta/data/north/Muons/%s/' %fname
muon_list = os.listdir(muon_dir)
muon_list.sort()

evt_list = os.listdir('/home/augta/data/north/Events/%s/' %fname)
evt_list = [k for k in evt_list if '.evt' in k]
glob_evt_list = [k for k in evt_list if 'global' in k]
glob_evt_list.sort()
local_evt_list = [k for k in evt_list if 'local' in k]
local_evt_list.sort()

nloc_dir = '/var/www/html/monitor/data/local_north/%s/' %fname
nglob_dir = '/var/www/html/monitor/data/global_north/%s/' %fname
sp.call(['mkdir',nloc_dir])
sp.call(['mkdir',nglob_dir])

bl_evt = 514
if len(local_evt_list) > 0:
	for m in local_evt_list:
		curr_file = '/home/augta/data/north/Events/%s/%s' %(fname,m)
		fout = nloc_dir + m[:-4] + '.txt'
		with open(fout,'w') as f:
			sp.call(['./testevt',curr_file],stdout=f)
		with open(fout,'r') as f:
			gps_line = f.readline() # Get GPS information
			gps_ts = gps_line.split(' ')[-2].replace(',','') # Select time stamp
			utc_line = f.readline()
			utc_date = utc_line.split(' ')[-2]
			utc_time = utc_line.split(' ')[-1].split('.')[0]
		utc = utc_date+'_'+utc_time
		vem_charge,vem_peak = get_calib(utc,muon_list)
		plt.subplot(121)
		plt.hist(vem_peak,bins=np.arange(0,50),histtype='step')
		xx,yy = np.histogram(vem_peak,np.arange(0,50))
		vem_pulse_peak = xx.argmax() + 1
		plt.xlabel('ADC counts')
		plt.title('A30 Pulse height')
		plt.subplot(122)
		grid=GridSearchCV(KernelDensity(),{'bandwidth': np.linspace(5,80,30)},cv=10,n_jobs=2)
		grid.fit(vem_charge[:,None])
		kde=grid.best_estimator_
		best_bw=grid.best_params_['bandwidth']
		xgrid=np.linspace(0,vem_charge.max(),700)
		pdf=np.exp(kde.score_samples(xgrid[:,None]))
		plt.hist(vem_charge,bins=50,histtype='stepfilled',fc='gray',alpha=0.2,normed=True)
		peak_pdf = pdf.argmax()
		vem_charge_peak = xgrid[peak_pdf]
		plt.plot(xgrid,pdf)
		plt.vlines(vem_charge_peak,plt.ylim()[0],plt.ylim()[1])
		plt.xlim(xmax=1000) #No need to go beyond 500 for current HV
		plt.title('A30 Charge')
		plt.tight_layout()
		plt.savefig(nloc_dir+'calib_histogram_%s.png' %m[:-4])
		data = np.loadtxt(fout,usecols=(4,),skiprows=3)
		adc = data - bl_evt
		ymax = adc.argmax()
		signal = np.sum(adc[ymax-40:ymax+50]) / (vem_charge_peak / 30)
		adc = adc / vem_charge_peak * (vem_pulse_peak+1)
		x = np.arange(1024)
		plt.step(x,adc)
		plt.xlim(ymax-40,ymax+50)
		plt.xlabel('Time [10 ns]')
		plt.ylabel('Signal [VEM Peak]')
		plt.title('Signal: %.3f VEM' %signal)
		plt.savefig(nloc_dir + '%s_trace.png' %m[:-4])
		plt.close('all')
		locindex = m.split('_')[0]
		np.savetxt(nloc_dir+'%s_pulse_height_hist.txt' %m[:-4],vem_peak)
		np.savetxt(nloc_dir+'%s_charge_hist.txt' %m[:-4],vem_charge)
		with open(nloc_dir + 'signal.txt','a') as f:
			f.write('%s %s %.3f %.3f %.3f\n' %(locindex,gps_ts,signal,vem_charge_peak,vem_pulse_peak))
		with open('north_local_signal.txt','a') as f:
			f.write('%s %.3f\n' %(gps_ts,signal))

if len(glob_evt_list) > 0:
	for m in glob_evt_list:
		curr_file = '/home/augta/data/north/Events/%s/%s' %(fname,m)
		fout = nglob_dir + m[:-4] + '.txt'
		with open(fout,'w') as f:
			sp.call(['./testevt',curr_file],stdout=f)
		with open(fout,'r') as f:
			gps_line = f.readline() # Get GPS information
			gps_ts = gps_line.split(' ')[-2].replace(',','') # Select time stamp
			utc_line = f.readline()
			utc_date = utc_line.split(' ')[-2]
			utc_time = utc_line.split(' ')[-1].split('.')[0]
		utc = utc_date+'_'+utc_time
		vem_charge,vem_peak = get_calib(utc,muon_list)
		plt.subplot(121)
		plt.hist(vem_peak,bins=np.arange(0,50),histtype='step')
		xx,yy = np.histogram(vem_peak,np.arange(0,50))
		vem_pulse_peak = xx.argmax() + 1
		plt.xlabel('ADC counts')
		plt.title('A30 Pulse height')
		plt.subplot(122)
		grid=GridSearchCV(KernelDensity(),{'bandwidth': np.linspace(5,80,30)},cv=10,n_jobs=2)
		grid.fit(vem_charge[:,None])
		kde=grid.best_estimator_
		best_bw=grid.best_params_['bandwidth']
		xgrid=np.linspace(0,vem_charge.max(),700)
		pdf=np.exp(kde.score_samples(xgrid[:,None]))
		plt.hist(vem_charge,bins=50,histtype='stepfilled',fc='gray',alpha=0.2,normed=True)
		peak_pdf = pdf.argmax()
		vem_charge_peak = xgrid[peak_pdf]
		plt.plot(xgrid,pdf)
		plt.vlines(vem_charge_peak,plt.ylim()[0],plt.ylim()[1])
		plt.title('A30 Charge')
		plt.xlim(xmax=1000)
		plt.tight_layout()
		plt.savefig(nglob_dir+'calib_histogram_%s.png' %m[:-4])
		plt.close('all')
		data = np.loadtxt(fout,usecols=(4,),skiprows=3)
		adc = data - bl_evt
		ymax = adc.argmax()
		signal = np.sum(adc[ymax-40:ymax+50])/(vem_charge_peak / 30)
		adc = adc / vem_charge_peak * (vem_pulse_peak+1)
		x = np.arange(1024)
		plt.step(x,adc)
		plt.xlim(ymax-40,ymax+50)
		plt.xlabel('Time [10 ns]')
		plt.ylabel('Signal [VEM Peak]')
		plt.title('Signal: %.3f VEM' %signal)
		plt.savefig(nglob_dir + '%s_trace.png' %m[:-4])
		plt.close('all')
		locindex = m.split('_')[0]
		np.savetxt(nglob_dir+'%s_pulse_height_hist.txt' %m[:-4],vem_peak)
		np.savetxt(nglob_dir+'%s_charge_hist.txt' %m[:-4],vem_charge)
		with open(nglob_dir + 'signal.txt','a') as f:
			f.write('%s %s %.3f %.3f %.3f\n' %(locindex,gps_ts,signal,vem_charge_peak,vem_pulse_peak))
		with open('north_global_signal.txt','a') as f:
			f.write('%s %.3f\n' %(gps_ts,signal))