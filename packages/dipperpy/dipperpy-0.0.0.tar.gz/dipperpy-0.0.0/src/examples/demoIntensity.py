################################################################################
#
# Main subprograms for pydip package
#
################################################################################

import sqlite3
import numpy as np
#import dippy as dp
from scipy.interpolate import CubicSpline
from scipy import interpolate
#from scipy.integrate import trapz
from scipy import special
import scipy
from matplotlib import pyplot as plt
from astropy.io import ascii
import scipy.special as sp
import time
import copy
import sys
import math

def pe(t):
    p=0.5 /(1.+t)
    return p, -1.*p*p

######################################################################

n=5
tau = np.linspace(-3,n,n*20)
dt = np.gradient(tau)
tau=10.**tau

n=4000
tau = 0.001 + np.linspace(0,n,n*5)
dt=tau[1]-tau[0]

tm =max(tau)-tau +min(tau)

p,derp=pe(tau)
pt,derpt=pe(tm)
derpt[-1]=derpt[-2]
b=1. +0.*tau
eps=.1
s=b*0. +1. #+ max(b)/(tau+max(tau))
jp=b*0.
jm=b*0.
second=jp*0.
emax=1.
#
#  here are the escape probabilities at each edge of the slab
#
pt0=0.5
ptt=0.5
#
# here is incident radiation approximated as Jinc*pe
#
jinc=0.3
jinc*=p
#
#
c=0
elim =1.e-3
while (emax > elim and c < 20):
    c+=1
    sold=s*1.0
    #
    # first order part of KP92 eq 34.  Currently PGJ cannot
    #  account for the    fudge factor. does seem to work. 
    #
    fudge=0.5
    first=(pt0-p-pt+ptt)*sold * fudge +0. 
    jp=first*1.
    jm=first*1.
    #second order 
    second = -np.cumsum(s*derpt*dt)*fudge
    second[-1]=second[-2]  # something wrong with cumsum
#    print()
#    print(c, 'first')
#    print(first)
#    print(c,'second')
#    print(second/first)
#    print('old sold')
#    print(sold)
    jp  =  first + second + jinc*0
    jm  =  jp[::-1] -jinc
    #
    snew =(1.-eps)*(jp+jm) + eps*b
    emax=max(np.abs(1-snew/sold))
    s=snew
    print(c,"{:2e}".format(emax))
    if( c % 20 ==0):
        plt.plot(tau,sold)
        plt.plot(tau,first,'.')
        #plt.plot(tau,jp)
        plt.title(str(c))
        plt.plot(tau,second,'*')
        plt.yscale('log')
        plt.show()
if(1 <0):
    title='epsilon='+str(eps)
    plt.xscale('linear')
    plt.yscale('log')
    plt.title(title)
    plt.savefig('esc2.pdf')
    plt.show()
    plt.close()

uu=1.66e-24
kb=1.38e-16

mion=56*uu     # iron, e.g. 
vt=10. # turbulence km/s
t=1.e4
dnyd=np.sqrt(kb*t/mion + vt*vt*1.e10) 

x = np.linspace(-8,8,100)  #/dnyd
sm=3

phi=np.exp(-x*x)  +0.0001/x/x
intx=phi*0.
#
c=-1
#
# eddington-barbiet outward intensity
#
one=1.
for y in x:
    c+=1
    tx=phi[c]*tau  # opacity at x[c]
    intx[c] = np.interp(one,tx,s, left=0.,right=0.) # s where tau =1
#
plt.close()
#
dnyd=1.
plt.step(x*dnyd,intx)
intx=scipy.ndimage.gaussian_filter1d(intx,sm)
plt.step(x*dnyd,intx)
plt.plot(x*dnyd,phi)
plt.ylabel('Intensity (relative units)')
plt.xlabel('wavelength (units of Doppler width)')
plt.show()


