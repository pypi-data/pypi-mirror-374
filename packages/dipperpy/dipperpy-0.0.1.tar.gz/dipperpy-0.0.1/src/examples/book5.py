####################################################################################################
# Plot isoelectronic sequence of other ions
####################################################################################################
import dipperpy as dp
import numpy as np
from matplotlib import pyplot as plt
import time
from astropy.io import ascii
from scipy.interpolate import CubicSpline

figure, axis = plt.subplots(3, 2,figsize=(10,11))

col=['r','b','y']

dipperpy_regime=0  # coronal

iseq=-1
for sequence in (np.array([6,6],int)):   # loop over sequence
    iseq+=1
    atoms = np.arange(sequence,30)


    diprd_init=dp.diprd(sequence,1,False, dipperpy_regime=dipperpy_regime)
    atom = diprd_init.atom
    lvl=atom['lvl']


    print(lvl[0].keys())
    # dp.level(atom) # print levels
    llab=lvl[1]['label']
    if(sequence == 7): llab=lvl[0]['label']
    ulab=[lvl[8]['label'],lvl[9]['label'],lvl[11]['label']]
    print('USE FOLLOWING UPPER LEVELS')
    print(ulab)
    print('TO LOWER LEVEL')
    print(llab)

    atoms = np.arange(sequence,30)

######################################################################
#   Collision strength plot
######################################################################

    const=1.
    kount=-1
    for uab in ulab:
        kount+=1
        out= atoms*0  +np.nan
        outt=out*0.
        count=-1
        for at in range(sequence+1,30):
            count+=1
            ion= at-sequence+1
            diprd_init=dp.diprd(at,ion,False, dipperpy_regime=dipperpy_regime)
            atom = diprd_init.atom
            if(atom['ok'] == True):
            
                tl, omega = diprd_init.matchcol(llab,uab)
                out[count]=omega
                outt[count]=tl
                            
                #if(sequence == 14 and at == 20): out[count]*=10

        use= np.logical_not(np.isnan(out))

        axis[0,iseq].plot(atoms[use]+1,out[use]*const, col[kount]+'.-',label=llab+' -- '+uab)
        axis[0,iseq].set_yscale('log')
        axis[0,iseq].set_ylabel(r'$\Upsilon(T_e)$ ')
        axis[0,iseq].set_xticks(atoms[::2])
        axis[0,iseq].set_xticklabels(atoms[::2], fontsize=10)
        axis[0,iseq].set_title(r"Collision strengths of "+
                               dp.dipall.atomname(sequence)+' sequence',fontsize=9)
        axis[0,iseq].legend(fontsize=8)
    
######################################################################
#   Oscillator strength plot
######################################################################

    const=1.
    kount=-1
    for ul in ulab:
        kount+=1
        out= atoms*0  +np.nan
        outt=out*0.
        count=-1
        for at in range(sequence+1,30):
            count+=1
            ion= at-sequence+1
            diprd_init=dp.diprd(at,ion,False, dipperpy_regime=dipperpy_regime)
            atom = diprd_init.atom
            if(atom['ok'] == True):
                ##dp.trans(atom)
                f = diprd_init.matchf(llab,ul.strip())
                out[count]=f
                ##print(at,ion,f,llab,ul.strip())

        use= np.logical_not(np.isnan(out))
        axis[1,iseq].plot(atoms[use]+1,out[use]*const, col[kount]+'.-',label=llab+' -- '+ul.strip())
    axis[1,iseq].set_yscale('log')
    axis[1,iseq].set_ylabel(r'$f_{ABS}$ ')
    axis[1,iseq].set_xticks(atoms[::2])
    axis[1,iseq].set_xticklabels(atoms[::2], fontsize=10)
    axis[1,iseq].set_title(r"Oscillator strengths of "+dp.dipall.atomname(sequence)+' sequence',fontsize=9)
    axis[1,iseq].legend(fontsize=8)
    axis[1,iseq].set_ylim([1.e-7, 1.])
        
    
######################################################################
#   Energy level plot
######################################################################

######################################################################
#  ionization potential
    out= atoms*0  +np.nan
    count=-1
    coli='g'
    for at in range(sequence+1,30):
        count+=1
        ion= at-sequence+1
        diprd_init=dp.diprd(at,ion,False, dipperpy_regime=dipperpy_regime)
        atom = diprd_init.atom
        out[count]=diprd_init.ipotl(ion)
        use= np.logical_not(np.isnan(out))


    axis[2,iseq].plot(atoms[use]+1,out[use]*const, coli+'.-',label='IP')
    axis[2,iseq].set_yscale('log')
    axis[2,iseq].set_xlabel('Atomic number A')
    axis[2,iseq].set_ylabel('Level energy eV  ')
    axis[2,iseq].set_xticks(atoms[::2])
    axis[2,iseq].set_xticklabels(atoms[::2], fontsize=10)
    axis[2,iseq].set_title(r"Level energy eV"
                           +dp.dipall.atomname(sequence)+' sequence',fontsize=9)
######################################################################

        
    const= 100. * dp.dipall.hh * dp.dipall.cc        / dp.dipall.ee 
    kount=-1
    for ul in ulab:
        kount+=1
        out= atoms*0  +np.nan
        outt=out*0.
        count=-1
        for at in range(sequence+1,30):
            count+=1
            ion= at-sequence+1
            diprd_init=dp.diprd(at,ion,False, dipperpy_regime=dipperpy_regime)
            atom = diprd_init.atom
            e=np.nan
            done=0
            if(atom['ok'] == True and done ==0):
                lvl=atom['lvl']
                for il in range(0,len(lvl)):
                    if(done == 0):
                        #print('HERE LEVEL ',il,' ',ul.strip(),' : ',lvl[il]['label'].strip())
                        if( lvl[il]['label'].strip() == ul.strip()):
                            e=lvl[il]['e']
                            #print('HERE ENERGY ',e,' MATCH')
                            out[count]=e*const
                            done=1

        use= np.logical_not(np.isnan(out))
        axis[2,iseq].plot(atoms[use]+1,out[use]*const, col[kount]+'.-',label=ul)
        axis[2,iseq].set_yscale('log')
        axis[2,iseq].set_xticks(atoms[::2])
        axis[2,iseq].set_xticklabels(atoms[::2], fontsize=10)
        axis[2,iseq].set_title(r"Level energies of "+dp.dipall.atomname(sequence)+' sequence',fontsize=9)
        axis[2,iseq].legend(fontsize=8)




        
################################################################################

plt.savefig('figisos67.png')
plt.show()
plt.close()

                    

