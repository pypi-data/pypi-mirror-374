####################################################################################################
# MAIN 
####################################################################################################
import numpy as np
from matplotlib import pyplot as plt
import time, os
import dipperpy as dp



ions=np.arange(5,dtype=int)+2
print('ions ',ions)
diprd_multi_init = dp.diprd_multi(6,ions)
atom=diprd_multi_init.atom
#atom=diprd(6,2,False) 


lvl=atom['lvl']
for i in range(0,len(lvl),1000):
    print(i,lvl[i]['label'])
print('LEN ',len(lvl))

atom=diprd_multi_init.redatom(lowestn=True)
bb=atom['bb']
#a=diprd_multi_init.check()

lvl=atom['lvl']
nl=len(lvl)

m=100
nout= np.zeros((m,nl))
count=-1
k=400  
l= 700
delta=int((l-k)/m)
tlog=[]
ne=1.e10
for tl in range(k,l,delta):
    #for i in range(10): print('.')
    count+=1
    te=10.**(tl/100.0)
    #print(' T  n  ', te,ne)
    n, nstar, w, e, lhs, cmatrix =diprd_multi_init.se(te,ne)
    nout[count,:]=n
    if count ==3:
        eout=e
    tlog.append(tl/100.)

#print()
print(' LEVELS !!!')
for i in range(0,len(lvl),10):
#    if(lvl[i]['meta'])==1:
        print(i,'  ', lvl[i]['label'],'    ',lvl[i]['meta'],lvl[i]['ion'],
              n[i],lvl[i]['g'],lvl[i]['lifetime'])
        #print('nout ',nout[:,i])

#w = dict2array(bb,'wl',float)
#j=np.argsort(w)
#eout/=max(eout)
#for i in range(0,len(w)):
#        if(eout[j[i]] > 1.e-4): print( w[j[i]],'  :  ',eout[j[i]])
#plt.plot(w,eout/max(eout),'.')
#plt.xlim(970,1180)

mx=np.nanmax(nout)
print(np.shape(nout))
print(mx)

for i in range(len(lvl)):
    plt.plot(tlog,nout[:,i]/mx)
plt.yscale('log'),
plt.ylim(1.e-6,2.)
plt.xlim(np.min(tlog),np.max(tlog))
plt.xlabel('Log10 T')
plt.ylabel('Carbon ions: relative level population')
plt.savefig('demo1.pdf')
plt.show()

print(tlog)

print('Te Ne used  ',np.log10(te),np.log10(ne))
####################################################################################################



