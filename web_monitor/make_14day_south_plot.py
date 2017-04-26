import time
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, date2num
import numpy as np
import subprocess as sp

fpath = '/home/augta/web_monitor/recent_t2south.txt'
with open('/home/augta/web_monitor/recent_t2south.txt','w') as f:
	sp.call(['tail','-n','14','/home/augta/web_monitor/T2south_record.txt'],stdout=f)
t2 = np.loadtxt(fpath,usecols=(1,))
t2err = np.loadtxt(fpath,usecols=(2,))
rawdates = np.loadtxt(fpath,usecols=(0,),dtype=np.str)

#For some reason loadtxt puts garbage into the date strings
#rawdates[:] = [x[2:-1] for x in rawdates]
x=np.arange(len(t2))
plt.fill_between(x,t2-t2err,t2+t2err,color='red',alpha=0.1,linewidth=0.)
plt.plot(x,t2,'o--',color='red',fillstyle='none',ms=14)
plt.ylim(ymin=0.)
plt.xticks(x[::2],rawdates[::2],rotation=20,fontsize='large')
plt.yticks(fontsize='large')
plt.ylabel('T2 Rate (TOT+TH) [Hz]',fontsize='large')
plt.tight_layout()
plt.savefig('T2_recent.png',frameon=1)
plt.clf()
