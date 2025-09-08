####################################################################################################
# Plot isoelectronic sequence of photo ionization data
####################################################################################################
import numpy as np
from matplotlib import pyplot as plt
import time
import dipperpy as dp
from astropy.io import ascii


#plt.rc('text', usetex=True)
#plt.rc('font', family='serif')


dipperpy_regime=1 # full nlte

sequence=2



# levellab=['1s2 1SE']
term1= 100
orb1=102
print(orb1,' ',term1, dp.dipall.slp(term1))
term2=0
orb2=1
print(orb2,' ', term2, dp.dipall.slp(term2))
atoms = np.arange(sequence,30)


col=['r','b']
count=-1
out=atoms*0. + np.nan
outl=out*0. 
for at in range(sequence,30):
    count+=1
    ion= at-sequence+1
    diprd_init=dp.diprd(at,ion,False)
    atom = diprd_init.atom
    if(atom['ok'] == True): 
        print('   PLOTTING  ',at,'   ', dp.dipall.atomname(at), ion)
        bf=atom['bf']
        nbf=len(bf)
        #print(dp.keyzero(bf))
        for i in range(0,nbf):
            #print(' -> ',i, bf[i]['orb1'],' ', bf[i]['term1'], ' ', 
            #      bf[i]['orb2'],' ', bf[i]['term2'],'  vs.  ',orb1,term1,orb2,term2)
            if(bf[i]['term1'] == term1 and bf[i]['orb1'] == orb1 and
               bf[i]['term2'] == term2 and bf[i]['orb2'] == orb2):
                            l=np.frombuffer(bf[i]['lam'])
                            l=l**3
                            p=np.frombuffer(bf[i]['sigma'])
                            p=p**3
                            #plt.plot(l,p)
                            #plt.show()
                            #print(l)
                            il=-1
                            #print('match ', l[il],p[il],bf[i]['edgepm'])
                            out[count] =p[il]
                            outl[count]=l[il]

print(outl)
print(out)
#plt.plot(outl,(out),'.')
plt.plot(atoms-sequence+1,(out),'k.')
plt.yscale('log')
plt.title(' Photoionization '+dp.dipall.atomname(sequence) +
          ' sequence')
plt.xlabel(r'Atomic number')
#plt.xlabel(r'Threshold $\lambda\  \AA$')
plt.ylabel(r'Threshold $\sigma$ MB')
plt.savefig('he.png')
plt.show()



