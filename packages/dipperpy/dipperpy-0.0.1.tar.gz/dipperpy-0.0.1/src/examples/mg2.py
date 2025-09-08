import matplotlib.pyplot as plt
import numpy as np
import scipy.special as sp
import math
import dipperpy as dp

ee=dp.dipall.ee
em=dp.dipall.em
cc=dp.dipall.cc
hh=dp.dipall.hh
bk=dp.dipall.bk
pi=dp.dipall.pi
rydinf=dp.dipall.c['rydinf']

plt.rcParams.update({'font.size': 14})
plt.rcParams.update({'lines.linewidth': 2.})


el=8
isos=3
z=el-isos+1
diprd_init=dp.diprd(el,el-isos+1,True)
atom = diprd_init.atom
lvl=atom['lvl']
ip=diprd_init.iprd()
ipj=ip[el,z]*ee
print(ip[el,z])
print(ee)

e=dp.dipall.dict2array(lvl,'e',float)* hh*cc # erg
pqn=dp.dipall.dict2array(lvl,'pqn',int)
l=pqn*0.
nstar=l*0.

for i in range(0,len(lvl)):
    orb1= lvl[i]['orb1']
    p=math.floor(orb1/100)
    pqn[i]=p
    #pqn[i]= lvl[i]['pqn']
    ll=orb1-p*100
    ll=math.floor(ll/10)
    l[i] = ll
    # from ip-E = ryd*z*z / nstar^2
    dej = (ipj-e[i]) 
    nstar[i]= z * np.sqrt( rydinf/ dej )
    print(i, pqn[i]-nstar[i],lvl[i]['label'],'PQN  =  ', pqn[i], '  L  = ',l[i])

delt=pqn-nstar



lab=['S','P','D','F']
for s in range(0,3):
    ok= (l == s).nonzero()
    plt.plot(pqn[ok],0*pqn[ok]+delt[ok],'.-',label=lab[s])



plt.xlabel(r'principal QN $n$')
plt.ylabel(r'$\delta_n$')

plt.title('Quantum defects for '+dp.dipall.atomname(el)+ ' '+dp.dipall.roman(z))
plt.legend()             
plt.tight_layout()
plt.savefig('mg2.png')
plt.show()
plt.close()




