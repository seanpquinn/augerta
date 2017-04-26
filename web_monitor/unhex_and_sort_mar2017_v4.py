# Copyright (c) Case Western Reserve University 2017
# This software is distributed under Apache License 2.0
# Consult the file LICENSE.txt
# Author: Sean Quinn spq@case.edu
# Mar 23 2017

import binascii
import bz2
import struct
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import subprocess as sp
import time
import sys
import scipy.signal as spysig

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


def rle(inarray):
        """ run length encoding. Partial credit to R rle function. 
            Multi datatype arrays catered for including non Numpy
            returns: tuple (runlengths, startpositions, values) """
        ia = np.array(inarray)                  # force numpy
        n = len(ia)
        if n == 0: 
            return (None, None, None)
        else:
            y = np.array(ia[1:] != ia[:-1])     # pairwise unequal (string safe)
            i = np.append(np.where(y), n - 1)   # must include last element posi
            z = np.diff(np.append(-1, i))       # run lengths
            p = np.cumsum(np.append(0, z))[:-1] # positions
            return(z, p, ia[i])

def save_calib(bytes):
	f = open('calib_info.txt','w')
	calsize = struct.unpack('>I',bytes[8212:8216])[0]
	if calsize == 0:
		calsize = struct.unpack('>I',bytes[8216:8220])[0]
		if calsize == 84 or calsize == 104:
			f.write('Version {}\n'.format(struct.unpack('>H',bytes[8220:8222])[0]))
			f.write('TubeMask {}\n'.format(struct.unpack('>H',bytes[8222:8224])[0]))
			f.write('StartSecond {}\n'.format(struct.unpack('>I',bytes[8224:8228])[0]))
			f.write('EndSecond {}\n'.format(struct.unpack('>I',bytes[8228:8232])[0]))
			f.write('NbT1 {}\n'.format(struct.unpack('>H',bytes[8232:8234])[0]))
			f.write('NbT2 {}\n'.format(struct.unpack('>H',bytes[8234:8236])[0]))
			evol = [0,0,0] # Last 8 minutes of calibration evolution
			for i in range(3):
				evol[i] = struct.unpack('>H',bytes[8236+2*i:8236+2*(i+1)])[0]
			f.write('Evolution {0} {1} {2}\n'.format(*evol))
			# Finish at 8242
			dynode_base = [0,0,0]
			for i in range(3):
				dynode_base[i] = struct.unpack('>H',bytes[8242+2*i:8242+2*(i+1)])[0]*0.01
			f.write('Dynode Base {0:.3f} {1:.3f} {2:.3f}\n'.format(*dynode_base))
			# Finish at 8248
			anode_base = [0,0,0]
			for i in range(3):
				anode_base[i] = struct.unpack('>H',bytes[8248+2*i:8248+2*(i+1)])[0]*0.01
			f.write('Anode Base {0} {1} {2}\n'.format(*anode_base))
			#Finish at 8254
			dynode_base_var = [0,0,0]
			for i in range(3):
				dynode_base_var[i] = struct.unpack('>H',bytes[8254+2*i:8254+2*(i+1)])[0]*0.01
			f.write('Dynode Base Var {0} {1} {2}\n'.format(*dynode_base_var))
			# Finish at 8260
			anode_base_var = [0,0,0]
			for i in range(3):
				anode_base_var[i] = struct.unpack('>H',bytes[8260+2*i:8260+2*(i+1)])[0]*0.01
			f.write('Anode Base Var {0} {1} {2}\n'.format(*anode_base_var))
			#Finish at 8266
			block = ['VemPeak','Rate','NbTDA','DA','SigmaDA','VemCharge']
			vem_peak = [0,0,0]
			for i in range(3):
				vem_peak[i] = struct.unpack('>H',bytes[8266+2*i:8266+2*(i+1)])[0]*0.1
			f.write('VemPeak ' + '{0} {1} {2}\n'.format(*vem_peak))
			# Finish at 8272
			rate70Hz = [0,0,0]
			for i in range(3):
				rate70Hz[i] = struct.unpack('>H',bytes[8272+2*i:8272+2*(i+1)])[0]*0.01
			f.write('70 Hz Rate ' + '{0} {1} {2}\n'.format(*rate70Hz))
			# Finish at 8278
			trigger_DA = [0,0,0]
			for i in range(3):
				trigger_DA[i] = struct.unpack('>H',bytes[8278+2*i:8278+2*(i+1)])[0]
			f.write('Trigger D/A ' + '{0} {1} {2}\n'.format(*trigger_DA))
			# Finish at 8284
			DA = [0,0,0]
			for i in range(3):
				DA[i] = struct.unpack('>H',bytes[8284+2*i:8284+2*(i+1)])[0]*0.01
			f.write('D/A ' + '{0} {1} {2}\n'.format(*DA))
			# Finish at 8290
			DA_var = [0,0,0]
			for i in range(3):
				DA_var[i] = struct.unpack('>H',bytes[8290+2*i:8290+2*(i+1)])[0]*0.01
			f.write('D/A var ' + '{0} {1} {2}\n'.format(*DA_var))
			# Finish at 8296
			Area = [0,0,0]
			for i in range(3):
				Area[i] = struct.unpack('>H',bytes[8296+2*i:8296+2*(i+1)])[0]*0.1
			f.write('VemCharge ' + '{0} {1} {2}\n'.format(*Area))
			# Finish at 8302
			totRate = struct.unpack('>H',bytes[8302:8304])[0]*0.01
			f.write('TotRate ' + '{0}\n'.format(totRate))
			#Finish at 8304
			f.write('NbTOT {}\n'.format(struct.unpack('>H',bytes[8302:8304])[0]))
			if calsize == 104:
				block = ['DADt','SigmaDADt','DAChi2']
				for i in range(3):
					vals = [0,0,0]
					for j in range(3):
						vals[j]=struct.unpack('>H',bytes[8266+2*(3*i+j):8266+2*(3*i+j+1)])[0]/100.
				f.write(block[i]+' '+'{0} {1} {2}\n'.format(*vals))
		else:
			f.write("BAD COMPRESS\n")
			f.close()
	else:
		f.write("BAD COMPRESS\n")
		f.close()
	f.close()
	return calsize

