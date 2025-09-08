######################################################################

def uv(atom, plasma):
    #
    #  Returns  Rybicki Hummer U and V between levels i,
    # ip and at angles and frequencies mu nu,
    # for one atom object, temperature-dependent.
    # keys  'q','uji','uij','vji','vij' are added to bb and bf
    # for later use
    #  RH92 eqs 2.3
    #
    lvl=atom['lvl']
    bb=atom['bb']
    nbb=len(bb)
    bf=atom['bf']
    nbf=len(bf)
    #
    # RH92 eqs 32-34
    #
    # line frequencies in  units of cm/sec, +/- 180 km/s
    #
    x=np.array()[120,60,30,15,8,6,5,4,3,2.5,2,1.5, 1.]*2.e5)
    x=[-x,0 x[::-1]]

    for kr in range(0,nbb):
        i=bb['lo']
        j=bb['hi']
        a=1./ltime(i) + 1./ltime(j)
        nul = (lvl[j]-lvl[i])*cc *( 1. +x/cc) # Hz
        phi = voigt(a, x)

        u = aji*plasma.phi *  hh*nul/4./pi
        bb[kr]['q']=nul
        bb[kr]['uji']=u
        bb[kr]['uij']=0.*u

        bb[kr]['vji']= bji*hh*nul/4/pi * plasma.phi
        bb[kr]['vij'] = bij/bji * bb[kr]['vji']

        atom['bb'] = bb

    for kr in range(0,nbf):

        i=bf['lo']
        j=bf['hi']

        saha= (lvl[i]['g']/lvl[j]['g']) * (h*h/2/pi/kb/plasma.te)**1.5
        * np.exp((lvl[j]['e']-lvl[i]['e'])*hh/bk/plasma.te)

        nu=cc/bf['lambda']
        bf[kr]['q']=nu
        sigma=cc/bf['sigma']

        bf[kr]['uji']=2*hh*nu *(nu/cc)**2 * sigma * saha * np.exp(-hh*nu/kb/plasma.te)
        bf[kr]['uij']=bf[kr]['uji']

        bf[kr]['vji'] = sigma * saha * np.exp(-hh*nu/kb/plasma.te)
        bf[kr]['vij']= sigma

        atom['bf'] = bf

    return atom

######################################################################
def meld(atoms):
    #
    #  returns q,uji,uoj,vji,vij arrays agnostic to atom, functions of
    #  frequency alone.  In principle should also be a function
    #  of atmos.mu  The atom structures are updated.
    #
    count=0
    for ia in range(0,len(atoms)):
        atom=atoms([ia])
        atom=uv(atom)  # add vji,vij et to atom
        bb=atom['bb']
        bf=atom['bf']
        if(count eq 0):  define output array to be appended
            kr=0
            nu=np.array([])
            uji=np.array([])
            uij=np.array([])
            vji=np.array([])
            vij=np.array([])
            count+=1

        for kr=1,len(bb):
            q.append(  np.array(bb[kr]['q']   ))
            uji.append(np.array(bb[kr]['uji'] ))
            uij.append(np.array(bb[kr]['uij'] ))
            vji.append(np.array(bb[kr]['vji'] ))
            vij.append(np.array(bb[kr]['vij'] ))

            q.append(  np.array(bf[kr]['q'])    )
            h
            uji.append(np.array(bf[kr]['uji'] ) )
            uij.append(np.array(bf[kr]['uij'] ) )
            vji.append(np.array(bf[kr]['vji'] ) )
            vij.append(np.array(bf[kr]['vij'] ) )
        # Update each atom and then atoms
        atom['bb']=bb
        atom['bf']=bf
        atoms[ia]=atom
        #
        # unique, sorted indices
        #
    s=q.argsort()
    uji=uji[s]
    uij=uij[s]
    vji=vji[s]
    vij=vij[s]
    q,u= np.unique(q[s],return_index=True)
    print(len(q), 'unique frequencies among the active atoms')
    #
    # return atoms and the list of frequencies and uv data as fn frequency
    #
    return atoms, q

######################################################################
def etachi(atom):
    #
    #  emission and absorption coefficients belonging to transitions
    #  within one atom
    #  the populations are assumed to be stored in lvl['pop']
    #  RH92 eq. 2.5
    #
    lvl=atom['lvl']
    pop=lvl['pop']
    bb=atom['bb']
    nbb=len(bb)
    bf=atom['bf']
    nbf=len(bf)
    #
    for kr in range(0,nbb):
        lp=bb['lo']
        l=bb['hi']
        # emission coefficient eq RH92 2.5
        eta= lvl[l]['pop']*uji[kr]
        chi= lvl[lp]['pop']*vij[kr] -  lvl[l]['pop']*vji[kr]
        bb[kr]['eta']=eta
        bb[kr]['chi']=chi

    for kr in range(nbb,nbb+nbf):
        lp=bf['lo']
        l=bf['hi']
        # emission coefficient eq RH92 2.5
        eta= lvl[l]['pop']*uji[kr]
        chi= lvl[lp]['pop']*vij[kr] -  lvl[l]['pop']*vji[kr]
        bf[kr]['eta']=eta
        bf[kr]['chi']=chi

    atom['bb']=bb
    atom['bf']=bf
    return atom

######################################################################
def totaletachi(atoms,plasma):
    #
    # total opacity and emissivity returned as a function of
    # frequency (and later angle)
    # we must assign u and v to each frequency and just sum
    # opacity
    # RH92 eqs 2.6 and 2.7
    # first get all frequencies in variable nu
    #
    atom1,nu,uji,uij,vji,vij =uv(atom[0])  # add vji,vijc et to atom
    #
    # background opacity and emissivity chi and eta
    #
    chi=nu*0. + plasma.hminus(plasma.nh,plasma.pe,nu)
    eta=chi*planck(nu,plasma.te)
    #
    #
    #
    for ia in range(0,len(atoms)):
        atom=atoms([ia])
        bb=atom['bb']
        bf=atom['bf']
        achi+=bb['chi']
        aeta+=bb['eta']
        #
        # index = indices in nu corresponding to those in bb
        #
        index=find_indices(nu,bb['nu'])
        eta[index]=achi
        chi[index]=aeta
        index=find_indices(nu,bf['nu'])
        eta[index]=achi
        chi[index]=aeta
    return eta, chi  # emissivity and opacity as a function of nu

######################################################################
def find_indices(big, small):
    #
    # returns indices of array big corresponding to small
    #
    from bisect import bisect_left, bisect_right
    #
    inds = []
    sind = np.argsort(big)
    sbig = big[sind]
    for i in range(len(small)):
        i1 = bisect_left(sbig, small[i])
        i2 = bisect_right(sbig, small[i])
        try:
            inds.append(sind[i1:i2][0])
        except IndexError:
            pass
    return inds
