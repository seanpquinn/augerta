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

# Script that automatically extracts appropriate high gain or low gain
# PMT signals by checking saturation flag.
# spq@ucla.edu
# 7/18/21

# Get list of files
dir_path = 'first_analysis_data'
dirlist = os.listdir(dir_path)

# Filter out unwanted files
pat = re.compile("^CLF_\d+_DataWriterTest.dat$")
input_files = list(filter(pat.match, dirlist))
# print(input_files)
num_files = len(input_files)

ssd_gain_ratio = 128
wcd_gain_ratio = 32

wcd_sum_hg_adc_to_vem = 4854.6
ssd_sum_hg_adc_to_mip = 194.1
# TASD value is from PEAK of OMNIDIRECTIONAL atmospheric muon histogram
adelaide_tasd_mev_to_mip = 2.5

#Main loop for CLF WCD/SSD station data in folder

#output format by column number
# 0 sta_id
# 1 cal_tot_ssd_sig
# 2 cal_em_ssd_sig
# 3 cal_mu_ssd_sig
# 4 cal_tot_wcd_sig
# 5 cal_em_wcd_sig
# 6 cal_mu_wcd_sig
out_header_str = " sta_id  cal_tot_ssd_sig  cal_em_ssd_sig  cal_mu_ssd_sig  cal_tot_wcd_sig  cal_em_wcd_sig  cal_mu_wcd_sig  ssd_hg_sat  wcd_hg_sat"
out_col_num = len(out_header_str.split("  "))

# Convenience format string
out_fmt = "%d" + " %.2f"*6 + " %d %d"

for i, f in enumerate(input_files):
  f_path = dir_path + "/" + f
  f_nparray = np.loadtxt(f_path,delimiter="\t")
  # Skip if empty
  if len(f_nparray) == 0:
    print("[INFO]: %s is empty. Skipping." %f)
    continue
  out_nparray = np.zeros((len(f_nparray), out_col_num))
  for j, x in enumerate(f_nparray):
    # Write station ID
    # print(x)
    out_nparray[j,0] = x[1]
    # Saturation check
    scin_hg_sat_flag = x[11]
    scin_lg_sat_flag = x[8]
    wcd_hg_sat_flag = x[26]
    wcd_lg_sat_flag = x[23]
    # If lg is saturated, event must be skipped
    if scin_lg_sat_flag > 0 or wcd_lg_sat_flag > 0:
      print("[INFO]: Saturated event %d. Station: %d. Skipping." %(x[0], x[1]))
      continue
    # Computed calibrated signals
    # Default to hg outputs
    # SSD
    ssd_cal_const = ssd_sum_hg_adc_to_mip
    out_nparray[j,1] = x[9] / ssd_cal_const # cal_tot_ssd_sig
    out_nparray[j,2] = x[16] / ssd_cal_const # cal_em_ssd_sig
    out_nparray[j,3] = x[19] / ssd_cal_const  # cal_mu_ssd_sig
    # WCD
    wcd_cal_const = wcd_sum_hg_adc_to_vem
    out_nparray[j,4] = x[24] / wcd_cal_const # cal_tot_wcd_sig
    out_nparray[j,5] = x[31] / wcd_cal_const # cal_em_wcd_sig
    out_nparray[j,6] = x[34] / wcd_cal_const  # cal_mu_wcd_sig
    # If hg is saturated, force use of lg
    if wcd_hg_sat_flag > 0:
      wcd_cal_const = wcd_sum_hg_adc_to_vem / wcd_gain_ratio
      out_nparray[j,4] = x[21] / wcd_cal_const # cal_tot_wcd_sig
      out_nparray[j,5] = x[30] / wcd_cal_const # cal_em_wcd_sig
      out_nparray[j,6] = x[33] / wcd_cal_const  # cal_mu_wcd_sig
      out_nparray[j,8] = 1
    if scin_hg_sat_flag > 0:
      ssd_cal_const = ssd_sum_hg_adc_to_mip / ssd_gain_ratio
      out_nparray[j,1] = x[6] / ssd_cal_const # cal_tot_ssd_sig
      out_nparray[j,2] = x[15] / ssd_cal_const # cal_em_ssd_sig
      out_nparray[j,3] = x[18] / ssd_cal_const  # cal_mu_ssd_sig
      out_nparray[j,7] = 1
  out_path = dir_path + "/" + "CAL_" + f
  np.savetxt(out_path, out_nparray, fmt=out_fmt, header=out_header_str)
