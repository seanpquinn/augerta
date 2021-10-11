import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import matplotlib

data_file = 'FADC_EPOS-LHC.txt'

# Column convention: tot EM MU
id = np.loadtxt(data_file,unpack=True,skiprows=1,usecols=(0))
mip = np.loadtxt(data_file,unpack=True,skiprows=1,usecols=(2,4,5))
vem = np.loadtxt(data_file,unpack=True,skiprows=1,usecols=(3,6,7))

AS_ii=np.where(id==5048)[0]
TA_ii=np.where(id==5040)[0]

y=mip.T[TA_ii];x=vem.T[AS_ii]

xtot = vem.T[TA_ii,0]
ytot = mip.T[AS_ii,0]

R_E = 1.09
R_HAD = 1.59

yerr = 0.08 * y[:,1] + 0.17 * y[:,2]
xerr = 0.08 * x[:,1] + 0.17 * x[:,2]

y = R_E * y[:,1] + R_HAD * R_E**0.9 * y[:,2]
x = R_E * x[:,1] + R_HAD * R_E**0.9 * x[:,2]


#old constants
#mip_lg_conv = 160.34
#wcd_lg_conv = 4667.96
#New values from David, as of Aug. 3 2017
mip_lg_conv = 197.005
wcd_lg_conv = 4735.1
y = y / mip_lg_conv
x = x / wcd_lg_conv
ytot = ytot / mip_lg_conv
xtot = xtot / wcd_lg_conv
yerr = yerr / mip_lg_conv
xerr = xerr / wcd_lg_conv

y = y * 0.78 #Scale to TA effective area
yerr = yerr * 0.78
ytot = ytot * 0.78

auger_south = (51.581+60.142+57.745)/3
det2421 = (31.94+41.22)/2

a_pmt = np.array([51.581,60.142,57.745])
t_pmt = np.array([34.36,43.29])

plt.figure(figsize=(10,12))
scatter_axes = plt.subplot2grid((3, 3), (1, 0), rowspan=2, colspan=2)
x_hist_axes = plt.subplot2grid((3, 3), (0, 0), colspan=2,
                               sharex=scatter_axes)
y_hist_axes = plt.subplot2grid((3, 3), (1, 2), rowspan=2,
                               sharey=scatter_axes)

histbins = np.arange(0,85,5)
x_hist_axes.hist(x,bins=histbins,histtype='step',color='black',align='mid')
y_hist_axes.hist(y,bins=histbins,orientation='horizontal',histtype='step',color='black',align='mid')

#y_hist_axes.axis('off')
#x_hist_axes.axis('off')

y_hist_axes.axes.get_yaxis().set_visible(False)
x_hist_axes.axes.get_xaxis().set_visible(False)

x_hist_axes.spines['right'].set_visible(False)
x_hist_axes.spines['top'].set_visible(False)

# Only show ticks on the left and bottom spines
x_hist_axes.yaxis.set_ticks_position('left')
x_hist_axes.xaxis.set_ticks_position('bottom')

y_hist_axes.spines['right'].set_visible(False)
y_hist_axes.spines['top'].set_visible(False)

# Only show ticks on the left and bottom spines
y_hist_axes.yaxis.set_ticks_position('left')
y_hist_axes.xaxis.set_ticks_position('bottom')


X,Y=np.mgrid[0:70:400j,0:70:400j]
positions = np.vstack([X.ravel(), Y.ravel()])
values=np.vstack([x,y])
kernel=stats.gaussian_kde(values)
Z=np.reshape(kernel(positions).T,X.shape)
the_cmap = plt.cm.OrRd
the_cmap.set_under('white')
scatter_axes.contourf(X,Y,Z,cmap=the_cmap,vmin=0.0004,zorder=1)

def as_unc(x):
	x2 = x*x
	return np.sqrt(np.var(x)+0.01**2*x2.sum())