def save_mon(bytes,si):
	#si is fondly known as start index
	si += 8220
	mon_size = struct.unpack('>I',bytes[si:si+4])[0]
	si += 4
	if mon_size == 6080:
		f = open('mon_hist_offset.txt','w')
		offsets = np.zeros(10,dtype=int)
		for i in range(10):
			val = struct.unpack('>H',bytes[si+2*i:si+2*(i+1)])[0]
			offsets[i] = val
			f.write('{}\n'.format(val))
		si += 2 * 10
		f.close()
# -------------BASELINE HISTOGRAMS-------------
		pmt_base = np.zeros((20,6),dtype=int)
		pmt_base[:,0] = np.arange(offsets[0],offsets[0]+20)
		pmt_base[:,2] = np.arange(offsets[1],offsets[1]+20)
		pmt_base[:,4] = np.arange(offsets[2],offsets[2]+20)
		tmp_labels=['','PMT 1','','PMT 2','','PMT 3']
		for j in [1,3,5]:
			for i in range(20):
				pmt_base[i,j] = struct.unpack('>H',bytes[si+2*i:si+2*(i+1)])[0]
			si += 2*20
			plt.step(pmt_base[:,j-1],pmt_base[:,j],where='pre',label=tmp_labels[j])
		plt.xlabel('FADC channels')
		plt.ylabel('Counts')
		plt.title('Baseline histograms')
		plt.legend()
		plt.savefig('mon_hist_base.png')
		plt.close('all')
		np.savetxt('mon_hist_base.txt',pmt_base,fmt="%i")
# -------------PULSE HEIGHT HISTOGRAMS-------------
		mon_peak = np.zeros((150,6),dtype=int)
		mon_peak[:,0] = np.arange(offsets[3],offsets[3]+150)
		mon_peak[:,2] = np.arange(offsets[4],offsets[4]+150)
		mon_peak[:,4] = np.arange(offsets[5],offsets[5]+150)
		tmp_labels=['','PMT 1','','PMT 2','','PMT 3']
		for j in [1,3,5]:
			for i in range(150):
				mon_peak[i,j] = struct.unpack('>H',bytes[si+2*i:si+2*(i+1)])[0]
			si += 2*150
			lab = tmp_labels[j]
			plt.step(mon_peak[:,j-1],mon_peak[:,j],where='pre',label=lab)
		plt.xlabel('FADC channels')
		plt.ylabel('Counts')
		plt.title('Pulse height histograms')
		plt.legend()
		plt.savefig('mon_hist_pulse_height.png')
		plt.close('all')
		np.savetxt('mon_hist_pulse_height.txt',mon_peak,fmt="%i")
