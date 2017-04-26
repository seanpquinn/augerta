import numpy as np
import os
import sys
import subprocess as sp
import time

def get_tot_th(x):
	"""Takes a list of T2 strings, returns
			num_tot, num_th"""
	tot_count = 0
	th_count = 0
	for y in x:
		testval = y.split(':')
		testval = testval[0][-1]
		if testval == "9":
			tot_count += 1
		elif testval == "1":
			th_count +=1
		else:
			continue
	return tot_count,th_count

fdate = sp.check_output(['date','--date','yesterday','+%Y%m%d'])
fdate = fdate.replace('\n','')
yr = int(fdate[:4])
mo = int(fdate[4:6])
dy = int(fdate[6:])

os.chdir('/home/augta/web_monitor')
file_name = "%i_%02d_%02d.T2.gz" %(yr,mo,dy)
sp.call(['cp','/home/augta/data/south/t2/%s' %file_name,'.'])

if ".T2.gz" in file_name:
	sp.Popen(['gunzip',file_name])
	time.sleep(10) # Decompress takes some time, I guess :X
	with open(file_name.strip('.gz'),'r') as f:
		# Break up into a list of 1s data
		all_data = f.read()
		sec_list = all_data.split('---\n')
	nt2list = np.zeros((len(sec_list),3))
	i = 0
	for t2 in sec_list[:-1]:
		t2list = t2.splitlines()
		nt2 = t2list[0].split(' ')[2]
		nt2list[i,0] = int(nt2)
		nt2list[i,1],nt2list[i,2] = get_tot_th(t2list) #Get types of T2
		i += 1
	date = file_name.split('.')[0]
	with open('T2south_record.txt','a') as f:
		# DATE <TOT+TH> STD(TOT+TH) <TOT> <TH> 
		f.write('%s %.4f %.4f %.4f %.4f\n' %(date,nt2list[:,0].mean(),
			nt2list[:,0].std(),nt2list[:,1].mean(),nt2list[:,2].mean()))
	sp.call(['rm','%s.T2' %date])
else:
	sys.exit()
