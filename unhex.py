# Copyright (c) Case Western Reserve University 2015
# This software is distributed under Apache License 2.0
# Consult the file LICENSE.txt
# Author: Sean Quinn spq@case.edu
# June 14 2015

import binascii
import bz2
import struct
import os
import matplotlib.pyplot as plt
import numpy
import subprocess

"""Small Python3 script that parses the master T3.out list. The file contains 
all the relevant T3 data: Event ID, GPS time, Trigger type, and FADC traces for the
3 PMTs. Ricardo Sato has written a program "x2" which recovers the trace data
only from a decompressed T3 message. This script performs the following function
1.) Isolates individual events in the master list
2.) Converts ASCII hex data to raw binary
2.) Decompresses (bz2 format) T3 data message (still raw binary)
3.) Creates a folder for individual events with following name format
    GPSTIME_MICROSECOND
    Example: 1117640005_616863
4.) Places output of x2 program, which is an ASCII text file containing the
    PMT traces (presumably mV levels for dynode/anode?)
"""

def save_calib(bytes):
    f = open('calib_info','w')
    cal_vals = ['cal_size','ver','tube_mask','gps_start','gps_end','NT1','NT2','Evo1',
                'Evo2','Evo3','Base1A','Base1D','Base2A','Base2D','Base3A','Base3D',
                'VEM1Peak','VEM2Peak','VEM3Peak','Rate1','Rate2','Rate3','NTDA1',
                'NTDA2','NDTA3','DA1','DA2','DA3','SigDA1','SigDA2','SigDA3',
                'VemCharge1','VemCharge2','VemCharge3','NToT','DADt1','DADt2','DADt3',
                'SigmaDADt1','SigmaDADt2','SigmaDADt3','DAChi2_1','DAChi2_2','DAChi2_3']
    f.writelines(cal_vals[0]+': '+'%i\n' %int(struct.unpack('>I',bytes[-6226:-6222])[0]))
    f.writelines(cal_vals[1]+': '+'%i\n' %int(struct.unpack('>h',bytes[-6222:-6220])[0]))
    f.writelines(cal_vals[2]+': '+'%i\n' %int(struct.unpack('>h',bytes[-6220:-6218])[0]))
    f.writelines(cal_vals[3]+': '+'%i\n' %int(struct.unpack('>I',bytes[-6218:-6214])[0]))
    f.writelines(cal_vals[4]+': '+'%i\n' %(int(struct.unpack('>I',bytes[-6218:-6214])[0])+1))
    for i in range(39):
        f.writelines(cal_vals[i+5]+': '+'%i\n' %int(struct.unpack('>h',bytes[-6210+2*i:-6210+2*(i+1)])[0]))
    f.close()

def save_mon(bytes):
    mon_size = int(struct.unpack('>I',bytes[-6118:-6114])[0])
    if mon_size == 6080:
        offset=[]
        for i in range(-6114,-6114+20,2): 
            offset.append(int(struct.unpack('>h',bytes[i:i+2])[0]))
        numpy.savetxt('mon_histo_offset',offset,fmt='%i')
        i_next = i+2
        base = numpy.zeros((20,3))
        pmt_num = 0
        for j in range(i_next,i_next+120,40):
            data_index = 0
            for i in range(j,j+40,2):
                base[data_index,pmt_num] = int(struct.unpack('>h',bytes[i:i+2])[0])    
                data_index+=1
            pmt_num+=1
        numpy.savetxt('mon_histo_base',base,fmt='%i %i %i')
        i_next = i + 2
        peak = numpy.zeros((150,3))
        pmt_num = 0
        for j in range(i_next,i_next+900,300):
            data_index = 0
            for i in range(j,j+300,2):
                peak[data_index,pmt_num] = int(struct.unpack('>h',bytes[i:i+2])[0])    
                data_index+=1
            plt.plot(peak[:,pmt_num], drawstyle='steps',label='%i'%(pmt_num+1))
            pmt_num+=1
        plt.legend()
        plt.savefig('peak.pdf')
        plt.clf()
        numpy.savetxt('mon_histo_peak',peak,fmt='%i %i %i')
        i_next = i + 2
        charge = numpy.zeros((600,4))
        pmt_num = 0
        for j in range(i_next,i_next+4800,1200):
            data_index = 0
            for i in range(j,j+1200,2):
                charge[data_index,pmt_num] = int(struct.unpack('>h',bytes[i:i+2])[0])    
                data_index+=1
            plt.plot(charge[:,pmt_num], drawstyle='steps',label='%i'%(pmt_num+1))
            pmt_num+=1
        numpy.savetxt('mon_histo_charge',charge,fmt='%i %i %i %i')
        plt.legend()
        plt.savefig('charge.pdf')
        plt.clf()
        i_next = i + 2
        shape = numpy.zeros((20,3))
        pmt_num = 0
        for j in range(i_next,i_next+240,80):
            data_index = 0
            for i in range(j,j+80,4):
                shape[data_index,pmt_num] = int(struct.unpack('>I',bytes[i:i+4])[0])    
                data_index+=1
            plt.plot(shape[:,pmt_num], drawstyle='steps',label='%i'%(pmt_num+1))
            pmt_num+=1
        plt.legend()
        plt.savefig('shape.pdf')
        plt.clf()
        numpy.savetxt('mon_histo_shape',shape,fmt='%i %i %i')

f = open('T3.out','r')
t3list = []

data_str=''
t3list=[]
old_line=''

for line in f:
    if len(line)!= 30 and len(old_line)!=30:
        if len(data_str)>0:
            t3list.append(data_str)
        data_str = ''
        continue
    else:
        s1 = line.replace(' ','')
        s2 = s1.replace('\n','')
        data_str+=s2
    old_line = line

f.close()
   
for t3 in t3list:
    evt_id = int(t3[:4],16)
    error_code = int(t3[4:8],16) #Hopefully decimal value of 256
    packed=binascii.unhexlify(bytes(t3[8:],'ascii'))    
    dec_t3 = bz2.decompress(packed)
    # Now that we have uncompressed message let's get some information
    # The PowerPC hardware uses big endian format
    gps_YMDHMnS = struct.unpack('>I', packed[:4]) # First 4 bytes are GPS time
    gps_MICRO = struct.unpack('>I', packed[4:8]) # Next 4 bytes are GPS microsecond
    try:
        os.mkdir('%i_%i_%i' %(evt_id,int(gps_YMDHMnS[0]),int(gps_MICRO[0])))
    except OSError as e:
        #Catch folder already exists error
        if e.errno==17:
            print("This event has already been unpacked and saved, skipping ...")
            continue
    os.chdir('%i_%i_%i' %(evt_id,int(gps_YMDHMnS[0]),int(gps_MICRO[0])))
    f=open('T3_%i.bin' %evt_id, 'bw')
    f.write(dec_t3)
    f.close()   
    subprocess.call(["../x2", "T3_%i.bin" %evt_id])
    save_calib(dec_t3)
    save_mon(dec_t3)
    os.chdir('..')