# -------------CHARGE HISTOGRAMS-------------
		mon_charge = np.zeros((600,8),dtype=int)
		mon_charge[:,0] = np.arange(offsets[6],offsets[6]+600)
		mon_charge[:,2] = np.arange(offsets[7],offsets[7]+600)
		mon_charge[:,4] = np.arange(offsets[8],offsets[8]+600)
		mon_charge[:,6] = np.arange(offsets[9],offsets[9]+600)
		tmp_labels=['','PMT 1','','PMT 2','','PMT 3','','PMT SUM']
		for j in [1,3,5,7]:
			for i in range(600):
				mon_charge[i,j] = struct.unpack('>H',bytes[si+2*i:si+2*(i+1)])[0]
			si += 2*600
			lab = tmp_labels[j]
			if j != 7:
				plt.step(mon_charge[:,j-1],mon_charge[:,j],where='pre',label=lab)
		plt.xlabel('FADC channels')
		plt.ylabel('Counts')
		plt.title('Charge histograms')
		plt.legend()
		plt.savefig('mon_hist_charge.png')
		plt.close('all')
		np.savetxt('mon_hist_charge.txt',mon_charge,fmt="%i")
		plt.step(mon_charge[:,6],mon_charge[:,7],where='pre',label=tmp_labels[-1])
		plt.xlabel('FADC channels')
		plt.ylabel('Counts')
		plt.title('Sum charge histogram')
		plt.legend()
		plt.savefig('mon_hist_charge_sum.png')
		plt.close('all')
	# -------------SHAPE HISTOGRAMS-------------
		mon_shape = np.zeros((20,4),dtype=int)
		mon_shape[:,0] = np.arange(0,500,25)
		for j in range(1,4):
			for i in range(20):
				mon_shape[i,j] = struct.unpack('>I',bytes[si+4*i:si+4*(i+1)])[0]
			si += 4*20
			plt.step(mon_shape[:,0],mon_shape[:,j],where='pre',label='PMT %i' %j)
		plt.xlabel('FADC bins [25 ns]')
		plt.ylabel('Counts')
		plt.title('PMT Shape')
		plt.legend()
		plt.savefig('mon_hist_pmt_shape.png')
		plt.close('all')
		np.savetxt('mon_hist_pmt_shape.txt',mon_shape,fmt="%i")
	elif mon_size == 0:
		return 0
	else:
		f = open('BAD_MON_COMPRESS','w')
		f.close()
		return mon_size
	return si

def save_gps(bytes,si):
	gpssize = struct.unpack('>I',bytes[si:si+4])[0]
	si += 4
	block = ['Current100','Next100','Current40','Next40','PreviousST',
				'CurrentST','NextST']
	f = open('gps_info.txt','w')
	for i in range(7):
		val = struct.unpack('>I',bytes[si+4*i:si+4*(i+1)])[0]
		f.write(block[i]+' '+'{}\n'.format(val))
	si += 4*7
	if gpssize == 30:
		val = struct.unpack('>H',bytes[si:si+2])[0]
		f.write('Offset {}'.format(val))
	f.close()

