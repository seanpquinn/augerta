import numpy as np
import time

# Script that simulates a synchronized Auger North and Auger 
# South T2 list being written to a file

start_time = 1153402261
j = 0

with open('TA_GLOBAL.txt','w',0) as f1:
  while True:
    sec = start_time + j
    trig_dec = np.random.randint(0,100)
    if trig_dec <= 20:
      us = np.random.randint(0,999999)
      f1.write('%i.%06d\n' %(sec,us))
    j += 1
    time.sleep(1)
