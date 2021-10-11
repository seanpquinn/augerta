import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import matplotlib

def as_unc(x):
	x2 = x*x
	return np.sqrt(np.var(x)+0.01**2*x2.sum())

def rel_unc(x,y,dx,dy):
	#x is simulated signal
	#so, x argument should be x.mean() or y.mean()
	#y is observed signal
	#so y is a_pmt.mean() or t_pmt.mean()
	return np.sqrt( (4 * y * dx / (x + y)**2)**2 + (4 * x * dy / (x + y)**2)**2 )

t_pmt = np.array([3.74,4.61])
a_pmt = np.array([5.019,6.778,7.468])
xy_max = 20

enum = 156
plot_size = (7,7)

#old constants
#mip_lg_conv = 160.34
#wcd_lg_conv = 4667.96
#New values from David, as of Aug. 3 2017
mip_hg_conv = 197.005
wcd_hg_conv = 4735.1


data_file = 'FADC_EPOS-LHC.txt'

# Column convention: tot EM MU
id = np.loadtxt(data_file,unpack=True,skiprows=1,usecols=(0))
mip = np.loadtxt(data_file,unpack=True,skiprows=1,usecols=(2,4,5))
vem = np.loadtxt(data_file,unpack=True,skiprows=1,usecols=(3,6,7))

AS_ii=np.where(id==5048)[0]
TA_ii=np.where(id==5040)[0]

y=mip.T[TA_ii];x=vem.T[AS_ii]

y = y[:,0]
x = x[:,0]

y = y / mip_hg_conv
x = x / wcd_hg_conv

y = y * 0.78 #Scale to TA effective area

a_err = as_unc(a_pmt)
t_err = t_pmt.std()

sim_mip_mean = y.mean()
sim_mip_err = y.std()
sim_vem_mean = x.mean()
sim_vem_err = x.std()
uncorr_mip = sim_mip_mean
uncorr_mip_unc = sim_mip_err
uncorr_vem = sim_vem_mean
uncorr_vem_unc = sim_vem_err



# Column convention: tot EM MU
id = np.loadtxt(data_file,unpack=True,skiprows=1,usecols=(0))
mip = np.loadtxt(data_file,unpack=True,skiprows=1,usecols=(2,4,5))
vem = np.loadtxt(data_file,unpack=True,skiprows=1,usecols=(3,6,7))

AS_ii=np.where(id==5048)[0]
TA_ii=np.where(id==5040)[0]

y=mip.T[TA_ii];x=vem.T[AS_ii]

R_E = 1.04
R_HAD = 1.45

y = y / mip_hg_conv
x = x / wcd_hg_conv

y = R_E * y[:,1] + R_HAD * R_E**0.9 * y[:,2]
x = R_E * x[:,1] + R_HAD * R_E**0.9 * x[:,2]

y = y * 0.78 #Scale to TA effective area

sim_mip_mean = y.mean()
sim_mip_err = y.std()
sim_vem_mean = x.mean()
sim_vem_err = x.std()

corr_mip = sim_mip_mean
corr_mip_unc = sim_mip_err
corr_vem = sim_vem_mean
corr_vem_unc = sim_vem_err

plt.figure(figsize=plot_size)
plt.scatter(corr_vem,corr_mip,color='indianred',s=65,
label='EPOS-LHC',zorder=2,marker='s')
plt.errorbar(corr_vem,corr_mip,xerr=corr_vem_unc,
	yerr=corr_mip_unc,color='indianred',capsize=0)
plt.scatter(uncorr_vem,uncorr_mip,color='red',s=65,zorder=2,marker='^')
plt.errorbar(uncorr_vem,uncorr_mip,xerr=uncorr_vem_unc,
	yerr=uncorr_mip_unc,color='indianred',capsize=0)
plt.xlabel('S(Auger south) [VEM]')
plt.ylabel('S(TA) [MIP]')
plt.minorticks_on()



data_file = 'FADC_QGSJETII-04.txt'

# Column convention: tot EM MU
id = np.loadtxt(data_file,unpack=True,skiprows=1,usecols=(0))
mip = np.loadtxt(data_file,unpack=True,skiprows=1,usecols=(2,4,5))
vem = np.loadtxt(data_file,unpack=True,skiprows=1,usecols=(3,6,7))

AS_ii=np.where(id==5048)[0]
TA_ii=np.where(id==5040)[0]

y=mip.T[TA_ii];x=vem.T[AS_ii]

y = y[:,0]
x = x[:,0]

#old constants
#mip_lg_conv = 160.34
#wcd_lg_conv = 4667.96
#New values from David, as of Aug. 3 2017

y = y / mip_hg_conv
x = x / wcd_hg_conv

y = y * 0.78 #Scale to TA effective area

sim_mip_mean = y.mean()
sim_mip_err = y.std()
sim_vem_mean = x.mean()
sim_vem_err = x.std()
uncorr_mip = sim_mip_mean
uncorr_mip_unc = sim_mip_err
uncorr_vem = sim_vem_mean
uncorr_vem_unc = sim_vem_err

data_file = 'FADC_QGSJETII-04.txt'

