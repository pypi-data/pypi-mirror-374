####################################################################################################
# MAIN
####################################################################################################
import numpy as np
from matplotlib import pyplot as plt
from scipy import integrate
import time
import dipperpy as dp
from astropy.io import ascii

#def print(*args):
#    __builtins__.print(*("%.1e" % a if isinstance(a, float) else a
#                         for a in args))

dipperpy_regime=1
verbose=True

diprd_init = dp.diprd(6,1,False, dipperpy_regime=dipperpy_regime, verbose=verbose)

atom = diprd_init.redatom( lowestn=True )
lvl = atom['lvl']
for i in range(0,len(lvl)):
    print(i, lvl[i]['label'])

te=1.0e4
nne= 1.e11
l=[1.e0,1.e11]
vturb=5.e5
resolution=8000.
c=0
for length in l:
    #
    n,powr,cmatrix=diprd_init.nrescape(te,nne,length,vturb)  # alpha
    w,s = diprd_init.synspec(n,powr,resolution)  # PGJ
    if(c ==0):
        n0=n
        plt.plot(n0,'k.')
    if(c ==1):
        n1=n
        plt.plot(n1,'rx')
    #print(n)
    c+=1
plt.yscale('log')
plt.show()
plt.savefig('n.pdf')
plt.close()

#    plt.xlim([2320,2810])
#    #plt.ylim(auto=True)
#    ss=np.argsort(w)
#    plt.plot(w[ss],s[ss])
#    plt.yscale('linear')
#    plt.savefig('spec.pdf')
#    plt.close()



#
# look at jsun:
waves = np.linspace(1, 30001, 300)  # Wavelengths from 200 to 10000 Å
nu=diprd_init.cc*1.e8/waves
nu=nu[::-1]  # reverse
jbar = diprd_init.jsun(nu)

plt.plot(nu,jbar)
plt.yscale('log')
plt.xscale('linear')
plt.xlabel(r'$\nu$ Hz')
plt.ylabel(r'$J_\nu$')
plt.xlim(1.e14,1.e16)
plt.show()
plt.savefig('jsun.pdf')
plt.close()

plt.plot(waves,jbar[::-1])
plt.xlabel(r'$\lambda$ angstrom')
plt.ylabel(r'$J_\nu$ Hz')
plt.yscale('log')
plt.xscale('linear')
plt.show()
plt.savefig('jsunl.pdf')
plt.close()