def find_baseline(x,y):
	"""Determine baseline from ADC trace.
Looks at a subsample (0-125) of pretrigger ADC counts.
The bin count with the largest weight is taken as the baseline.
Algorithm is based on GAP2016_044.

Parameters
----------
x,y : array_like
	Dynode and anode channel arrays. Converts to int.

Returns
-------
a,b : array_like
	The baseline values for dynode and anode, respectively

c,d,e,f : scalars
	Start bins for dynode and anode, stop bins for dynode and anode

"""
	dyn = x.astype(int)
	ano = y.astype(int)
	sigma = 2
	#Find high gain baseline pieces
	dyn_b = np.zeros(768)
	#Determine most likely baseline
	binval = np.arange(dyn.min(),dyn.min()+5)
	counts = np.array([len(dyn[dyn==i]) for i in binval])
	likely_base = binval[counts.argmax()]
	for i in range(768):
		if abs(dyn[i] - likely_base) < 2:
			dyn_b[i] = 1
	num_vals,start,val = rle(dyn_b)
	base_i = np.where(val==1)[0]
	num_vals,start=num_vals[base_i],start[base_i]
	n_pieces = len(num_vals)
	for i in range(n_pieces):
		delta = num_vals[i]
		if delta > 10:
			base_mean = dyn[start[i]:start[i]+num_vals[i]].mean()
			dyn_b[start[i]:start[i]+num_vals[i]] = base_mean
		else:
			dyn_b[start[i]:start[i]+num_vals[i]] = 0
	#Interpolate between pieces
	zeros = np.where(dyn_b == 0.)[0]
	logical = np.zeros(768,dtype=bool)
	logical[zeros] = True
	tz = lambda z: z.nonzero()[0]
	#Interp might fail in some situations
	try:
		dyn_b[logical] = np.interp(tz(logical),tz(~logical),dyn_b[~logical])
	except:
		if len(zeros) > 0:
			dyn_b[logical] = dyn_b[760]
	#Signal start search
	dyn2 = dyn-dyn_b
	dyn_start = 150 #Default in case problems
	for i in range(100,768-1):
		w0 = dyn2[i]
		w1 = dyn2[i+1]
		if w0 > 10 and w1 > 10:
			dyn_start = i - 2
			break
	#Signal stop search
	dyn_finish = 350 #Default in case of problems
	#Don't care about spurious muons near end either
	for i in range(767,dyn_start,-1):
		w0 = dyn2[i]
		if w0 > 4 and i < 400:
			dyn_finish = i + 10
			break
	ano_b = np.zeros(768)
	#Determine most likely baseline
	binval = np.arange(ano.min(),ano.min()+5)
	counts = np.array([len(ano[ano==i]) for i in binval])
	likely_base = binval[counts.argmax()]
	for i in range(768):
		if abs(ano[i] - likely_base) < 2:
			ano_b[i] = 1
	num_vals,start,val = rle(ano_b)
	base_i = np.where(val==1)[0]
	num_vals,start=num_vals[base_i],start[base_i]
	n_pieces = len(num_vals)
	for i in range(n_pieces):
		delta = num_vals[i]
		if delta > 10:
			base_mean = ano[start[i]:start[i]+num_vals[i]].mean()
			ano_b[start[i]:start[i]+num_vals[i]] = base_mean
		else:
			ano_b[start[i]:start[i]+num_vals[i]] = 0
	#Interpolate between pieces
	zeros = np.where(ano_b == 0.)[0]
	logical = np.zeros(768,dtype=bool)
	logical[zeros] = True
	tz = lambda z: z.nonzero()[0]
	#Interp might fail in some situations
	try:
		ano_b[logical] = np.interp(tz(logical),tz(~logical),ano_b[~logical])
	except:
		if len(zeros) > 0:
			ano_b[logical] = ano_b[760]
	#Signal start search
	ano2 = ano-ano_b
	ano_start = 150 #Default in case problems
	for i in range(100,768-1):
		w0 = ano2[i]
		w1 = ano2[i+1]
		if w0 > 10 and w1 > 10:
			ano_start = i - 2
			break
	#Signal stop search
	ano_finish = 350 #Default in case of problems
	#Don't care about spurious muons near end either
	for i in range(767,ano_start,-1):
		w0 = ano2[i]
		if w0 > 2 and i < 400:
			ano_finish = i + 10
			break
	if len(np.where(dyn > 1020)[0]) < 2:
		ano_start = dyn_start
		ano_finish = dyn_finish
	return dyn_b,ano_b,dyn_start,ano_start,dyn_finish,ano_finish

def find_vem(p):
	"""Determine peak of the charge histogram for PMT `p`.
Loads mon_hist_charge.txt file for input PMT. The histogram
is smoothed using a 45th order 3rd degree polynomial Savitzky-Golay filter.
The second peak of the smoothed signal is selected.

Parameters
----------
p : int
	PMT number. I.e. 0,1 or 2 for PMT#1,#2,#3

Returns
-------
y : int
	Estimated location of charge histogram peak
"""
	xax,yax = np.loadtxt("mon_hist_charge.txt",usecols=(p*2,2*p+1),dtype=int,unpack=True)
	xax = xax - xax[0]
	Y = spysig.savgol_filter(yax,45,3)
	ped_peak = Y[:60].argmax()
	q_peak = Y[60:].argmax() + 60
	return q_peak,ped_peak

