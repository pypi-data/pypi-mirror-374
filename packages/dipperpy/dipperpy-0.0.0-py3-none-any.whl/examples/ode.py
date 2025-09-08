################################################################################
#
# Main subprograms for dippperpy package
#
################################################################################

import sqlite3
import numpy as np
import dipperpy as dp
from scipy.interpolate import CubicSpline#, trapz
from scipy import interpolate, special
from matplotlib import pyplot as plt
from astropy.io import ascii
import scipy.special as sp
import time
import copy
import sys
import math

def pe(t):
    p=1/(1.+t)
    return p, -1.*p*p

n=30
elim =0.01
tau = np.linspace(-10,n,n)/10.
tau=10.**tau

n=100
tau = np.linspace(0.1,n,n)

dt = np.gradient(tau)

tm =max(tau)-tau +min(tau)

p,derp=pe(tau)
pt,derpt=pe(tm)
derpt[-1]=derpt[-2]

#second=False
second=True

slab=True
#slab=False

if(slab == False):
    ptt=0.
    jp0=1.3*0
else:
    ptt=0.5
    jp0=.3

b=1. +0.*tau
eps=1.e-2
#s=b*np.sqrt(eps) +tau*0. # S=B as a first guess
s=b*.2 +0
jp=b*0.
jm=b*0.
emax=1.
c=-1

while (emax > elim and c < 45):
    c+=1
    sold=s
    jinc=jp0*p
    zp=s*derpt
    zm=s*derp
    first=(.5-p-pt+ptt)*s
    jp=first*1.
    jm=first*1.
    i=0
    #print(i, 'JP', jp[i])
    #print(zp)
    if(second):
        for i in range(1,n):
            #print(i,' ZP', zp[i-1]*dt[i-1])
            jp[i]  +=  zp[i-1]*dt[i-1] +jinc[i]
            ii=n-i-1
            jm[ii]  +=  zm[ii+1]*dt[ii-1]
            #print(ii,' JM', jm[ii])
    #
    s =(1.-eps)*(jp+jm) /2.+ eps*b
    emax=max(np.abs(1-s/sold))
    print(c,"{:2e}".format(emax))
    plt.plot(tau,sold)
#print(zp)
print('...done')
plt.plot(tau,s,'.')
title='epsilon='+str(eps)
plt.xscale('linear')
plt.yscale('linear')
plt.title(title)
plt.savefig('esc2.pdf')
plt.close()


