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

sequence=5



# levellab=['2S2 2P 2PO 3/2']
term1= 210
orb1=211
print(orb1,' ',term1, dp.dipall.slp(term1))
term2=0
orb2=202
print(orb2,' ', term2, dp.dipall.slp(term2))
# seems to work  
orb1 =212 # 2p^2
term1=200 #2So
orb2=201  #2s^1
term2=0   # < nowt> #

atoms = np.arange(sequence,7)


col=['r','b']
count=-1
out=atoms*0. + np.nan
outl=out*0. 
for at in range(sequence+1,7):
    count+=1
    ion= at-sequence+1
    diprd_init=dp.diprd(at,ion,False, dipperpy_regime=dipperpy_regime)
    atom = diprd_init.atom
    if(atom['ok'] == True): 
        print('   PLOTTING  ',at,'   ', dp.dipall.atomname(at), ion)
        bf=atom['bf']
        nbf=len(bf)
        for i in range(0,nbf):
            #print(' -> ',i, bf[i]['orb1'],' ', bf[i]['term1'], ' ', 
            #      bf[i]['orb2'],' ', bf[i]['term2'])
            if(bf[i]['term1'] == term1 and bf[i]['orb1'] == orb1 and
               bf[i]['term2'] == term2 and bf[i]['orb2'] == orb2):
                            l=np.frombuffer(bf[i]['lam'])
                            p=np.frombuffer(bf[i]['sigma'])
                            il=10
                            print(l[il],p[il])
                            out[count] =p[il]
                            outl[count]=l[il]

print(outl)
print(out)
plt.plot(atoms,outl,'.')
plt.show()


