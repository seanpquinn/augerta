import mpmath as mpm #Available on Ubuntu repos
import time
import subprocess as sp

# Set decimal precision for mpm
mpm.mp.dps = 22 # mpm numbers will be 22*3.333 bit

# Auger trigger decision is based on the TA Global trigger (TAGT) time stamp
# Auger T2s are stored in memory. When a TAGT time stamp is written
# to a file then search the Auger T2 ring buffers for a coincidence within 8 us
# If |AS_T2 - TAGT| < 8 us and |AN_T2 - TAGT| < 8 us then send
# a T3 request to both stations using the respective time stamp
# that satisfied the condition


#--------------------------USER DEFINED PARAMETERS------------------------------------
south_file = 'AS_T2.txt'
north_file = 'AN_T2.txt'
ta_file = 'TA_GLOBAL.txt'
logfile = 'clf_coincidence.log'
NT2 = 70 #INTEGER ONLY

#-------------------------------MAIN PROGRAM------------------------------------------

with open(logfile,'a',0) as f:
  time_now = time.gmtime()
  stime_now = time.strftime("%Y-%m-%d %H:%M:%S", time_now)
  f.write("\n%s   NEW RUN\n" %stime_now)

# Initialize global trigger variable
TAG_old = ''

# Main loop
while True:
# Probably a number of ways to do this next part
# My approach is to read the last entry in the global trigger file
# this is polled every 250ms and stored in memory
# if the value is the same as last iteration, do nothing.
  tail_call = sp.Popen(['tail','-n','1',ta_file],stdout=sp.PIPE,stderr=sp.PIPE)
  TAG_new, err = tail_call.communicate()
  if len(err) > 0:
    with open(logfile,'a',0) as f:
      time_now = time.gmtime()
      stime_now = time.strftime("%Y-%m-%d %H:%M:%S", time_now)
      f.write("\n%s   Error reading file, exiting program\n" %stime_now)
      f.write("%s   %s\n" %(stime_now,err))
    break
  elif len(TAG_new) == 0:
    with open(logfile,'a',0) as f:
      time_now = time.gmtime()
      stime_now = time.strftime("%Y-%m-%d %H:%M:%S", time_now)
      f.write("%s   Got empty string, waiting for more data ...\n" %stime_now)
    time.sleep(0.5)
  elif TAG_new == TAG_old:
    time.sleep(0.25)
    continue
  else:
    # New global trigger. Wait 1.5 seconds, load AN and AS T2s
    # and perform coincidence check
    TAG_old = TAG_new
    TAG_new = TAG_new.replace('\n','')
    TAG_float = mpm.mpf(TAG_new)
    time.sleep(1.5)
    tail_call = sp.Popen(['tail','-n','%i'%NT2,south_file],stdout=sp.PIPE,stderr=sp.PIPE)
    AS,err = tail_call.communicate()
    if len(err) > 0:
      with open(logfile,'a',0) as f:
        time_now = time.gmtime()
        stime_now = time.strftime("%Y-%m-%d %H:%M:%S", time_now)
        f.write("%s   Error reading Auger SOUTH T2 file, exiting program\n" %stime_now)
        f.write("%s   %s\n" %(stime_now,err))
      break
    AS = AS.split('\n')[:-1]
    tail_call = sp.Popen(['tail','-n','%i'%NT2,north_file],stdout=sp.PIPE,stderr=sp.PIPE)
    AN,err = tail_call.communicate()
    if len(err) > 0:
      with open(logfile,'a',0) as f:
        time_now = time.gmtime()
        stime_now = time.strftime("%Y-%m-%d %H:%M:%S", time_now)
        f.write("%s   Error reading Auger NORTH T2 file, exiting program\n" %stime_now)
        f.write("%s   %s\n" %(stime_now,err))
      break
    AN = AN.split('\n')[:-1]
    TAG_float = mpm.mpf(TAG_new)
    as_diff = [0] * NT2
    an_diff = [0] * NT2
    for i in range(NT2):
      as_diff[i] = abs(float(mpm.mpf(AS[i])-TAG_float))
      an_diff[i] = abs(float(mpm.mpf(AN[i])-TAG_float))
    # AS + AN + TAG coincidence test
    as_candidate = [j for j in range(NT2) if as_diff[j] < 8e-6]
    an_candidate = [j for j in range(NT2) if an_diff[j] < 8e-6]
    if len(as_candidate) > 0 and len(an_candidate) > 0:
      # Coincidence found, uses first occurence only
      AS_T2 = AS[as_candidate[0]]
      AN_T2 = AN[an_candidate[0]]
      with open(logfile,'a',0) as f:
        time_now = time.gmtime()
        stime_now = time.strftime("%Y-%m-%d %H:%M:%S", time_now)
        f.write("%s   AN+AS+TA coincidence found!\n" %stime_now)
        f.write("%s   %s %s %s\n" %(stime_now,AS_T2,AN_T2,TAG_new))
      time.sleep(0.2)
    else:
      time.sleep(0.2)
      continue