def plot_vem():
	fig = plt.figure(figsize=(16,9))
	for p in range(3):
		xax,yax = np.loadtxt("mon_hist_charge.txt",usecols=(p*2,2*p+1),dtype=int,unpack=True)
		xax = xax - xax[0]
		Y = spysig.savgol_filter(yax,45,3)
		ped_peak = Y[:60].argmax()
		q_peak = Y[60:].argmax() + 60
		ax = fig.add_subplot(1,3,p+1)
		plt.step(xax,yax)
		plt.plot(xax,Y)
		plt.xlabel('FADC channels')
		plt.title('PMT %i charge histogram' %(p+1))
		plt.ylim(ymin=0)
		ymax = plt.ylim()[1]
		plt.vlines(ped_peak,0,ymax)
		plt.vlines(q_peak,0,ymax)
		s='Pedestal peak = %i\nCharge peak=%i' %(ped_peak,q_peak)
		plt.text(0.65,0.75,s,fontsize=10,transform=ax.transAxes)
	plt.tight_layout()
	plt.savefig('hist_charge_fit.png')
	plt.close('all')

def make_plots(evt_num,gps):
	# Get *estimated* offsets from calib data
	a_base = [0,0,0]
	d_base = [0,0,0]
	v_peaks = [0,0,0]
	da = [0,0,0]
	v_charge = [0,0,0]
	with open('calib_info.txt','r') as F:
		for line in F:
			if "Dynode Base" in line and "Var" not in line:
				ss = line.split(' ')
				for j in range(3):
					d_base[j] = float(ss[j+2])
			elif "Anode Base" in line and "Var" not in line:
				ss = line.split(' ')
				for j in range(3):
					a_base[j] = float(ss[j+2])
			elif "VemPeak" in line:
				ss = line.split(' ')
				for j in range(3):
					v_peaks[j] = float(ss[j+1])
			elif "D/A" in line and "var" not in line and "Trigger" not in line:
				ss = line.split(' ')
				for j in range(3):
					da[j] = float(ss[j+1])
			elif "VemCharge" in line:
				ss = line.split(' ')
				for j in range(3):
					v_charge[j] = float(ss[j+1])
			else:
				continue
	fadc_hist = np.loadtxt('FADC_trace',dtype=int)
	xaxis = np.arange(0,768)
	plt.figure(figsize=(19,8))
	for i in range(3):
		plt.subplot(1,3,i+1)
		plt.plot(xaxis,fadc_hist[:,i+1],
						drawstyle='steps-pre')
		plt.title('PMT {}'.format(i+1))
		plt.xlabel(r'Time [25 ns]')
		plt.ylabel('ADC counts')
	plt.tight_layout()
	plt.savefig('dynode_adc.png')
	plt.close()
	plt.figure(figsize=(19,8))
	for i in range(3):
		plt.subplot(1,3,i+1)
		plt.plot(xaxis,fadc_hist[:,i+4],
					drawstyle='steps-pre')
		plt.title('PMT {}'.format(i+1))
		plt.xlabel(r'Time [25 ns]')
		plt.ylabel('ADC counts')
	plt.tight_layout()
	plt.savefig('anode_adc.png')
	plt.close()
	# Make Signal plot
	sga = [0.]*3	
	sgd = [0.]*3
	f,axs = plt.subplots(nrows=2,ncols=3,sharex='col',sharey='row',figsize=(22,14))
	axs[0][0].set_ylabel('ANODE Signal [VEM peak]')
	axs[1][0].set_ylabel('DYNODE Signal [VEM peak]')
	ano_sat = [0]*3
	dyn_sat = [0]*3
	for i in range(3):
		y=np.empty(0) #Anode y-axis
		y2 = np.empty(0) #Dynode y-axis
		#Get ADC traces for anode
		y = fadc_hist[:,i+4]
		max_ano_adc = np.where(y>1020)[0]
		#Get ADC traces for dynode
		y2 = fadc_hist[:,i+1]
		max_dyn_adc = np.where(y2>1020)[0]
		#Determine baseline
		dyn_b,ano_b,d_start,a_start,d_end,a_end = find_baseline(y2,y)
		qvem_peak, pdl_peak = find_vem(i)
		#Calculate signals
		y_sig = y - ano_b
		sga[i] = y_sig[a_start:a_end].sum() / (qvem_peak / 32)
		y2_sig = y2 - dyn_b
		sgd[i] = y2_sig[d_start:d_end].sum() / qvem_peak
		#Put ADC traces into normalized units
		y_peak_in_vem = np.max(y_sig / (qvem_peak / 32))
		y2_peak_in_vem = np.max(y2_sig / qvem_peak)
		y2_max_val = y2_sig.max()
		xnew = xaxis[d_start-10:d_end+20]
		plot_y = y_sig[d_start-10:d_end+20] * y_peak_in_vem / qvem_peak
		plot_y2 = y2_sig[d_start-10:d_end+20] * y2_peak_in_vem / qvem_peak
		#Plot anode
		axs[0][i].step(xnew,plot_y)
		axs[0][i].vlines(a_start,0,1.2*plot_y.max(),linestyle='dashed',color='green')
		axs[0][i].vlines(a_end,0,1.2*plot_y.max(),linestyle='dashed',color='green')
		axs[1][i].step(xnew,plot_y2)
		axs[1][i].vlines(d_start,0,1.2*plot_y2.max(),linestyle='dashed',color='green')
		axs[1][i].vlines(d_end,0,1.2*plot_y2.max(),linestyle='dashed',color='green')
		axs[1][i].set_xlabel(r'Time [25 ns]')
		boxstr = 'S=%.1f VEM\nD/A=%.1f\nVEM Charge=%.1f\nVEM Peak=%.1f' %(sga[i],da[i],v_charge[i],v_peaks[i])
		boxstr2 = 'S=%.1f VEM\nD/A=%.1f\nVEM Charge=%.1f\nVEM Peak=%.1f' %(sgd[i],da[i],v_charge[i],v_peaks[i])
		axs[0][i].text(0.7,0.75,boxstr,fontsize=10,transform=axs[0][i].transAxes)
		axs[1][i].text(0.7,0.75,boxstr2,fontsize=10,transform=axs[1][i].transAxes)
		axs[0][i].set_title('PMT %i' %(i+1))
		axs[0][i].set_xlim(xmin=xnew.min(),xmax=xnew.max())
		axs[1][i].set_xlim(xmin=xnew.min(),xmax=xnew.max())
		if len(max_ano_adc) > 2:
			axs[0][i].text(0.1,0.75,'SATURATED',color='red',fontsize=10,transform=axs[0][i].transAxes)
			ano_sat[i] = 1
		if len(max_dyn_adc) > 2:
			axs[1][i].text(0.1,0.75,'SATURATED',color='red',fontsize=10,transform=axs[1][i].transAxes)
			dyn_sat[i] = 1
	plt.tight_layout()
	plt.savefig('%i_signal.png' %evt_num)
	plt.close('all')
	plot_vem()
	return "%i %.3f %.3f %.3f %.3f %.3f %.3f %i %i %i %i %i %i" %(gps,sga[0],sga[1],sga[2],sgd[0],sgd[1],sgd[2],ano_sat[0],ano_sat[1],ano_sat[2],dyn_sat[0],dyn_sat[1],dyn_sat[2])

