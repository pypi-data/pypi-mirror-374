#
# Main subprograms for pydip package
#
####################################################################################################
import numpy as np
from matplotlib import pyplot as plt
from collections import defaultdict
from astropy.io import fits
from astropy.io import ascii
import dipperpy as dp
import os
#
####################################################################################################
#
# MAIN 
####################################################################################################
#
# here are global variables, i.e. with global scope
#
print("DIAGNOSTIC PACKAGE IN PYTHON (dipperpy)")
print('Global variables all are of the kind dipperpy_XXX                                          ')
print('       where  XXX is, e.g., regime, approx, dbdir')
print()
dipperpy_regime=2
dipperpy_approx=0

np.set_printoptions(precision=2)
plt.rcParams["figure.figsize"] = (9,6)
plt.rcParams.update({'font.size': 11})


x=dp.dipall.diplist('c')
#x=dp.diplist('c')
##x=dp.diplist('o')
##x=dp.diplist('fe')
               
print()
print('Reading BASS spectrum ')
#
lam=input("enter 6302 or 5250: ")
lam=int(lam)
file='bass'+str(lam)
pathdir = dp.diprd(26,1).dipperpy_dbdir + os.path.sep  
print(pathdir + file)

d=ascii.read(pathdir + file+'.txt', guess=False, format='basic')
w=d['wave']
f=d['flux']

plt.plot(w,f,label='Sun BASS ')
#
plt.xlim(lam-8,lam+8)
plt.ylim(00,16000)
plt.xlabel('Wavelength angstrom')
plt.ylabel('Jungfraujoch brightness')

boundonly=True
diprd_init=dp.diprd(26,1,boundonly, dipperpy_regime=dipperpy_regime, dipperpy_approx=dipperpy_approx) # debug, not sure why this doesn't have any levels in the lvlrd
atom = diprd_init.atom
lvl=atom['lvl']
#print(lvl[0])

#bb=dp.bbdata(atom)
bb=diprd_init.bbdata()
bbold=bb

print()
print('atom ',type(atom))
print('lvl ', type(lvl))
print('bb ',type(bb))
print()
print(len(bb), 'bef')
##if(lam == 6302): bb=missing.missing(atom)
#bb=missing.missing(atom)
bb=diprd_init.missing()
print(len(bb), 'aft')
print(' MISSING:')


atom['bb']=bb

#x=dp.specid(atom)
x=diprd_init.specid()

plt.show()
plt.savefig(file+'.pdf')



