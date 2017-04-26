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
dirlist = os.listdir('/home/augta/data/north/Events/%i%02d%02d/' %(yr,mo,dy))
dirlist = [k for k in dirlist if '.tsp' in k]

t2_counts = np.empty(0)
for tspfile in dirlist:
	tmp = sp.check_output(['/home/augta/web_monitor/testtsp',
	'/home/augta/data/north/Events/%i%02d%02d/%s' %(yr,mo,dy,tspfile)])
	tmp = tmp.split('\n')
	tmp = [int(k.split('.')[0]) for k in tmp if len(k) > 0]
	tmp = [len(list(group)) for key, group in groupby(tmp)]
	t2_counts = np.concatenate((t2_counts,np.array(tmp)),axis=0)

with open('/home/augta/web_monitor/T2north_record.txt','a') as f:
	# DATE <T2> STD(T2)
	f.write('%s %.4f %.4f\n' %(date,t2_counts.mean(),t2_counts.std()))

fpath = '/home/augta/web_monitor/recent_t2north.txt'
with open('/home/augta/web_monitor/recent_t2north.txt','w') as f:
	sp.call(['tail','-n','14','/home/augta/web_monitor/T2north_record.txt'],stdout=f)
t2 = np.loadtxt(fpath,usecols=(1,))
t2err = np.loadtxt(fpath,usecols=(2,))
rawdates = np.loadtxt(fpath,usecols=(0,),dtype=np.str)

x=np.arange(len(t2))
plt.fill_between(x,t2-t2err,t2+t2err,color='red',alpha=0.1,linewidth=0.)
plt.plot(x,t2,'o--',color='red',fillstyle='none',ms=14)
plt.ylim(ymin=0.)
plt.xticks(x[::2],rawdates[::2],rotation=90,fontsize='large')
plt.yticks(fontsize='large')
plt.ylabel('T2 Rate [Hz]',fontsize='large')
plt.tight_layout()
plt.savefig('/var/www/html/monitor/img/T2north_recent.png',frameon=1)
plt.clf()
