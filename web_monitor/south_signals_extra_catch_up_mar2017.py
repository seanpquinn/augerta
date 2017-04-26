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

# Takes south_local_signal.txt and south_global_signal.txt
# and adds microseconds, UTC time, as well as trigger type,
# in addition to the VEM signals for anode and dynode

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

date_list = ['20161107',
'20161108',
'20161109',
'20161110',
'20161111',
'20161112',
'20161113',
'20161114',
'20161115',
'20161116',
'20161117',
'20161118',
'20161119',
'20161120',
'20161121',
'20161122',
'20161123',
'20161124',
'20161125',
'20161126',
'20161127',
'20161128',
'20161129',
'20161130',
'20161201',
'20161202',
'20161203',
'20161204',
'20161205',
'20161206',
'20161207',
'20161208',
'20161209',
'20161210',
'20161211',
'20161212',
'20161213',
'20161214',
'20161215',
'20161216',
'20161217',
'20161218',
'20161219',
'20161220',
'20161221',
'20161222',
'20161223',
'20161224',
'20161225',
'20161226',
'20161227',
'20161228',
'20161229',
'20161230',
'20161231',
'20170101',
'20170102',
'20170103',
'20170104',
'20170105',
'20170106',
'20170107',
'20170108',
'20170109',
'20170110',
'20170111',
'20170112',
'20170114',
'20170117',
'20170118',
'20170119',
'20170120',
'20170121',
'20170122',
'20170123',
'20170127',
'20170128',
'20170129',
'20170130',
'20170131',
'20170201',
'20170202',
'20170203',
'20170204',
'20170205',
'20170206',
'20170207',
'20170208',
'20170209',
'20170210',
'20170211',
'20170212',
'20170213',
'20170214',
'20170215',
'20170216',
'20170217',
'20170218',
'20170219',
'20170220',
'20170221',
'20170222',
'20170223',
'20170224',
'20170225',
'20170226',
'20170227',
'20170228',
'20170301',
'20170302',
'20170303',
'20170304',
'20170305',
'20170306',
'20170307',
'20170308',
'20170309',
'20170310',
'20170311',
'20170312',
'20170313',
'20170314',
'20170315',
'20170316',
'20170317',
'20170318',
'20170319',
'20170320',
'20170321',
'20170322',
'20170323',]

for date in date_list:

	fdate = date
	yr = int(fdate[:4])
	mo = int(fdate[4:6])
	dy = int(fdate[6:])

	# Array columns: GPS sec, A1, A2, A3, D1, D2, D3
	local_sig = np.loadtxt('/home/augta/web_monitor/south_local_signal.txt',dtype='S500')
	local_coi = np.loadtxt('/home/augta/data/coincidence/%i_%02d_%02d.CTAL.gz' %(yr,mo,dy)
		,usecols=(1,),dtype='S100')

	sp.call(['cp','/home/augta/data/south/t2/%i_%02d_%02d.T2.gz' %(yr,mo,dy),'.'])
	sp.call(['gunzip','%i_%02d_%02d.T2.gz' %(yr,mo,dy)])
	file_name = "%i_%02d_%02d.T2" %(yr,mo,dy)

	with open(file_name,'r') as f:
		all_data = f.read()

	sp.call(['rm',file_name])
	new_slf = '/home/augta/web_monitor/south_local_signal_extra.txt'
	if local_coi.size > 0:
		if local_coi.size == 1:
			tmp = str(local_coi)
			local_coi = []
			local_coi.append(tmp)
		for i in local_coi:
			# Find where GPS second is
			try:
				adi = all_data.index(i.split('.')[0])
			#Time stamp not in file, edit manually
			except:
				print i
				print "Previous second: %i" %gps_int
				continue
			# Get string blob with T2 list
			blob = all_data[adi:adi+1000]
			our_second = blob.split('--\n')[0]
			micro = i.split('.')[1]
			mi = our_second.index('%s' %str(int(micro)))
			ttype = our_second[mi-2]
			# Compute UTC time
			gps_sec_str = i.split('.')[0]
			gps_int = int(gps_sec_str)
			week = gps_int / secsInWeek
			sow = gps_int - week*secsInWeek
			utc = UTCFromGps(week,sow)
			utc_str = "%i-%02d-%02d-%02d:%02d:%02d" %utc
			utc_str = utc_str + '.%06d' %int(micro)
			# Find matching local signal data
			for j in local_sig:
				if gps_sec_str in j[0]:
					vems = j[1:]
					# Now we have everything we need to write to a file
					with open(new_slf,'a') as f:
						out_str = '%s %s %s' %(i,utc_str,ttype)
						out_str += ' %s'*12 %tuple(vems)
						out_str += '\n'
						f.write(out_str)

	global_sig = np.loadtxt('/home/augta/web_monitor/south_global_signal.txt',dtype='S500')
	global_coi = np.loadtxt('/home/augta/data/coincidence/%i_%02d_%02d.CTAG.gz' %(yr,mo,dy),
		usecols=(6,),dtype='S100',comments=None)

	new_sgf = '/home/augta/web_monitor/south_global_signal_extra.txt'
	print global_coi.size
	if global_coi.size > 0:
		if global_coi.size == 1:
			tmp = str(global_coi)
			global_coi = []
			global_coi.append(tmp)
		for i in global_coi:
			# Find where GPS second is
			try:
				adi = all_data.index(i.split('.')[0])
			#Time stamp not in file, edit manually
			except:
				print i
				print "Previous second: %i" %gps_int
				continue
			# Get string blob with T2 list
			blob = all_data[adi:adi+1000]
			our_second = blob.split('--\n')[0]
			micro = i.split('.')[1]
			mi = our_second.index('%s' %str(int(micro)))
			ttype = our_second[mi-2]
			# Compute UTC time
			gps_sec_str = i.split('.')[0]
			gps_int = int(gps_sec_str)
			week = gps_int / secsInWeek
			sow = gps_int - week*secsInWeek
			utc = UTCFromGps(week,sow)
			utc_str = "%i-%02d-%02d-%02d:%02d:%02d" %utc
			utc_str = utc_str + '.%06d' %int(micro)
			# Find matching local signal data
			for j in global_sig:
				if gps_sec_str in j[0]:
					vems = j[1:]
					# Now we have everything we need to write to a file
					with open(new_sgf,'a') as f:
						out_str = '%s %s %s' %(i,utc_str,ttype)
						out_str += ' %s'*12 %tuple(vems)
						out_str += '\n'
						f.write(out_str)