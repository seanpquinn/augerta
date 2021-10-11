import scipy.spatial
import numpy as np

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

evt_list = [1,9,12,13,34,49,53,74,80,86,90,96,
            105,107,111,114,119,122,145,149,154,156,157,165,181,188]

# TA signals
ta_data = np.loadtxt('spectrum_cut_full_analysis.txt',usecols=(5,6))

# Auger signals
auger_data = np.loadtxt('spectrum_cut_full_analysis.txt',usecols=(7,8,9))

# Must do some string parsing with this
shower_data = np.loadtxt('spectrum_cut_full_analysis.txt',dtype=str)

sim_files = ['FADC_QGSJETII-04.txt','FADC_EPOS-LHC.txt']

# Muon correction
em_coefs = [1.09,1.04]
had_coefs = [1.59,1.45]

# Bootstrap samples to take
nboot = 100000

print "0   1    2      3       4        5    6    7    8    9    10        11           12         13            14        15           16         17            18        19"
print "#ID TA_E TA_ZEN TA_EAST TA_NORTH MIP0 MIP1 VEM0 VEM1 VEM2 UMQGS_AVG UMQGS_UC_STD UMEPOS_AVG UMEPOS_UC_STD CMQGS_AVG CMQGS_UC_STD CMEPOS_AVG CMEPOS_UC_STD AS_RHO_MC TA_RHO_MC"
for j in range(len(evt_list)):
	mh = []
	mip_hg_conv = 197.005
	wcd_hg_conv = 4735.1
	# Manually switch to low gain for certain events
	# This is ugly/not maintainable and should be improved
	if evt_list[j] == 105:
		wcd_hg_conv = 4735.1 / 32
	if evt_list[j] == 114:
		wcd_hg_conv = 4735.1 / 32
		mip_hg_conv = 197.005 / 128
	if evt_list[j] == 119:
		wcd_hg_conv = 4735.1 / 32
		mip_hg_conv = 197.005
	if evt_list[j] == 154:
		wcd_hg_conv = 4735.1 / 32
		mip_hg_conv = 197.005 / 128
	if evt_list[j] == 181:
		wcd_hg_conv = 4735.1 / 32
		mip_hg_conv = 197.005 / 128
	for i in range(2):
		evt = evt_list[j]
		sim_file = '%i/' %evt + sim_files[i]
		id = np.loadtxt(sim_file,unpack=True,usecols=(0))
		mip = np.loadtxt(sim_file,unpack=True,usecols=(2,4,5))
		vem = np.loadtxt(sim_file,unpack=True,usecols=(3,6,7))
		rho = np.loadtxt(sim_file,unpack=True,usecols=(1,))
		AS_ii=np.where(id==5048)[0]
		TA_ii=np.where(id==5040)[0]
		TA_rho = rho[TA_ii][0]
		AS_rho = rho[AS_ii][0]
		y=mip.T[TA_ii];x=vem.T[AS_ii]
		y = y[:,0]
		x = x[:,0]
		y = y / mip_hg_conv
		x = x / wcd_hg_conv
		y = y * 0.78 #Scale to TA effective area
		vdata1 = auger_data[j]
		vdata2 = ta_data[j]
		vd1mean = vdata1.mean()
		vd2mean = vdata2.mean()
		# These are shower-to-shower errors
		# Should really also include signal variance added in quadrature.
		# Can use signal mean and unc functions above
		vd1err = np.sqrt(vd1mean)
		vd2err = np.sqrt(vd2mean)
		xmean = x.mean()
		ymean = y.mean()
		mu = np.array([xmean, ymean])
		V = np.cov(x,y,ddof=0)
		Vinv = np.linalg.inv(V)
		mahal_tmp = np.zeros(nboot)
		for k in range(nboot):
			vdata = np.array([np.random.normal(vd1mean,vd1err),np.random.normal(vd2mean,vd2err)])
			mahal_tmp[k] = scipy.spatial.distance.mahalanobis(vdata, mu, Vinv)
		mh.append(mahal_tmp.mean())
		mh.append(mahal_tmp.std())
	for i in range(2):
		evt = evt_list[j]
		sim_file = '%i/' %evt + sim_files[i]
		id = np.loadtxt(sim_file,unpack=True,skiprows=1,usecols=(0))
		mip = np.loadtxt(sim_file,unpack=True,skiprows=1,usecols=(2,4,5))
		vem = np.loadtxt(sim_file,unpack=True,skiprows=1,usecols=(3,6,7))
		AS_ii=np.where(id==5048)[0]
		TA_ii=np.where(id==5040)[0]
		y=mip.T[TA_ii];x=vem.T[AS_ii]
		y = y / mip_hg_conv
		x = x / wcd_hg_conv
		R_E = em_coefs[i]
		R_HAD = had_coefs[i]
		y = R_E * y[:,1] + R_HAD * R_E**0.9 * y[:,2]
		x = R_E * x[:,1] + R_HAD * R_E**0.9 * x[:,2]
		y = y * 0.78 #Scale to TA effective area
		vdata2 = ta_data[j]
		vdata1 = auger_data[j]
		vdata = np.array([vdata1.mean(), vdata2.mean()])
		mu = np.array([x.mean(), y.mean()])
		V = np.cov(x,y,ddof=0)
		Vinv = np.linalg.inv(V)
		vd1mean = vdata1.mean()
		vd2mean = vdata2.mean()
		vd1err = np.sqrt(vd1mean)
		vd2err = np.sqrt(vd2mean)
		xmean = x.mean()
		ymean = y.mean()
		mahal_tmp = np.zeros(nboot)
		for k in range(nboot):
			vdata = np.array([np.random.normal(vd1mean,vd1err),np.random.normal(vd2mean,vd2err)])
			mahal_tmp[k] = scipy.spatial.distance.mahalanobis(vdata, mu, Vinv)
		mh.append(mahal_tmp.mean())
		mh.append(mahal_tmp.std())
#		if i == 0 or i == 2:
#			print "%i: %.2f %.2f   %i" %(evt,mahal_tmp.mean(),mahal_tmp.std(),i)
	print " ".join('%s' %qq for qq in shower_data[j]) + " " + " ".join("%.2f"%qq for qq in mh) + " %i %i" %(AS_rho,TA_rho)

