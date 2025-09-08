####################################################################################################
# Plot isoelectronic sequence of Be-like ions
####################################################################################################
import numpy as np
from matplotlib import pyplot as plt
import time
import dipperpy as dp
from astropy.io import ascii
from scipy.interpolate import CubicSpline


sequence=4
levelulab=['2S 2P 3PO 0','2S 2P 1PO 1','2S 3P 1PO 1']
levelllab=['2S2 1SE 0']

#sequence=5
#levelulab=['2S 2P2 4PE 5/2','2S 2P2 2PE 3/2','2S2 3P 2PO 3/2']
#levelllab=['2S2 2P 2PO 1/2']

atoms = np.arange(sequence,30)


const=1.
col=['r','b','k']
kount=-1
lab=levelllab
for uab in levelulab:
    kount+=1
    out= atoms*0  +np.nan
    outt=out*0.
    count=-1
    print('DOING  ', uab,'  -  ',lab)
    for at in range(sequence+1,30):
        count+=1
        ion= at-sequence+1
        atom=dp.diprd(at,ion,False).atom
        lup=0
        llo=0
        if(atom['ok'] == True): 
            #print('   PLOTTING  ',at,'   ', dp.atomname(at), ion)
            cbb=atom['cbb']
            lvl=atom['lvl']
            labels=[]
            for il in range(0,len(lvl)):
                if(  (lvl[il]['label']).strip() == lab): llo=il
                if(  (lvl[il]['label']).strip() == uab): lup=il
            nc=len(cbb)
            omega=np.nan
            tl=np.nan
            #print(lup,llo)
            for kc in range(0,nc):
                up=cbb[kc]['j']
                lo=cbb[kc]['i']
                if(up == lup and lo == llo):
                    # decode 
                    temp=np.frombuffer(cbb[kc]['t'])
                    omega=np.frombuffer(cbb[kc]['o'])
                    spl = CubicSpline(temp, omega, bc_type='natural')
                    tl=   3.7 + 2.*np.log10(ion)
                    omega=spl(tl)
            out[count]=omega
            outt[count]=tl


    plt.plot(atoms+1,out*const, col[kount]+'.-',label=lab[0]+' -- '+uab)
    plt.yscale('log')
    plt.xlabel('Atomic number Z')
    plt.ylabel('Collision strength ')
    plt.xticks(atoms)
    plt.title(r"Collision strengths of "+dp.dipall.atomname(sequence)+' sequence')
    plt.legend()

plt.savefig('fig_isos43.png')
plt.show()
plt.close()



levellab=['2S 2P 3PO 1','2S 2P 1PO 1','2S 3P 1PO 1']

const = dp.dipall.hh * dp.dipall.cc / dp.dipall.ee
#const=1.

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
                    # print(at, ion, lvl[il]['label'])
                    #out[count] = lvl[il]['lifetime']
                    out[count] = lvl[il]['e']
    plt.plot(atoms+1,out*const, col[kount]+'.',label=lab)
    plt.yscale('log')
    plt.xlabel('Atomic number Z')
    plt.ylabel('Level energy')
    plt.xticks(atoms)
    plt.title(r" levels of "+dp.dipall.atomname(sequence)+' sequence, ground state 2S2 1SE 0')
    plt.legend()

#
# ionization potential
#

plt.savefig('fig_isos41.png')
plt.show()
plt.close()
# 



levellab=['2S 2P 3PO 1','2S 2P 1PO 1','2S 3P 1PO 1']
const=1.
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

plt.savefig('fig_isos42.png')
plt.show()
plt.close()



