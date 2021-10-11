import numpy as np
import os
import re

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

# Script to filter out only CLF station IDs
# spq@ucla.edu
# 7/18/21

# Get list of files
dir_path = 'first_analysis_data'
dirlist = os.listdir(dir_path)

# Filter out unwanted files
pat = re.compile("^\d+_DataWriterTest.dat$")
input_files = list(filter(pat.match, dirlist))
# print(input_files)
num_files = len(input_files)

header_str = " event_id	station_id	energy_mc	zenith_mc	r_mc	scin_tot_pesum	scin_lg_tot_sig	scin_lg_tot_nosat_sig	scin_lg_tot_sat	scin_hg_tot_sig	scin_hg_tot_nosat_sig	scin_hg_tot_sat	scin_lg_tot_nosat_max	scin_hg_tot_nosat_max	scin_em_pesum	scin_lg_em_sig	scin_hg_em_sig	scin_mu_pesum	scin_lg_mu_sig	scin_hg_mu_sig	wcd_tot_pesum	wcd_lg_tot_sig	wcd_lg_tot_nosat_sig	wcd_lg_tot_sat	wcd_hg_tot_sig	wcd_hg_tot_nosat_sig	wcd_hg_tot_sat	wcd_lg_tot_nosat_max	wcd_hg_tot_nosat_max	wcd_em_pesum	wcd_lg_em_sig	wcd_hg_em_sig	wcd_mu_pesum	wcd_lg_mu_sig	wcd_hg_mu_sig"

for i, f in enumerate(input_files):
  inf_path = dir_path + "/" + f
  f_nparray = np.loadtxt(inf_path, delimiter="\t", comments="event_id",dtype=str)
  # Find CLF station indices
  clf_ind = np.where( (f_nparray[:,1] == "5048") | (f_nparray[:,1] == "5040"))[0]
  out_nparray = f_nparray[clf_ind]
  np.savetxt(dir_path + "/" + "CLF_" + f,out_nparray, fmt="%s", delimiter="\t", header=header_str)
