def feaurh(t,s):
    # Appendix A of RH91.   First part only.
    delta=np.ediff1d(t,to_begin=(t[1]-t[0]),to_end=(t[-1]-t[-2]))
    #
    index=np.linspace(1,len(t)-1,dtype=int)
    dt1=delta[index]
    dt=delta[index-1]
    a=2./dt1/(dt1+dt)
    b=1. + 2/(dt*dt1)
    c=2./dt/(dt1+dt)
    #
    #
    d=a*0.
    z=a*0.
    u=a*0.
    d[0]=c[0]/b[0]
    z[0]=s[0]/b[0]
    # Equations A2-A5
#    for i in index:
#        d[i]= c[i]/(b[i]-a[i]*d[i-1])
#        z[i]= (s[i]+a[i]*z[i-1])/(b[i]-a[i]*d[i-1])
#    u[-1]=0.
#    for i in index[::-1]:
#        u[i]=d[i]*u[i-1] + z[i]
#    u1= u*1.

    # Equations A6-A9

    h=-a+b-c
    h[0]=b[0]-c[0]
    f=1./d-1.
    h[-1]=-a[-1]+b[-1]
    f[0]=h[0]/c[0]
    z[0]=s[0]/b[0]
    for i in index:
        f[i]= (h[i] + ( a[i]*f[i-1])/ (1.+f[i-1]) )/c[i]
        z[i]= (s[i]+a[i]*z[i-1])/c[i]/(1.+f[i])

    print(f)
    print(h)
    print(z)
    u[-1]=0

    for i in index[::-1]:
        u[i]=u[i-1]/(1+f[i]) + z[i]
    #print(u/u1)  # MW
    return u




######################################################################

from matplotlib import pyplot as plt
import numpy as np
s=1+np.linspace(0,40)/10.
t=10.**(s-2)
print(t)
#
u=feaurh(t,s)
plt.plot(t,s)
plt.plot(t,u)
plt.show()
