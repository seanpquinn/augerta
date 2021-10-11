import scipy.spatial
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

mahal_uepos = np.loadtxt('all_cuts_mahal.txt', usecols=(12,))
mahal_uepos_unc = np.loadtxt('all_cuts_mahal.txt', usecols=(13,))
mahal_cepos = np.loadtxt('all_cuts_mahal.txt', usecols=(16,))
mahal_cepos_unc = np.loadtxt('all_cuts_mahal.txt', usecols=(17,))

eid = np.loadtxt('all_cuts_mahal.txt', usecols=(0,))
mbin = [0.,1.52,2.49,3.44,4.37,5.35,6.3,7.3]
eid_str = []
for i in range(len(eid)):
	eid_str.append("%i" %eid[i])

# Plot EPOS results
locs = np.arange(len(eid))
plt.figure(figsize=(8,7))
plt.errorbar(mahal_uepos,locs-0.35,
	xerr=mahal_uepos_unc,ecolor='black',
	zorder=1,fmt='o',label='EPOS-LHC uncorr.',
	fillstyle='none',ms=11)
plt.errorbar(mahal_cepos,locs,
	xerr=mahal_cepos_unc,ecolor='black',zorder=1,fmt='o',label='EPOS-LHC corr.',
	ms=11)
plt.vlines(mbin,ymin=-1,ymax=len(eid)+1,
	linestyle='dashed',color='gray',alpha=0.6)
for i in range(1,len(mbin)):
	plt.text(mbin[i-1]+(mbin[i]-mbin[i-1])/2-0.13, 13.15, "%i$\sigma$" %i)	
plt.ylim(-1,13)
plt.yticks(locs,eid_str)
plt.xlabel(r'$\Delta$')
plt.ylabel('Event ID')
plt.tight_layout()
plt.minorticks_off()
plt.legend()
plt.show()



# Plot QGSJ results

mahal_uqgsj = np.loadtxt('all_cuts_mahal.txt', usecols=(10,))
mahal_uqgsj_unc = np.loadtxt('all_cuts_mahal.txt', usecols=(11,))
mahal_cqgsj = np.loadtxt('all_cuts_mahal.txt', usecols=(14,))
mahal_cqgsj_unc = np.loadtxt('all_cuts_mahal.txt', usecols=(15,))

locs = np.arange(len(eid))
plt.figure(figsize=(8,7))
plt.errorbar(mahal_uqgsj,locs-0.25,
	xerr=mahal_uqgsj_unc,ecolor='black',
	zorder=1,fmt='o',label='QGSJETII-04 uncorr.',
	fillstyle='none',color='orange',ms=11)
plt.errorbar(mahal_cqgsj,locs,
	xerr=mahal_cqgsj_unc,ecolor='black',
	zorder=1,fmt='o',label='QGSJETII-04 corr.',color='orange',
	ms=11)
plt.vlines(mbin,ymin=-1,ymax=len(eid)+1,
	linestyle='dashed',color='gray',alpha=0.6)
for i in range(1,len(mbin)):
	plt.text(mbin[i-1]+(mbin[i]-mbin[i-1])/2-0.13, 13.15, "%i$\sigma$" %i)	
plt.ylim(-1,13)
plt.yticks(locs,eid_str)
plt.xlabel(r'$\Delta$')
plt.ylabel('Event ID')
plt.tight_layout()
plt.minorticks_off()
plt.legend()
plt.show()

# Plot Delta vs. rho

rho = np.loadtxt('all_cuts_mahal.txt', usecols=(18,19))
avg_r = rho.mean(axis=1)
vem = np.loadtxt('all_cuts_mahal.txt', usecols=(7,8,9))
vem = vem.mean(axis=1)
mip = np.loadtxt('all_cuts_mahal.txt', usecols=(5,6))
mip = mip.mean(axis=1)

# Plot VEM
plt.figure(figsize=(8,7))
plt.scatter(avg_r,mahal_cepos,zorder=2,c=np.log10(vem),
	cmap='viridis',vmin=0,vmax=3,s=75)
