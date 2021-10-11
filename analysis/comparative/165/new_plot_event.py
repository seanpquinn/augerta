import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import matplotlib.patches as mpatches

# 0 event_id
# 1 station_id
# 2 energy_mc
# 3 zenith_mc
# 4 r_mc
# 5 scin_tot_pesum
# 6 scin_lg_tot_sig
# 7 scin_lg_tot_nosat_sig
# 8 scin_lg_tot_sat
# 9 scin_hg_tot_sig
# 10 scin_hg_tot_nosat_sig
# 11 scin_hg_tot_sat
# 12 scin_lg_tot_nosat_max
# 13 scin_hg_tot_nosat_max
# 14 scin_em_pesum
# 15 scin_lg_em_sig
# 16 scin_hg_em_sig
# 17 scin_mu_pesum
# 18 scin_lg_mu_sig
# 19 scin_hg_mu_sig
# 20 wcd_tot_pesum
# 21 wcd_lg_tot_sig
# 22 wcd_lg_tot_nosat_sig
# 23 wcd_lg_tot_sat
# 24 wcd_hg_tot_sig
# 25 wcd_hg_tot_nosat_sig
# 26 wcd_hg_tot_sat
# 27 wcd_lg_tot_nosat_max
# 28 wcd_hg_tot_nosat_max
# 29 wcd_em_pesum
# 30 wcd_lg_em_sig
# 31 wcd_hg_em_sig
# 32 wcd_mu_pesum
# 33 wcd_lg_mu_sig
# 34 wcd_hg_mu_sig

def as_unc_core(S,r,theta):
	# Compute Auger variance on signal S core distance r, zenith theta
	#r should be in m
	#theta in deg.
	a = 0.865
	b = 0.593
	c = 0.023
	beta = -2.2
	theta = theta * np.pi / 180.
	avgtheta = 35. * np.pi / 180.
	ab1 = a**2 * (1+b*(1/np.cos(theta)-1/np.cos(avgtheta)))**2
	Sexp = 24.1 * (r/1000.)**beta * ((r+700.)/1700.)**beta
	unc = np.sqrt(ab1 * Sexp + c**2 * S**2)
	return unc

data_file = 'FADC_ALL.txt'

# Load entire DataWriter output
data = np.loadtxt(data_file,dtype='S100')

# Remove headers
header_indices = np.where(data[:,0]=='event_id')[0]
all_ind = np.arange(len(data))
good_ind = np.setdiff1d(all_ind,header_indices)
new_data = data[good_ind]
st_id = new_data[:,1].astype(int)

# Event info
utah_evt_id = 49
auger_evt_id = 102205872600
sim_sta_id = [5083,5047,5048]
auger_sta_id = [145,192,191]
auger_sta_data = [38.3,65.8,46.3,6.8]
zenith = 38.6
rho = [795,844,690]

#Main loop for stations in event
for i in range(len(sim_sta_id)):
	st_index = np.where(st_id==sim_sta_id[i])[0]
	wcd_data = new_data[st_index]
	# Handle saturation: LG if ANY wcd_hg_tot_sat > 0
	if (wcd_data[:,24].astype(float) > 0.).all():
		# Column convention: tot EM MU
		wcd_vem = wcd_data[:,[21,30,33]].astype(float)
		adc_conv = 4735.1 / 32
	if (wcd_data[:,24].astype(float) == 0.).all():
		# Column convention: tot EM MU
		wcd_vem = wcd_data[:,[24,31,34]].astype(float)
		adc_conv = 4735.1
	vem_sig = wcd_vem / adc_conv
	sim_tot_sig = vem_sig[:,0]
	R_E = 1.04
	R_HAD = 1.45
	sig_corr = R_E * vem_sig[:,1] + R_HAD * R_E**0.9 * vem_sig[:,2]
	obs_sig = auger_sta_data[i]
	obs_unc = as_unc_core(obs_sig,rho[i],zenith)
	plt.figure(figsize=(8,7))
	plt.scatter(obs_sig,1,marker='o',color='black',label='Data')
	plt.plot([],[],marker='$[$ \quad $]$',color='black',
		label='Sys. error',ms=18,ls='None')
	plt.plot([],[],marker='$-$',color='black',
		label='Stat. error',ms=18,ls='None')	
	plt.plot(obs_sig-obs_unc,1,marker='$[$',color='black',ms=18)
	plt.plot(obs_sig+obs_unc,1,marker='$]$',color='black',ms=18)
	plt.hist(sim_tot_sig,density=True,label='Uncorr. sim',color='red')
	plt.hist(sig_corr,density=True,label='Corr. sim',color='blue',alpha=0.5)
	sim_unc_sys = as_unc_core(sim_tot_sig,rho[i],zenith)
	sim_unc_sys = sim_unc_sys.mean()
	plt.errorbar(sim_tot_sig.mean(),0.9,xerr=sim_tot_sig.std(),
		marker='o',color='red',alpha=0.5)
	plt.plot(sim_tot_sig.mean()-sim_unc_sys,0.9,marker='$[$',color='red',ms=18)
	plt.plot(sim_tot_sig.mean()+sim_unc_sys,0.9,marker='$]$',color='red',ms=18)
	sig_corr_unc_sys = as_unc_core(sim_tot_sig,rho[i],zenith).mean()
	plt.errorbar(sig_corr.mean(),0.8,xerr=sig_corr.std(),
		marker='o',color='blue')
	plt.plot(sig_corr.mean()-sig_corr_unc_sys,
		0.8,marker='$[$',color='blue',ms=18)
	plt.plot(sig_corr.mean()+sig_corr_unc_sys,
		0.8,marker='$]$',color='blue',ms=18)
	handles, labels = plt.gca().get_legend_handles_labels()
	plt.legend(handles[::-1], labels[::-1],prop={'size':12})
	plt.title('EPOS-LHC, Station %i (%i), $r=%.1f$ [m]' %(auger_sta_id[i],sim_sta_id[i],rho[i]))
	plt.xlabel('S [VEM]')
	plt.ylabel('Normalized probability')
	plt.savefig('%i_plot.png' %auger_sta_id[i])
	plt.show()