#Read through T3 file collecting events into a large list
#Since writing the original script I've found a more elegant approach
#thanks to inspectorG4dget at stackoverflow
#http://stackoverflow.com/questions/18865058/

fdate = sp.check_output(['date','--date','-1 day','+%Y%m%d'])
fdate = fdate.strip()

t3list = []
num_evts = 0
print("Reading T3 event file ...")

yr = int(fdate[:4])
mo = int(fdate[4:6])
dy = int(fdate[6:])

os.chdir('/home/augta/web_monitor/tmp')
fname = "%i_%02d_%02d" %(yr,mo,dy)
sp.call(['cp','/home/augta/data/south/t3/%s.T3.gz' %fname,'.'])

sp.call(['gunzip',"%s.T3.gz" %fname])

filename = "%s.T3" %fname

with open(filename,'r') as t3file:
	copy = False
	for line in t3file:
		if line.strip() == "Event ...":
			copy = True
			data_str = ''
			num_evts += 1
		elif line.strip() == "----------":
			copy = False
			#Avoid clipped data streams. Compressed event should be more than 10kB
			if len(data_str)>9000:
				t3list.append(data_str)
		elif copy:
			data_str += line.strip().replace(' ','')

time.sleep(0.5)
#print("[ OK ]")
#print("Found {} events".format(num_evts))

