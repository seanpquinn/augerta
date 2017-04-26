import time
import datetime
import subprocess as sp
import time
import sys
import os

fdate = sp.check_output(['date','--date','yesterday','+%Y%m%d'])
fdate = fdate.replace('\n','')
yr = int(fdate[:4])
mo = int(fdate[4:6])
dy = int(fdate[6:])
gdrive_exe = '/home/augta/google_drive/gdrive-linux-x64'

# Uploads
# Auger south files
t2path = '/home/augta/data/south/t2/'
t2file = t2path + '%i_%02d_%02d.T2.gz' %(yr,mo,dy)
t3path = '/home/augta/data/south/t3/'
t3file = t3path + '%i_%02d_%02d.T3.gz' %(yr,mo,dy)
remote_t2path = '0B7u8ES9AANJLcHFvMVVqY21aTGM'
remote_t3path = '0B7u8ES9AANJLTXY5aUJuTEUwdms'
sp.call([gdrive_exe,'upload','-r','-p',remote_t2path,t2file])
time.sleep(10)
sp.call([gdrive_exe,'upload','-r','-p',remote_t3path,t3file])
time.sleep(10)

# TA files
tapath = '/home/augta/data/ta/'
talfile = tapath + '%i_%02d_%02d.TAL.gz' %(yr,mo,dy)
tagfile = tapath + '%i_%02d_%02d.TAG.gz' %(yr,mo,dy)
remote_tapath = '0B7u8ES9AANJLNFh0bExPMHJKRmM'
sp.call([gdrive_exe,'upload','-r','-p',remote_tapath,talfile])
time.sleep(10)
sp.call([gdrive_exe,'upload','-r','-p',remote_tapath,tagfile])
time.sleep(10)

# Coincidence files
cnpath = '/home/augta/data/coincidence/'
ctagfile = cnpath + '%i_%02d_%02d.CTAG.gz' %(yr,mo,dy)
ctalfile = cnpath + '%i_%02d_%02d.CTAL.gz' %(yr,mo,dy)
remote_cnpath = '0B7u8ES9AANJLVU5VaXhqeVhyLU0'
sp.call([gdrive_exe,'upload','-r','-p',remote_cnpath,ctagfile])
time.sleep(10)
sp.call([gdrive_exe,'upload','-r','-p',remote_cnpath,ctalfile])
# Auger north files (litte more complicated)