plt.colorbar(label='log(S [VEM])')

n = len(avg_r)
for i in range(n):
		plt.errorbar(avg_r[i],mahal_cepos[i],xerr=np.diff(rho[i]),yerr=mahal_cepos_unc[i],ecolor='black',zorder=1)

plt.xlabel(r'$\rho$ [m]')
plt.ylabel(r'$\Delta$')
plt.xlim(100,1700)
plt.hlines(mbin,plt.xlim()[0],plt.xlim()[1],linestyles='dashed',color='gray',alpha=0.6)
plt.tight_layout()
plt.show()

# Plot MIP
plt.figure(figsize=(8,7))
plt.scatter(avg_r,mahal_cepos,zorder=2,c=np.log10(mip),
	cmap='plasma',vmin=0,vmax=3,s=75)
plt.colorbar(label='log(S [MIP])')

n = len(avg_r)
for i in range(n):
		plt.errorbar(avg_r[i],mahal_cepos[i],xerr=np.diff(rho[i]),yerr=mahal_cepos_unc[i],ecolor='black',zorder=1)

plt.xlabel(r'$\rho$ [m]')
plt.ylabel(r'$\Delta$')
plt.tight_layout()
lims=plt.xlim()
plt.hlines(mbin,plt.xlim()[0],plt.xlim()[1],linestyles='dashed',color='gray',alpha=0.6)
plt.xlim(lims)
plt.show()


# Plot Delta vs. E

E = np.loadtxt('all_cuts_mahal.txt', usecols=(1,))
plt.figure(figsize=(8,7))
plt.scatter(E,mahal_cepos,zorder=3,label='EPOS-LHC corr.',s=65)
plt.errorbar(E,mahal_cepos,yerr=mahal_cepos_unc,ecolor='black',zorder=1,fmt='o')
plt.scatter(E,mahal_cqgsj,zorder=3,label='QGSJETII-04 corr.',s=65)
plt.errorbar(E,mahal_cqgsj,yerr=mahal_cqgsj_unc,ecolor='black',zorder=1,fmt='o')
#for i in range(n):
#	plt.vlines(E[i],ymin=min(mahal_cepos[i],mahal_cqgsj[i]),
#		ymax=max(mahal_cepos[i],mahal_cqgsj[i]),linestyle='dashed')
plt.legend()
plt.xlabel('E [EeV]')
plt.ylabel(r'$\Delta$')
plt.tight_layout()
lims=plt.xlim()
plt.hlines(mbin,plt.xlim()[0],plt.xlim()[1],linestyles='dashed',color='gray',alpha=0.6)
plt.xlim(lims)
plt.show()

# Plot Delta vs. theta

theta = np.loadtxt('all_cuts_mahal.txt', usecols=(2,))
plt.figure(figsize=(8,7))
plt.scatter(theta,mahal_cepos,zorder=3,label='EPOS-LHC corr.',s=65)
plt.errorbar(theta,mahal_cepos,yerr=mahal_cepos_unc,ecolor='black',zorder=1,fmt='o')
plt.scatter(theta,mahal_cqgsj,zorder=3,label='QGSJETII-04 corr.',s=65)
plt.errorbar(theta,mahal_cqgsj,yerr=mahal_cqgsj_unc,ecolor='black',zorder=1,fmt='o')
#for i in range(n):
#	plt.vlines(theta[i],ymin=min(mahal_cepos[i],mahal_cqgsj[i]),
#		ymax=max(mahal_cepos[i],mahal_cqgsj[i]),linestyle='dashed')

plt.legend()
plt.xlabel(r'$\theta$ [deg.]')
plt.ylabel(r'$\Delta$')
plt.tight_layout()
lims=plt.xlim()
plt.hlines(mbin,plt.xlim()[0],plt.xlim()[1],linestyles='dashed',color='gray',alpha=0.6)
plt.xlim(lims)
plt.show()

