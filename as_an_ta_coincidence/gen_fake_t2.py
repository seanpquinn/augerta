import numpy as np
import time

# Script that simulates a synchronized Auger North and Auger 
# South T2 list being written to a file

start_time = 1153402261
j = 0

with open('AN_T2.txt','w',0) as f1, open('AS_T2.txt','w',0) as f2:
  while True:
    sec = start_time + j
    num_n = np.random.randint(17,27)
    num_s = np.random.randint(17,27)
    us_n = np.random.randint(0,999999,num_n)
    us_n.sort()
    us_s = np.random.randint(0,999999,num_s)
    us_s.sort()
    for i in range(num_n):
      f1.write('%i.%06d\n' %(sec,us_n[i]))
    for i in range(num_s):
      f2.write('%i.%06d\n' %(sec,us_s[i]))
    j += 1
    time.sleep(1)