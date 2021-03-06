import numpy as N
import pylab as P
import sys
import time
from scipy.optimize import leastsq


runs = 100
def InvRec(p,x):
	amplitude, b, T1, beta = p
	return amplitude *( 1 - b * N.exp(-(x/T1)**beta))

def func(p,x,y):
	return InvRec(p,x) - y

filename = sys.argv[1]
try:
	picfile = sys.argv[2]
except:
	picfile=None

data = N.loadtxt(filename)

x = data[:,0]
y = data[:,1]

n = len(y)

p0 = [ abs(y).max(), (y.max()-y.min())/y.max(), x[abs(y).argmin()]*N.log(2), 1]
print "Startparameter:",p0
res,covvar,misc,info,success = leastsq(func, p0, args=(x,y), full_output=1)
#print "A: %.2f\nb: %.2f\n T1:%.2fs\nbeta: %.2f\n"%(amplitude, b, T1, beta)

fitresults = []
skipped = 0 
p0 = list(res[:]+0)
print "Resampling ... "
t = time.time()
for i in xrange(runs):
	indices = N.random.randint(0,n,n)
	#print indices
	xnew,ynew = x[indices],y[indices]
	run_res,run_success = leastsq(func,p0,args=(xnew,ynew), maxfev=150, warning=0)
	if run_success == 1:
		fitresults.append(run_res)
	else: skipped += 1
t -= time.time()
print "\nUnsuccessful fits: %i out of %i (%.1f%%)"%(skipped, runs, skipped/float(runs)*100)
print "Time: %.1fs\n"%(-t)
fitresults = N.array(fitresults)
print "\n***** Boostrap/Resampling:\n"
print "A:   ",fitresults[:,0].mean(), "+/-",fitresults[:,0].std()/N.sqrt(runs-skipped)
print "b:   ",fitresults[:,1].mean(), "+/-",fitresults[:,1].std()/N.sqrt(runs-skipped)
print "T1:  ",fitresults[:,2].mean(), "+/-",fitresults[:,2].std()/N.sqrt(runs-skipped)
print "beta:",fitresults[:,3].mean(), "+/-",fitresults[:,3].std()/N.sqrt(runs-skipped)

if success == 1:
#	print "\n***** Standard Fit:\n"
	amplitude, b, T1, beta = res
	residuals = func(res,x,y)
	errs = N.dot(residuals,residuals)/(len(x)-len(res))
	errs *= N.diagonal(covvar)
	errs = N.sqrt(errs)
	resultstring =  " A   : %8.2f +/- %4.2f \n b   : %8.2f +/- %4.2f\n T1  :%8.4f +/- %4.4f s\n beta: %8.2f +/- %4.2f\n"%(amplitude, errs[0], b, errs[1], T1, errs[2], beta, errs[3])
#	print resultstring
P.semilogx(x,y,'bo',label=filename)
xr = N.logspace(N.log10(x.min()),N.log10(x.max()),1024)
P.semilogx(xr, InvRec(res,xr),'r-',label='Fit')
P.ylim(y.min()*1.2,y.max()*1.5)
P.xlabel('Time/s')
P.ylabel('Signal/a.u.')
P.text(0.05,0.6,resultstring,transform = P.gca().transAxes)
P.legend()
import re
a = re.compile('\d+\.\d')
try:
	T = re.search(a,filename).group()
except:
	T=0
print "#XXX", T,amplitude, T1, beta, b
if not picfile == None:
	P.savefig(picfile)
P.show()