# Column convention: tot EM MU
id = np.loadtxt(data_file,unpack=True,skiprows=1,usecols=(0))
mip = np.loadtxt(data_file,unpack=True,skiprows=1,usecols=(2,4,5))
vem = np.loadtxt(data_file,unpack=True,skiprows=1,usecols=(3,6,7))

AS_ii=np.where(id==5048)[0]
TA_ii=np.where(id==5040)[0]

y=mip.T[TA_ii];x=vem.T[AS_ii]

R_E = 1.09
R_HAD = 1.59

y = y / mip_hg_conv
x = x / wcd_hg_conv

y = R_E * y[:,1] + R_HAD * R_E**0.9 * y[:,2]
x = R_E * x[:,1] + R_HAD * R_E**0.9 * x[:,2]

y = y * 0.78 #Scale to TA effective area

sim_mip_mean = y.mean()
sim_mip_err = y.std()
sim_vem_mean = x.mean()
sim_vem_err = x.std()

corr_mip = sim_mip_mean
corr_mip_unc = sim_mip_err
corr_vem = sim_vem_mean
corr_vem_unc = sim_vem_err

plt.scatter(corr_vem,corr_mip,color='cornflowerblue',s=65,
label='QGSJETII-04',zorder=2,marker='s')
plt.errorbar(corr_vem,corr_mip,xerr=corr_vem_unc,
	yerr=corr_mip_unc,color='cornflowerblue',capsize=0)
plt.scatter(uncorr_vem,uncorr_mip,color='cornflowerblue',s=65,zorder=2,marker='^')
plt.errorbar(uncorr_vem,uncorr_mip,xerr=uncorr_vem_unc,
	yerr=uncorr_mip_unc,color='cornflowerblue',capsize=0)




data_file = 'FADC_QGSJETII-03.txt'

# Column convention: tot EM MU
id = np.loadtxt(data_file,unpack=True,skiprows=1,usecols=(0))
mip = np.loadtxt(data_file,unpack=True,skiprows=1,usecols=(2,4,5))
vem = np.loadtxt(data_file,unpack=True,skiprows=1,usecols=(3,6,7))

AS_ii=np.where(id==5048)[0]
TA_ii=np.where(id==5040)[0]

y=mip.T[TA_ii];x=vem.T[AS_ii]

y = y[:,0]
x = x[:,0]

#old constants
#mip_lg_conv = 160.34
#wcd_lg_conv = 4667.96
#New values from David, as of Aug. 3 2017

y = y / mip_hg_conv
x = x / wcd_hg_conv

y = y * 0.78 #Scale to TA effective area

sim_mip_mean = y.mean()
sim_mip_err = y.std()
sim_vem_mean = x.mean()
sim_vem_err = x.std()
uncorr_mip = sim_mip_mean
uncorr_mip_unc = sim_mip_err
uncorr_vem = sim_vem_mean
uncorr_vem_unc = sim_vem_err

data_file = 'FADC_QGSJETII-03.txt'

# Column convention: tot EM MU
id = np.loadtxt(data_file,unpack=True,skiprows=1,usecols=(0))
mip = np.loadtxt(data_file,unpack=True,skiprows=1,usecols=(2,4,5))
vem = np.loadtxt(data_file,unpack=True,skiprows=1,usecols=(3,6,7))

AS_ii=np.where(id==5048)[0]
TA_ii=np.where(id==5040)[0]

y=mip.T[TA_ii];x=vem.T[AS_ii]

R_E = 1.09
R_HAD = 1.59

y = y / mip_hg_conv
x = x / wcd_hg_conv

y = R_E * y[:,1] + R_HAD * R_E**0.9 * y[:,2]
x = R_E * x[:,1] + R_HAD * R_E**0.9 * x[:,2]

y = y * 0.78 #Scale to TA effective area

sim_mip_mean = y.mean()
sim_mip_err = y.std()
sim_vem_mean = x.mean()
sim_vem_err = x.std()

corr_mip = sim_mip_mean
corr_mip_unc = sim_mip_err
corr_vem = sim_vem_mean
corr_vem_unc = sim_vem_err

plt.scatter(corr_vem,corr_mip,color='orange',s=65,
label='QGSJETII-03',zorder=2,marker='s')
plt.errorbar(corr_vem,corr_mip,xerr=corr_vem_unc,
	yerr=corr_mip_unc,color='orange',capsize=0)
plt.scatter(uncorr_vem,uncorr_mip,color='orange',s=65,zorder=2,marker='^')
plt.errorbar(uncorr_vem,uncorr_mip,xerr=uncorr_vem_unc,
	yerr=uncorr_mip_unc,color='orange',capsize=0)



plt.scatter(a_pmt.mean(),t_pmt.mean(),color='violet',s=65,label='Data',zorder=2)
plt.errorbar(a_pmt.mean(),t_pmt.mean(),xerr=as_unc(a_pmt),yerr=t_pmt.std(),color='violet',capsize=0)
plt.ylim(0,xy_max)
plt.xlim(0,xy_max)
plt.legend(loc=2)
plt.tight_layout()
plt.savefig('had_compare_evt_%i.pdf' %enum)
plt.show()
