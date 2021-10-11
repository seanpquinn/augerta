import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import mplhep as hep
plt.style.use(hep.style.CMS)
from matplotlib.gridspec import GridSpec
import matplotlib.patches as mpatches

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

def ta_unc(S):
  return np.sqrt(S)

# Observed data file format
#0   1    2      3       4        5    6    7    8    9    10        11           12         13            14        15           16         17            18        19
#ID TA_E TA_ZEN TA_EAST TA_NORTH MIP0 MIP1 VEM0 VEM1 VEM2 UMQGS_AVG UMQGS_UC_STD UMEPOS_AVG UMEPOS_UC_STD CMQGS_AVG CMQGS_UC_STD CMEPOS_AVG CMEPOS_UC_STD AS_RHO_MC TA_RHO_MC
obs_data_nparray = np.loadtxt("obs_data.txt", skiprows=1)
num_evts = len(obs_data_nparray)

# Simulation file format
#output format by column number
# 0 sta_id
# 1 cal_tot_ssd_sig
# 2 cal_em_ssd_sig
# 3 cal_mu_ssd_sig
# 4 cal_tot_wcd_sig
# 5 cal_em_wcd_sig
# 6 cal_mu_wcd_sig

# Folder with Offline sims
offline_sims_path = "offline_wcd_ssd_sim"
offline_sims_file_prefix = "CAL_CLF_DataWriter"
# Folder with Adeilaide TASD Offline sims
adelaide_sims_path = "adelaide_tasd_sim"
adelaide_sims_file_suffix = "_adelaide_tasd_sig_mev.txt"
# Folder with first analysis Offline sims
first_offline_sims_path = "first_analysis_data"
first_offline_sims_prefix = "CAL_CLF_"
first_offline_sims_suffix = "_DataWriterTest.dat"

# Adelaide TASD calibration
adelaide_tasd_mev_mip = 2.5

#Main loop for stations in event

# AS_ii=np.where(id==5048)[0]
# TA_ii=np.where(id==5040)[0]

for i, x in enumerate(obs_data_nparray):
  sta_id = str(int(x[0]))
  obs_wcd = x[7:10].mean()
  wcd_rho_mc = x[18]
  wcd_theta_obs = x[2]
  obs_wcd_unc = as_unc_core(obs_wcd, wcd_rho_mc, wcd_theta_obs)
  obs_tasd = x[5:7].mean()
  obs_tasd_unc = ta_unc(obs_tasd)
  sim_wcd_ssd_fname = offline_sims_path + "/" + offline_sims_file_prefix + "%s.txt" %sta_id
  try:
    sim_wcd_ssd = np.loadtxt(sim_wcd_ssd_fname)
  except:
    continue
  wcd_i = np.where(sim_wcd_ssd[:,0] == 5048)[0]
  ssd_i = np.where(sim_wcd_ssd[:,0] == 5040)[0]
  R_E = 1.09
  R_HAD = 1.59
  sim_wcd_corr_mu = R_E * sim_wcd_ssd[wcd_i,5] + R_HAD * R_E**0.9 * sim_wcd_ssd[wcd_i,6]
  sim_ssd_corr_mu = R_E * sim_wcd_ssd[ssd_i,2] + R_HAD * R_E**0.9 * sim_wcd_ssd[ssd_i,3]
  # Scale SSD by effective TA area
  sim_ssd_corr_mu_scaled = sim_ssd_corr_mu * 0.78
  adelaide_fname = adelaide_sims_path + "/" + "%s" %sta_id + adelaide_sims_file_suffix
  adelaide_data = np.loadtxt(adelaide_fname)
  tasd_i = np.where(adelaide_data[:,0] == 5040)[0]
  adelaide_tasd_sim = adelaide_data[tasd_i, 1] / adelaide_tasd_mev_mip
  # First analysis
  first_sim_wcd_ssd_fname = first_offline_sims_path + "/" + first_offline_sims_prefix + "%s" %sta_id + first_offline_sims_suffix
  first_sim_wcd_ssd = np.loadtxt(first_sim_wcd_ssd_fname)
  first_wcd_i = np.where(first_sim_wcd_ssd[:,0] == 5048)[0]
  first_ssd_i = np.where(first_sim_wcd_ssd[:,0] == 5040)[0]
  first_sim_wcd_corr_mu = R_E * first_sim_wcd_ssd[first_wcd_i,5] + R_HAD * R_E**0.9 * first_sim_wcd_ssd[first_wcd_i,6]
  first_sim_ssd_corr_mu = R_E * first_sim_wcd_ssd[first_ssd_i,2] + R_HAD * R_E**0.9 * first_sim_wcd_ssd[first_ssd_i,3]
  first_sim_ssd_corr_mu_scaled = first_sim_ssd_corr_mu * 0.78
  fig = plt.figure(figsize=(12,10))
  gs = GridSpec(4,4)
  ax_scatter = fig.add_subplot(gs[0:4, 0:3])
  ax_hist_x = fig.add_subplot(gs[0:4, 3])
  ax_scatter.scatter(sim_wcd_corr_mu, sim_ssd_corr_mu_scaled, color = "blue", label = "SSD + WCD")
  ax_scatter.scatter(first_sim_wcd_corr_mu, first_sim_ssd_corr_mu_scaled, color = "green", label = "First SSD + WCD")
  ax_scatter.scatter(obs_wcd, obs_tasd, marker='o', s = 60, label = "Data", color = "magenta")
  ax_scatter.errorbar(obs_wcd, obs_tasd, xerr = obs_wcd_unc, yerr = obs_tasd_unc, capsize = 0, marker='o', ms = 2, color = "magenta")
  ax_hist_x.hist(adelaide_tasd_sim, orientation = 'horizontal', histtype='step', color = "red")
  ax_hist_x.hist(sim_ssd_corr_mu_scaled, orientation = 'horizontal', histtype='step', color = "blue")
  handles, labels = ax_scatter.get_legend_handles_labels()
  patch = mpatches.Patch(color='red', fill=False, label='Adelaide TASD')
  handles.append(patch)
  ax_scatter.legend(handles=handles,frameon = True, prop = {'size': 12})
  ax_scatter.set_ylabel("Signal [MIP]")
  ax_scatter.set_xlabel("Signal [VEM]")
  max_plot_lim_list = [obs_wcd, obs_tasd, sim_wcd_corr_mu.max(), sim_ssd_corr_mu.max(), first_sim_wcd_corr_mu.max(), first_sim_ssd_corr_mu.max()]
  max_plot_lim = 1.1 * max(max_plot_lim_list)
  ax_scatter.set_ylim(0, max_plot_lim)
  ax_scatter.set_xlim(0, max_plot_lim)
  ax_hist_x.set_ylim(0, max_plot_lim)
  plt.tight_layout(h_pad=0.18, w_pad=0.22, rect=(0., 0.0, 0.99, 0.97))
  fig.suptitle("Event %d" %x[0])
  plt.savefig("2021_p1_analysis_event%s.png" %str(int(x[0])))
  plt.show()