def rel_unc(x,y,dx,dy):
	#x is simulated signal
	#so, x argument should be x.mean() or y.mean()
	#y is observed signal
	#so y is a_pmt.mean() or t_pmt.mean()
	return np.sqrt( (4 * y * dx / (x + y)**2)**2 + (4 * x * dy / (x + y)**2)**2 )

a_err = as_unc(a_pmt)
t_err = t_pmt.std()

rvem = 2 * np.abs(a_pmt.mean() - x.mean()) / (a_pmt.mean() + x.mean()) * 100 #unit of %
rmip = 2 * np.abs(t_pmt.mean() - y.mean()) / (t_pmt.mean() + y.mean()) * 100 #unit of %
rvem_err = rel_unc(x.mean(),a_pmt.mean(),x.std(),as_unc(a_pmt)) * 100
rmip_err = rel_unc(y.mean(),t_pmt.mean(),y.std(),t_pmt.std()) * 100


#scatter_axes.scatter(x, y, color='black', s=12, label='EPOS-LHC corr.',zorder=3)
#scatter_axes.scatter(xtot, ytot, color='grey', s=12, label='EPOS-LHC uncorr.',zorder=2,alpha=0.6)
scatter_axes.scatter(x, y, color='black', s=12,zorder=3)
scatter_axes.scatter(xtot, ytot, color='grey', s=12,zorder=2,alpha=0.6)
scatter_axes.scatter(1000, 1000, color='black',label='EPOS-LHC corr.',s=80,zorder=3)
scatter_axes.scatter(1000, 10000, color='grey', label='EPOS-LHC uncorr.',s=80,zorder=2,alpha=0.65)

x_hist_axes.hist(xtot,bins=histbins,histtype='step',color='gray',align='mid',alpha=0.7)
y_hist_axes.hist(ytot,bins=histbins,orientation='horizontal',histtype='step',color='gray',align='mid',alpha=0.7)


#scatter_axes.errorbar(x, y, xerr=xerr, yerr=yerr, ls='none', color='black',capsize=0,zorder=1)
scatter_axes.scatter(auger_south,det2421,color='violet',s=80,label='Data',zorder=4)
scatter_axes.errorbar(auger_south,det2421,xerr=as_unc(a_pmt),yerr=t_pmt.std(),color='violet',capsize=0,lw=3.5,zorder=4)

scatter_axes.set_xlabel('S(Auger south) [VEM]')
scatter_axes.set_ylabel('S(TA) [MIP]')
scatter_axes.set_xlim(0,80)
scatter_axes.set_ylim(0,80)
scatter_axes.minorticks_on()
scatter_axes.legend()

sim_mip_mean = y.mean()
sim_mip_err = y.std()
sim_vem_mean = x.mean()
sim_vem_err = x.std()
#scatter_axes.errorbar(sim_vem_mean,sim_mip_mean,xerr=sim_vem_err,yerr=sim_mip_err,color='grey',capsize=0,lw=2.4)

plt.show()

print "dVEM: %.3f +- %.3f" %(auger_south-x.mean(),np.sqrt(a_err**2+x.var()))
print "rVEM: %.3f +- %.3f" %(rvem,rvem_err)
print "dMIP: %.3f +- %.3f" %(det2421-y.mean(),y.std())
print "rMIP: %.3f +- %.3f" %(rmip,rmip_err)
print "data x dx y dy: %.2f %.2f %.2f %.2f" %(a_pmt.mean(),a_err,t_pmt.mean(),t_err)
print "sim x dx y dy: %.2f %.2f %.2f %.2f" %(sim_vem_mean,sim_vem_err,sim_mip_mean,sim_mip_err)

#scatter_axes.text(0.05,0.85,prim_str,fontsize=20,color='dimgray',ha='left',va='center',transform=scatter_axes.transAxes)
#enum = 9
#plt.savefig('new_plot_%i.pdf' %enum)
#plt.show()