evt_count = 1
signal_data = []
for t3 in t3list:
	print("Event %i of %i" %(evt_count,len(t3list)))
	evt_id = int(t3[:4],16)
	error_code = int(t3[4:6],16) #Value of 1 indicates no error for T3
	packed=binascii.unhexlify(bytes(t3[8:],'ascii'))    
	dec_t3 = bz2.decompress(packed)
	# Now that we have uncompressed message let's get some information
	# The PowerPC hardware uses big endian format
	gps_YMDHMnS = struct.unpack('>I', dec_t3[:4])[0] #First 4 bytes are GPS sec
	gps_TICK = struct.unpack('>I', dec_t3[4:8])[0] #Next 4 are GPS clock cycles
	try:
		os.mkdir("{0}_{1}".format(evt_id,gps_YMDHMnS))
	except OSError as e:
		#Catch folder already exists error
		if e.errno==17:
			print("This event has already been unpacked and saved, skipping ...")
			continue
	os.chdir('{0}_{1}'.format(evt_id,gps_YMDHMnS))
	f=open('T3_{}.bin'.format(evt_id), 'bw')
	f.write(dec_t3)
	f.close()   
	sp.call(["../../x2", "T3_{}.bin".format(evt_id)])
	monstart = save_calib(dec_t3)
	gpsstart = save_mon(dec_t3,monstart)
	save_gps(dec_t3,gpsstart)
	signal_data.append(make_plots(evt_count,gps_YMDHMnS))
	evt_count += 1
	os.chdir('..')

sp.call(['rm',filename])
dirlist = os.listdir('.')
dirlist.sort()
sp.call(['mkdir','/var/www/html/monitor/data/global_south/%s' %fname])
sp.call(['mkdir','/var/www/html/monitor/data/local_south/%s' %fname])

sp.call(['cp',"/home/augta/data/coincidence/%s.CTAG.gz" %fname,
	'/var/www/html/monitor/data/global_south/%s' %fname])
sp.call(['cp',"/home/augta/data/coincidence/%s.CTAL.gz" %fname,
	'/var/www/html/monitor/data/local_south/%s' %fname])

sp.call(['cp',"/home/augta/data/coincidence/%s.CTAG.gz" %fname,'.'])

global_gps = np.loadtxt('%s.CTAG.gz'%fname,usecols=(6,),dtype='S500',
	comments=None)

sp.call(['rm',"%s.CTAG.gz" %fname])

num_glob = global_gps.size

dirlist_gpsonly = []
for j in dirlist:
	dirlist_gpsonly.append(j.split('_')[1])

# Make list of GPS seconds from signal data list 
signal_data_gpsonly = []
for j in signal_data:
	signal_data_gpsonly.append(j.split(' ')[0])

# Locate and move all global events
#Also, write event data to global text file
if num_glob > 0:
	if num_glob == 1:
		new_glob = np.zeros(1,dtype='S500')
		new_glob[0] = global_gps
		global_gps = new_glob

	for g in global_gps:
		gps_sec = g.decode('ascii').split('.')[0]
		try:#Event might not have associated T3 (sad, but happens rarely it seems)
			fold_ind = dirlist_gpsonly.index(gps_sec)
		except:#Skip to next event
			continue
		d = dirlist[fold_ind]
		sp.call(['mv',d+'/','/var/www/html/monitor/data/global_south/%s/' %fname])
		data_ind = signal_data_gpsonly.index(gps_sec)
		s = signal_data[data_ind]
		with open('/home/augta/web_monitor/south_global_signal.txt','a') as f:
			f.write(s+'\n')

# Get new dirlist which should, in principle, contain only local events
dirlist = os.listdir('.')
dirlist.sort()
dirlist_gpsonly = []
for j in dirlist:
	dirlist_gpsonly.append(j.split('_')[1])

N = len(dirlist)
for i in range(N):
	d = dirlist[i]
	sp.call(['mv',d+'/','/var/www/html/monitor/data/local_south/%s/' %fname])
	gps_sec = dirlist_gpsonly[i]
	data_ind = signal_data_gpsonly.index(gps_sec)
	s = signal_data[data_ind]
	with open('/home/augta/web_monitor/south_local_signal.txt','a') as f:
		f.write(s+'\n')
