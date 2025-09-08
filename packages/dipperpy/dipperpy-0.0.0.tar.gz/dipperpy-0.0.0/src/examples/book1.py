####################################################################################################
# Plot isoelectronic sequence of Be-like ions
####################################################################################################
import numpy as np
from matplotlib import pyplot as plt
import time
import dipperpy as dp
from astropy.io import ascii


#plt.rc('text', usetex=True)
#plt.rc('font', family='serif')


sequence=5
atoms = np.arange(sequence,30)
levellab=['2S 2P2 2PE 3/2','2S 2P 3P 2PE 3/2']

const = dp.dipall.hh * dp.dipall.cc / dp.dipall.ee
#const=1.
col=['r','b']
kount=-1
for lab in levellab:
    out= atoms*0  +np.nan
    print('DOING  ', lab)
    kount+=1
    count=-1
    for at in range(sequence+1,30):
        count+=1
        ion= at-sequence+1
        atom=dp.diprd(at,ion,False).atom
        if(atom['ok'] == True): 
            print('   PLOTTING  ',at,'   ', dp.dipall.atomname(at), ion)
            lvl=atom['lvl']
            nl=len(lvl)
            for il in range(0,nl,1):
                if(lvl[il]['label'].strip() == lab):
                    # print(at, ion, lvl[il]['label'])
                    #out[count] = lvl[il]['lifetime']
                    out[count] = lvl[il]['e']
    plt.plot(atoms+1,out*const, col[kount]+'.',label=lab)
    plt.yscale('log')
    plt.xlabel('Atomic number Z')
    plt.ylabel('Level energy')
    plt.xticks(atoms)
    plt.title(r" levels of "+dp.dipall.atomname(sequence)+' sequence, ground state 2S2 2P 2P0 1/2')
    plt.legend()

#
# ionization potential
#


plt.show()
plt.savefig('fig_isos51.png')
plt.close()
# 


levellab=['2S 2P2 4PE 3/2','2S 2P2 2PE 3/2','2S 2P 3P 2PE 3/2']
#levellab=['2S 2P2 2PE 3/2','2S 2P 3P 2PE 3/2']



const=1.
col=['r','b','k']
kount=-1
for lab in levellab:
    out= atoms*0  +np.nan
    print('DOING  ', lab)
    kount+=1
    count=-1
    for at in range(sequence+1,30):
        count+=1
        ion= at-sequence+1
        atom=dp.diprd(at,ion,False).atom
        if(atom['ok'] == True): 
            print('   PLOTTING  ',at,'   ', dp.dipall.atomname(at), ion)
            lvl=atom['lvl']
            nl=len(lvl)
            for il in range(0,nl,1):
                if(lvl[il]['label'].strip() == lab):
                    print(at, ion, lvl[il]['label'])
                    out[count] = lvl[il]['lifetime']
                    #out[count] = lvl[il]['e']
    plt.plot(atoms+1,out*const, col[kount]+'.',label=lab)
    plt.yscale('log')
    plt.xlabel('Atomic number Z')
    plt.ylabel('Level lifetime ')
    plt.xticks(atoms)
    plt.title(r"Energy level lifetimes of "+dp.dipall.atomname(sequence)+' sequence')
    plt.legend()


plt.savefig('fig_isos52.png')
plt.show()
plt.close()

#
# collision strengths
#



const=1.
col=['r','b','k']
kount=-1
for lab in levellab:
    out= atoms*0  +np.nan
    print('DOING  ', lab)
    kount+=1
    count=-1
    for at in range(sequence+1,30):
        count+=1
        ion= at-sequence+1
        atom=dp.diprd(at,ion,False).atom
        if(atom['ok'] == True): 
            print('   PLOTTING  ',at,'   ', dp.dipall.atomname(at), ion)
            lvl=atom['lvl']
            nl=len(lvl)
            for il in range(0,nl,1):
                if(lvl[il]['label'].strip() == lab):
                    print(at, ion, lvl[il]['label'])
                    out[count] = lvl[il]['lifetime']
                    #out[count] = lvl[il]['e']
    plt.plot(atoms+1,out*const, col[kount]+'.',label=lab)
    plt.yscale('log')
    plt.xlabel('Atomic number Z')
    plt.ylabel('Level lifetime ')
    plt.xticks(atoms)
    plt.title(r"Energy level lifetimes of "+dp.dipall.atomname(sequence)+' sequence')
    plt.legend()

plt.show()
plt.savefig('fig_isos52.png')
plt.close()


