#Code by Stef Husken stef.husken@student.kuleuven.be
#Last update: 25/08/2025

#----------------------------------------------------------------------------------#
#Here the HeunC evaluation starts

def HeunC(q,alpha,gamma,delta,epsilon,x,Heun_proxco=1/20,Heun_proxinf_rel=1,Heun_cont_coef=0.2444,Heun_klimit=1000,Heun_optserterms=40,Heun_asympt_klimit=200,eps=1e-16,session=None):
    """This function evaluates the confluent Heun function. It has the same form as the matlab or mathematica HeunC functions.
    It solves x(x-1)y''+(gamma(x-1)+delta x+x(x-1)epsilon)y'+(alpha x-q)y=0. The input parameters are in order: q,alpha,gamma,delta,epsilon all complex numbers
    then x a complex number outside of (1,infty) the branch cut. The additional parameters are Heun_proxco to determine when to expand around x=1, Heun_proxinf_rel
    to determine when to expand around infty, Heun_cont_coef to determine the analytic continuation jump size, Heun_klimit the maximum terms taken in the series,
    Heun_optserterms the optimal amount of terms, Heun_asympt_klimit the maximum terms taken in the asymptotic series. The next parameter is the error manager eps.
    If eps<1e-16 it will use mpmath to evaluate the function with the required accuracy. It thus supports arbitrary precision. The last parameter is session.
    It defaults to None but one can insert a wolframmathematicasession here. If one does this, the HeunC function is evaluated using 128dps mathematica."""
    if session is not None:
        from mpmath import mp
        DPS=int(-mp.log10(eps)+2)
        val,dval=Heunwrapper(q,alpha,gamma,delta,epsilon,x,session,DPS)
    else:
        if eps!=1e-16: #radius of asymptotic expansion to assure this expansion can get enough precision
            R=findR(eps)
        else:
            R=39.598767480747480554558975 #hard coded for general form to not have as much calculation time
        #from positive import error
        if eps<1e-16:#if smaller than 1e-16 we use mpmath for arbitrary precision. We make sure everything is in mpmath format.
            from mpmath import mp, mpc,mpf
            mp.dps=int(-mp.log10(eps)+2) #adding 2 guard digits
            x=mpc(x)
            q=mpc(q)
            alpha=mpc(alpha)
            gamma=mpc(gamma)
            delta=mpc(delta)
            epsilon=mpc(epsilon)
            Heun_proxco=mpf(1)/20
            Heun_proxinf_rel=mpf(1)
            Heun_cont_coef=mpf(Heun_cont_coef)
            Heun_klimit=mpf(Heun_klimit)
            Heun_optserterms=mpf(Heun_optserterms)
            Heun_asympt_klimit=mpf(Heun_asympt_klimit)
            if x.imag==mpf(0) and x.real>=mpf(1): #we exclude branch cut
                error('HeunC: z belongs to the branch cut [1,infty)')
            if abs(x-mpf(1))<Heun_proxco: #if close to the singular point, we use this point as a starting point for the series
                val,dval=HeunCnear1(q,alpha,gamma,delta,epsilon,x,Heun_cont_coef,Heun_klimit,Heun_optserterms,eps)
            elif abs(epsilon)>mpf(1)/2 and abs(q)<mpf(2.5) and abs(x)>Heun_proxinf_rel*R/(eps+abs(epsilon)): #using asymptotic expansion
                val,dval=HeunCfaraway(q,alpha,gamma,delta,epsilon,x,Heun_optserterms,Heun_cont_coef,Heun_klimit,Heun_asympt_klimit,eps)
            else: #using expansion around 0
                val,dval=HeunC0(q,alpha,gamma,delta,epsilon,x,Heun_cont_coef,Heun_klimit,Heun_optserterms,eps)
        else:
            if x.imag==0 and x.real>=1: #we exclude branch cut
                error('HeunC: z belongs to the branch cut [1,infty)')
            if abs(x-1)<Heun_proxco: #if close to the singular point, we use this point as a starting point for the series
                val,dval=HeunCnear1(q,alpha,gamma,delta,epsilon,x,Heun_cont_coef,Heun_klimit,Heun_optserterms,eps)
            elif abs(epsilon)>1/2 and abs(q)<2.5 and abs(x)>Heun_proxinf_rel*R/(eps+abs(epsilon)): #using asymptotic expansion
                val,dval=HeunCfaraway(q,alpha,gamma,delta,epsilon,x,Heun_optserterms,Heun_cont_coef,Heun_klimit,Heun_asympt_klimit,eps)
            else: #using expansion around 0
                val,dval=HeunC0(q,alpha,gamma,delta,epsilon,x,Heun_cont_coef,Heun_klimit,Heun_optserterms,eps)
    return val,dval




def HeunC0(q,alpha,gamma,delta,epsilon,x,Heun_cont_coef=0.38,Heun_klimit=1000,Heun_optserterms=40,eps=1e-16):
    from mpmath import mp, mpf,mpc
    if eps<1e-16:
        mpaccurate=True
        mp.dps=int(-mp.log10(eps)+2)
        from mpmath import sign
    else:
        mpaccurate=False
        from numpy import sign
    if abs(x)<Heun_cont_coef:
        val,dval=HeunC00(q,alpha,gamma,delta,epsilon,x,Heun_klimit,eps)
    elif x.real>1 and ((x.imag<=x.real and x.imag>0) or (x.imag<0 and x.imag>=-x.real)):
        if mpaccurate:
            z1=mpf(1)+sign(x.imag)*mpc(1j)
        else:
            z1=1+sign(x.imag)*1j
        z0=Heun_cont_coef*z1
        H0,dH0=HeunC00(q,alpha,gamma,delta,epsilon,z0,Heun_klimit,eps)
        H1,dH1,R=HeunCconnect(q,alpha,gamma,delta,epsilon,z1,z0,H0,dH0,None,Heun_optserterms,Heun_cont_coef,Heun_klimit,eps)
        val,dval,_=HeunCconnect(q,alpha,gamma,delta,epsilon,x,z1,H1,dH1,R,Heun_optserterms,Heun_cont_coef,Heun_klimit,eps)
    else:
        z0 = Heun_cont_coef*x/abs(x)
        H0,dH0=HeunC00(q,alpha,gamma,delta,epsilon,z0,Heun_klimit,eps)
        val,dval,_=HeunCconnect(q,alpha,gamma,delta,epsilon,x,z0,H0,dH0,None,Heun_optserterms,Heun_cont_coef,Heun_klimit,eps)
    return val,dval





def HeunC00(q,alpha,gamma,delta,epsilon,x,Heun_klimit=1000,eps=1e-16):
    from mpmath import mp, mpf
    if eps<1e-16:
        mpaccurate=True
        mp.dps=int(-mp.log10(eps)+2)
    else:
        mpaccurate=False
    if x==0:
        if mpaccurate:
            val=mpf(1)
        else:
            val=1
        dval=-q/gamma
        return val,dval
    else: 
        ckm1=-x*q/gamma
        if mpaccurate:
            recur = lambda k,ckm1,ckm2: (ckm1*x*(-q+(mpf(k-1))*(gamma-epsilon+delta+mpf(k-2)))+ckm2*x**2*((mpf(k-2))*epsilon+alpha))/(mpf(k)*(gamma+mpf(k-1)))
            ckm2=mpf(1)
            ddval=mpf(0)
            ckm0=mpf(1)
            k=mpf(2)
        else:
            recur = lambda k,ckm1,ckm2: (ckm1*x*(-q+(k-1)*(gamma-epsilon+delta+k-2))+ckm2*x**2*((k-2)*epsilon+alpha))/(k*(gamma+k-1))
            ckm2=1
            ddval=0
            ckm0=1
            k=2
        vm2=mp.nan
        val=ckm1+ckm2
        vm1=val
        dval=-q/gamma
        dm1=dval
        while k<=Heun_klimit and (vm2!=vm1 or dm2!=dm1 or abs(ckm0)>eps):
            ckm0=recur(k,ckm1,ckm2)
            val=val+ckm0
            dval=dm1+k*ckm0/x
            ddval=ddval+k*(k-1)*ckm0/x**2
            ckm2=ckm1
            ckm1=ckm0
            vm2=vm1
            vm1=val
            dm2=dm1
            dm1=dval
            k=k+1
        return val,dval




def HeunCconnect(q,alpha,gamma,delta,epsilon,x,x0,H0,dH0,R=None,Heun_optserterms=40,Heun_cont_coef=0.38,Heun_klimit=1000,eps=1e-16):
    if eps<1e-16:
        from mpmath import exp,arg,mpf,mp
        mpaccurate=True
        mp.dps=int(-mp.log10(eps)+2)
        theta=arg(x-x0)
    else:
        mpaccurate=False
        from numpy import angle,exp
        theta=angle(x-x0)
    insearch=True
    if R==None:
        if mpaccurate:
            R=min(mpf(12)/(mpf(1)+abs(epsilon)),abs(x0),abs(x0-mpf(1)))*Heun_cont_coef
        else:
            R=min(12/(1+abs(epsilon)),abs(x0),abs(x0-1))*Heun_cont_coef
    Rtuned=False
    iter=1
    while not Rtuned:
        if abs(x-x0)<=R:
            x1=x
        else:
            x1=x0+R*exp(1j*theta)
        H1,dH1,err,numb=HeunCfromZ0(q,alpha,gamma,delta,epsilon,x1,x0,H0,dH0,Heun_klimit,eps)
        if mpaccurate:
            Rtuned=err<mpf(5)*eps and numb<Heun_optserterms or iter>5 or numb<=8
            if not Rtuned:
                R=R/max(err/(mpf(5)*eps),numb/Heun_optserterms)
        else:
            Rtuned=err<5*eps and numb<Heun_optserterms or iter>5 or numb<=8
            if not Rtuned:
                    R=R/max(err/(5*eps),numb/Heun_optserterms)
        insearch=not (Rtuned and x==x1)
        iter=iter+1
    x0=x1
    H0=H1
    dH0=dH1
    while insearch:
        R=min(R,abs(x0)*Heun_cont_coef,abs(x0-1)*Heun_cont_coef)
        if abs(x-x0)<=R:
            x1=x
            insearch=False
        else:
            x1=x0+R*exp(1j*theta)
        H0,dH0,err,numb=HeunCfromZ0(q,alpha,gamma,delta,epsilon,x1,x0,H0,dH0,Heun_klimit,eps)
        if insearch:
            R=Heun_optserterms*R/(numb+eps)
        x0=x1
    return H0,dH0,R





def HeunCfromZ0(q,alpha,gamma,delta,epsilon,x,x0,H0,dH0,Heun_klimit=1000,eps=1e-16):
    #from positive import error
    from mpmath import mp,sqrt,mpf
    R=min(abs(x0),abs(x0-1))
    if eps<1e-16:
        mpaccurate=True
        mp.dps=int(-mp.log10(eps)+2)
    else:
        mpaccurate=False
    if abs(x-x0)>=R:
        error('x is out of convergence radius')
    elif abs(x-1)<eps or abs(x0-1)<eps:
        error('x or x0 is too close to the singular points')
    elif x==x0:
        val=H0
        dval=dH0
        if mpaccurate:
            err=mpf(0)
            numb=mpf(0)
        else:
            err=0
            numb=0
    else:
        zeta=x-x0
        ckm3=H0
        ckm2=dH0*zeta
        if mpaccurate:
            recur = lambda k,ckm1,ckm2,ckm3: (ckm1*zeta*(mpf(k-1))*(epsilon*x0**2+(gamma-epsilon+delta+mpf(2)*(mpf(k-2)))*x0-gamma-mpf(k)+mpf(2))+ckm2*zeta**2*((mpf(2)*(mpf(k-2))*epsilon+alpha)*x0-q+(mpf(k-2))*(gamma-epsilon+delta+mpf(k-3)))+ckm3*zeta**3*((mpf(k-3))*epsilon+alpha))/(x0*(x0-mpf(1))*(mpf(1-k))*mpf(k))
            ckm1=recur(mpf(2),ckm2,ckm3,mpf(0))
            dm1=dH0+mpf(2)*ckm1/zeta
            ddval=mpf(2)*ckm1/zeta**2
            ckm0=mpf(1)
        else:
            recur = lambda k,ckm1,ckm2,ckm3: (ckm1*zeta*(k-1)*(epsilon*x0**2+(gamma-epsilon+delta+2*(k-2))*x0-gamma-k+2)+ckm2*zeta**2*((2*(k-2)*epsilon+alpha)*x0-q+(k-2)*(gamma-epsilon+delta+k-3))+ckm3*zeta**3*((k-3)*epsilon+alpha))/(x0*(x0-1)*(1-k)*k)
            ckm1=recur(2,ckm2,ckm3,0)
            dm1=dH0+2*ckm1/zeta
            ddval=2*ckm1/zeta**2
            ckm0=1
        val=ckm3+ckm2+ckm1 
        vm1=val
        vm2=mp.nan
        dm2=dH0
        dval=dm1
        k=3
        while k<=Heun_klimit and (vm2!=vm1 or dm2!=dm1 or abs(ckm0)>eps):
            ckm0=recur(k,ckm1,ckm2,ckm3)
            val=val+ckm0
            dval=dm1+k*ckm0/zeta
            ddval=ddval+k*(k-1)*ckm0/zeta**2
            ckm3=ckm2
            ckm2=ckm1
            ckm1=ckm0
            vm2=vm1
            vm1=val
            dm2=dm1
            dm1=dval
            k=k+1
        if mpaccurate:
            numb=mpf(k-1)
        else:
            numb=k-1
        if q-alpha*x!=0:
            if mpaccurate:
                val2=(x*(x-mpf(1))*ddval+(gamma*(x-mpf(1))+delta*x+epsilon*x*(x-mpf(1)))*dval )/(q-alpha*x)
            else:
                val2=(x*(x-1)*ddval+(gamma*(x-1)+delta*x+epsilon*x*(x-1))*dval )/(q-alpha*x)
            err1=abs(val-val2)
        else:
            err1=mp.inf
        if abs(q-alpha*x)<0.01: #is this valid????!!!! It seems it is, from numerical inspection
            err2=abs(ckm0)*sqrt(numb)+abs(val)*eps*numb
            err=min(err1,err2)
        else:
            err=err1
    return val,dval,err,numb





def HeunCnear1(q,alpha,gamma,delta,epsilon,x,Heun_cont_coef=0.38,Heun_klimit=1000,Heun_optserterms=40,eps=1e-16):
    if eps<1e-16:
        from mpmath import mp,mpf
        mp.dps=int(-mp.log10(eps)+2)
        val1f,dval1f=HeunC0(q-alpha,-alpha,delta,gamma,-epsilon,mpf(1)-x,Heun_cont_coef,Heun_klimit,Heun_optserterms,eps)
        val1s,dval1s=HeunCs0(q-alpha,-alpha,delta,gamma,-epsilon,mpf(1)-x,Heun_cont_coef,Heun_optserterms,Heun_klimit,eps)
    else:
        val1f,dval1f=HeunC0(q-alpha,-alpha,delta,gamma,-epsilon,1-x,Heun_cont_coef,Heun_klimit,Heun_optserterms,eps)
        val1s,dval1s=HeunCs0(q-alpha,-alpha,delta,gamma,-epsilon,1-x,Heun_cont_coef,Heun_optserterms,Heun_klimit,eps)
    m1,m2=HeunCjoin10(q,alpha,gamma,delta,epsilon,Heun_cont_coef,Heun_klimit,Heun_optserterms,eps)
    dval1f=-dval1f
    dval1s=-dval1s
    val=m1*val1f+m2*val1s
    dval=m1*dval1f+m2*dval1s
    return val,dval





def HeunCjoin10(q,alpha,gamma,delta,epsilon,Heun_cont_coef=0.38,Heun_klimit=1000,Heun_optserterms=40,eps=1e-16):
    if eps<1e-16:
        from mpmath import mp,mpf, matrix
        mpaccurate=True
        mp.dps=int(-mp.log10(eps)+2)
        joinpt=mpf(0.5)
    else:
        mpaccurate=False
        from numpy import array, linalg
        joinpt=0.5
    val0,dval0=HeunC0(q,alpha,gamma,delta,epsilon,joinpt,Heun_cont_coef,Heun_klimit,Heun_optserterms,eps)
    val0s,dval0s=HeunCs0(q,alpha,gamma,delta,epsilon,joinpt,Heun_cont_coef,Heun_optserterms,Heun_klimit,eps)
    val1,dval1=HeunC0(q-alpha,-alpha,delta,gamma,-epsilon,1-joinpt,Heun_cont_coef,Heun_klimit,Heun_optserterms,eps)
    dval1=-dval1
    val1s,dval1s=HeunCs0(q-alpha,-alpha,delta,gamma,-epsilon,1-joinpt,Heun_cont_coef,Heun_optserterms,Heun_klimit,eps)
    dval1s=-dval1s
    if mpaccurate:
        m=matrix([[val1,val1s],[dval1,dval1s]])
        b=matrix([[val0,val0s],[dval0,dval0s]])
        C10=m**(-1)*b
    else:
        m=array([[val1,val1s],[dval1,dval1s]])
        b=array([[val0,val0s],[dval0,dval0s]])
        C10=linalg.solve(m,b)
    m1=C10[0,0]
    m2=C10[1,0]
    return m1,m2





def HeunCs0(q,alpha,gamma,delta,epsilon,x,Heun_cont_coef=0.38,Heun_optserterms=40,Heun_klimit=1000,eps=1e-16):
    from mpmath import sign,mp,mpf,mpc
    if eps<1e-16:
        mpaccurate=True
        mp.dps=int(-mp.log10(eps)+2)
    else:
        mpaccurate=False
    if abs(x)<Heun_cont_coef:
        val,dval=HeunCs00(q,alpha,gamma,delta,epsilon,x,Heun_klimit,eps)
    elif x.real>1 and ((x.imag<=x.real and x.imag>0) or (x.imag<0 and x.imag>=-x.real)):
        if mpaccurate:
            x1=mpf(1)+sign(x.imag)*mpc(1j)
        else:
            x1=1+sign(x.imag)*1j
        x0=Heun_cont_coef*x1
        H0,dH0=HeunCs00(q,alpha,gamma,delta,epsilon,x0,Heun_klimit,eps)
        H1,dH1,R=HeunCconnect(q,alpha,gamma,delta,epsilon,x1,x0,H0,dH0,None,Heun_optserterms,Heun_cont_coef,Heun_klimit,eps)
        val,dval,_=HeunCconnect(q,alpha,gamma,delta,epsilon,x,x1,H1,dH1,R,Heun_optserterms,Heun_cont_coef,Heun_klimit,eps)
    else:
        x0=Heun_cont_coef*x/abs(x)
        H0,dH0=HeunCs00(q,alpha,gamma,delta,epsilon,x0,Heun_klimit,eps)
        val,dval,_=HeunCconnect(q,alpha,gamma,delta,epsilon,x,x0,H0,dH0,None,Heun_optserterms,Heun_cont_coef,Heun_klimit,eps)
    return val,dval





def HeunCs00(q,alpha,gamma,delta,epsilon,x,Heun_klimit=1000,eps=1e-16):
    from mpmath import mp,mpf
    if eps<1e-16:
        mpaccurate=True
        mp.dps=int(-mp.log10(eps)+2)
    else:
        mpaccurate=False
    if abs(gamma-1)<eps:
        return mp.nan,mp.nan
    else:
        if mpaccurate:
            H0,dH0=HeunC00(q+(gamma-mpf(1))*(delta-epsilon),alpha+epsilon*(mpf(1)-gamma),mpf(2)-gamma,delta,epsilon,x,Heun_klimit,eps)
            val=x**(mpf(1)-gamma)*H0
            dval=(mpf(1)-gamma)*x**(-gamma)*H0+x**(mpf(1)-gamma)*dH0
        else:
            H0,dH0=HeunC00(q+(gamma-1)*(delta-epsilon),alpha+epsilon*(1-gamma),2-gamma,delta,epsilon,x,Heun_klimit,eps)
            val=x**(1-gamma)*H0
            dval=(1-gamma)*x**(-gamma)*H0+x**(1-gamma)*dH0
        return val,dval





def HeunCfaraway(q,alpha,gamma,delta,epsilon,x,Heun_optserterms=40,Heun_cont_coef=0.38,Heun_klimit=1000,Heun_asympt_klimit=200,eps=1e-16):
    if eps<1e-16:
        from mpmath import mp,mpf,sign,exp,mpc,arg,matrix
        mpaccurate=True
        mp.dps=int(-mp.log10(eps)+2)
    else:
        mpaccurate=False
        from numpy import sign, angle, linalg, exp,array
    from mpmath import pi
    hs=sign(x.imag)
    if mpaccurate:
        aSt=mpc(1j)/epsilon
    else:
        aSt=1j/epsilon
    if hs*sign(aSt.imag)<0:
        aSt=-aSt
    if mpaccurate:
        diri=arg(aSt)
    else:
        diri=angle(aSt)
    if abs(diri)<eps:
        diri=eps*hs
    elif pi-abs(diri)<eps:
        diri=pi+eps*hs
    C0A,CsA=HeunCjoin0infA(q,alpha,gamma,delta,epsilon,diri,Heun_optserterms,Heun_cont_coef,Heun_klimit,Heun_asympt_klimit,eps)
    C0B,CsB=HeunCjoin0infA(q-epsilon*gamma,alpha-epsilon*(gamma+delta),gamma,delta,-epsilon,diri,Heun_optserterms,Heun_cont_coef,Heun_klimit,Heun_asympt_klimit,eps)
    if eps!=1e-16:
        R=findR(eps)
    else:
        R=39.598767480747480554558975
    if mpaccurate:
        infpt=max(mpf(1),R/(abs(epsilon)+eps))*x/abs(x)
    else:
        infpt=max(1,R/(abs(epsilon)+eps))*x/abs(x)
    if abs(x)>abs(infpt):
        valA,dvalA=HeunCinfA(q,alpha,gamma,delta,epsilon,x,Heun_asympt_klimit,eps)
        valB,dvalB=HeunCinfA(q-epsilon*gamma,alpha-epsilon*(gamma+delta),gamma,delta,-epsilon,x,Heun_asympt_klimit,eps)
    else:
        valinfA,dvalinfA=HeunCinfA(q,alpha,gamma,delta,epsilon,infpt,Heun_asympt_klimit,eps)
        valA,dvalA,_=HeunCconnect(q,alpha,gamma,delta,epsilon,x,infpt,valinfA,dvalinfA,None,Heun_optserterms,Heun_cont_coef,Heun_klimit,eps)
        valinfB,dvalinfB=HeunCinfA(q-epsilon*gamma,alpha-epsilon*(gamma+delta),gamma,delta,-epsilon,infpt,Heun_asympt_klimit,eps)
        valB,dvalB,_=HeunCconnect(q-epsilon*gamma,alpha-epsilon*(gamma+delta),gamma,delta,-epsilon,x,infpt,valinfB,dvalinfB,None,Heun_optserterms,Heun_cont_coef,Heun_klimit,eps)
    if mpaccurate:
        m=matrix([[C0A,CsA],[C0B,CsB]])
        m=m**(-1)
    else:
        m=array([[C0A,CsA],[C0B,CsB]])
        m=linalg.inv(m)
    val=m[0,0]*valA+m[0,1]*exp(-epsilon*x)*valB
    dval=m[0,0]*dvalA+m[0,1]*exp(-epsilon*x)*(-epsilon*valB+dvalB)
    return val,dval





def HeunCinfA(q,alpha,gamma,delta,epsilon,x,Heun_asympt_klimit=200,eps=1e-16):
    from mpmath import mp,mpf,sqrt
    if eps<1e-16:
        mp.dps=int(-mp.log10(eps)+2)
        recur1= lambda n,cnm1: cnm1*mpf(n)/(x*epsilon)*(mpf(1)+(-q+alpha/epsilon*(mpf(2)*mpf(n)-gamma-delta-mpf(1)+alpha/epsilon)+(gamma-epsilon+delta+mpf(1))*(mpf(1-n))+alpha-mpf(1))/mpf(n)**2)
        recur= lambda n,cnm1,cnm2: recur1(n,cnm1)+cnm2/(x**2*epsilon)*((mpf(n-2)+alpha/epsilon)*(gamma-mpf(n)+mpf(1)-alpha/epsilon))/mpf(n)
        cnm2=mpf(1)
        dnm2=mpf(0)
        numb=mpf(2)
    else:
        recur1= lambda n,cnm1: cnm1*n/(x*epsilon)*(1+(-q+alpha/epsilon*(2*n-gamma-delta-1+alpha/epsilon)+(gamma-epsilon+delta+1)*(1-n)+alpha-1)/n**2)
        recur= lambda n,cnm1,cnm2: recur1(n,cnm1)+cnm2/(x**2*epsilon)*((n-2+alpha/epsilon)*(gamma-n+1-alpha/epsilon))/n
        cnm2=1
        dnm2=0
        numb=2
    cnm3=mp.inf
    cnm1=recur1(1,cnm2)
    dnm3=mp.inf
    dnm1=-cnm1/x
    val=cnm2+cnm1
    dval=dnm1
    vm3=mp.nan
    vm2=mp.nan
    vm1=mp.nan
    vm0=val
    dvm3=mp.nan
    dvm2=mp.nan
    dvm1=mp.nan
    dvm0=dval
    growcn=False
    valstab=False
    growdn=False
    dvalstab=False
    while numb<=Heun_asympt_klimit and (abs(cnm2)>sqrt(eps) or not (growcn or valstab) or not (growdn or dvalstab)):
        cnm0=recur(numb,cnm1,cnm2)
        dnm0=-numb*cnm0/x
        val=val+cnm0
        dval=dval+dnm0
        numb=numb+1
        growcn=growcn or (abs(cnm0)>abs(cnm1) and abs(cnm1)>abs(cnm2) and abs(cnm2)>abs(cnm3))
        valstab=valstab or (vm3==vm2 and vm2==vm1 and vm1==val)
        growdn=growdn or (abs(dnm0)>abs(dnm1) and abs(dnm1)>abs(dnm2) and abs(dnm2)>abs(dnm3))
        dvalstab=dvalstab or (dvm3==dvm2 and dvm2==dvm1 and dvm1==dval)
        if abs(cnm2)>sqrt(eps) or not (growdn or valstab):
            cnm3=cnm2
            cnm2=cnm1
            cnm1=cnm0
            vm3=vm2
            vm2=vm1
            vm1=vm0
            vm0=val
        if abs(cnm2)>sqrt(eps) or not (growdn or dvalstab):
            dnm3=dnm2
            dnm2=dnm1
            dnm1=dnm0
            dvm3=dvm2
            dvm2=dvm1
            dvm1=dvm0
            dvm0=dval
    val=(-x)**(-alpha/epsilon)*vm3
    dval=(-x)**(-alpha/epsilon)*(dvm3-alpha/epsilon*vm3/x)
    return val,dval





def HeunCjoin0infA(q,alpha,gamma,delta,epsilon,theta,Heun_optserterms=40,Heun_cont_coef=0.38,Heun_klimit=1000,Heun_asympt_klimit=200,eps=1e-16):
    if eps<1e-16:
        from mpmath import exp,sign,matrix,mp,mpf,mpc
        mpaccurate=True
        mp.dps=int(-mp.log10(eps)+2)
    else:
        mpaccurate=False
        from numpy import exp, sign, array, linalg
    if eps!=1e-16:
        R=findR(eps)
    else:
        R=39.598767480747480554558975
    R0=R/(eps+abs(epsilon))
    if mpaccurate:
        temp=exp(mpc(1j)*theta)
        infpt=mpf(2)*R0*temp
        joinpt=mpc(1j)*min(mpf(1),R0)*sign(temp.imag)
    else:
        temp=exp(1j*theta)
        infpt=2*R0*temp
        joinpt=1j*min(1,R0)*sign(temp.imag)
    valinf,dvalinf=HeunCinfA(q,alpha,gamma,delta,epsilon,infpt,Heun_asympt_klimit,eps)
    valJinf,dvalJinf,_=HeunCconnect(q,alpha,gamma,delta,epsilon,joinpt,infpt,valinf,dvalinf,None,Heun_optserterms,Heun_cont_coef,Heun_klimit,eps)
    valJ0,dvalJ0=HeunC0(q,alpha,gamma,delta,epsilon,joinpt,Heun_cont_coef,Heun_klimit,Heun_optserterms,eps)
    valJs,dvalJs=HeunCs0(q,alpha,gamma,delta,epsilon,joinpt,Heun_cont_coef,Heun_optserterms,Heun_klimit,eps)
    if mpaccurate:
        m=matrix([[valJ0,valJs],[dvalJ0,dvalJs]])
        b=matrix([valJinf,dvalJinf])
        c=m**(-1)*b
    else:
        m=array([[valJ0,valJs],[dvalJ0,dvalJs]])
        b=array([valJinf,dvalJinf])
        c=linalg.solve(m,b)
    C0=c[0]
    Cs=c[1]
    return C0, Cs





def findR(eps=1e-16):
    from mpmath import log, mpf, mp, power
    mp.dps=int(-mp.log10(eps)+2)
    eps=mpf(eps)
    logeps=log(eps)
    R=-logeps
    fact=mpf(1)
    n=mpf(1)
    while True:
        n=n+mpf(1)
        fact=fact*n
        R0=R
        R=(log(fact)-logeps)/n
        if R>R0:
            break
    N=n-1
    R=power(fact/n/eps,mpf(1)/N)
    return R




#-----------------------------------------------------------#
#Here the section to find QNMs and QNM behaviour starts


def W(A,omega,a,s,m,eps=1e-16,session=None):
    """This function calculates the Wronskian of the angular part of the Teukolsky equation. It needs to vanish to determine the separation constant. The necessary
    parameters are in the correct order: separation constant A (2-element tuple of real part, imaginary part), omega (complex of mpc number) frequency, a=dimensionless spin
    (float or mpmath), s=spin (integer or mpmath), m angular momentum projection (integer or mpmath). The next parameter is the error manager eps.
    If eps<1e-16 it will use mpmath to evaluate the function with the required accuracy. It thus supports arbitrary precision. The last parameter is session.
    It defaults to None but one can insert a wolframmathematicasession here. If one does this, the HeunC function is evaluated using 128dps mathematica."""
    #from positive import HeunC
    if eps<1e-16:
        #for high accuracy we implement mpmath compatibility and define all the parameters as such. This is probably not needed (in the sense that
        #mpf(2) and those kind of things are probably overkill but we need to make sure).
        from mpmath import mp,mpc,mpf
        mpaccurate=True
        mp.dps=int(-mp.log10(eps)+2) #setting accuracy with guard digits
        omega=mpc(omega)
        a=mpf(a)
        s=mpf(s)
        m=mpf(m)
        A=mpf(A[0])+mpf(A[1])*mpc(1j)
        alphamin=mpf(4)*a*omega
        deltamin=mpf(4)*s*a*omega
        etamin=mpf(1)/mpf(2)*m**2-mpf(1)/mpf(2)*s**2-s-mpf(2)*m*a*omega-mpf(2)*s*a*omega-A-a**2*omega**2+mpf(2)*m*a*omega
        alphaplus=-mpf(4)*a*omega
        deltaplus=-mpf(4)*s*a*omega
        etaplus=mpf(1)/mpf(2)*m**2-mpf(1)/mpf(2)*s**2-s-mpf(2)*m*a*omega+mpf(2)*s*a*omega-A-a**2*omega**2+mpf(2)*m*a*omega
    else:
        mpaccurate=False
        A=A[0]+A[1]*1j
        alphamin=4*a*omega
        deltamin=4*s*a*omega
        etamin=1/2*m**2-1/2*s**2-s-2*m*a*omega-2*s*a*omega-A-a**2*omega**2+2*m*a*omega
        alphaplus=-4*a*omega
        deltaplus=-4*s*a*omega
        etaplus=1/2*m**2-1/2*s**2-s-2*m*a*omega+2*s*a*omega-A-a**2*omega**2+2*m*a*omega
    betamin=m-s
    gammamin=m+s
    betaplus=m+s
    gammaplus=m-s
    if mpaccurate:
        qmin=(mpf(1)+abs(betamin))*alphamin/mpf(2)-(mpf(1)+abs(gammamin))*abs(betamin)/mpf(2)-abs(gammamin)/mpf(2)-etamin
        qplus=(mpf(1)+abs(betaplus))*alphaplus/mpf(2)-(mpf(1)+abs(gammaplus))*abs(betaplus)/mpf(2)-abs(gammaplus)/mpf(2)-etaplus
        alphamatmin=(mpf(2)+abs(betamin)+abs(gammamin))*alphamin/mpf(2)+deltamin
        alphamatplus=(mpf(2)+abs(betaplus)+abs(gammaplus))*alphaplus/mpf(2)+deltaplus
        #after defining all the parameters and define them such that they fit into the matlab/mathematica/python conventions, we fill in the Heun functions
        Hmin,Hminprime=HeunC(qmin,alphamatmin,mpf(1)+abs(betamin),mpf(1)+abs(gammamin),alphamin,mpf(1)/mpf(2),eps=eps,session=session)
        Hplus,Hplusprime=HeunC(qplus,alphamatplus,mpf(1)+abs(betaplus),mpf(1)+abs(gammaplus),alphaplus,mpf(1)/mpf(2),eps=eps,session=session)
    else:
        qmin=(1+abs(betamin))*alphamin/2-(1+abs(gammamin))*abs(betamin)/2-abs(gammamin)/2-etamin
        qplus=(1+abs(betaplus))*alphaplus/2-(1+abs(gammaplus))*abs(betaplus)/2-abs(gammaplus)/2-etaplus
        alphamatmin=(2+abs(betamin)+abs(gammamin))*alphamin/2+deltamin
        alphamatplus=(2+abs(betaplus)+abs(gammaplus))*alphaplus/2+deltaplus
        #after defining all the parameters and define them such that they fit into the matlab/mathematica/python conventions, we fill in the Heun functions
        Hmin,Hminprime=HeunC(qmin,alphamatmin,1+abs(betamin),1+abs(gammamin),alphamin,0.5,eps=eps)
        Hplus,Hplusprime=HeunC(qplus,alphamatplus,1+abs(betaplus),1+abs(gammaplus),alphaplus,0.5,eps=eps)
    wronskian=Hmin*Hplusprime+Hplus*Hminprime
    return wronskian.real, wronskian.imag





def B(r,omega,a,s,m,A,eps=1e-16,session=None):
    """This function calculates the incoming at infinity parameter of the radial part of the Teukolsky equation. It needs to vanish to 
    determine the separation constant. The necessary parameters are in the correct order: r (radius to evaluate at), float or mpmath,
    omega (complex of mpc number) frequency, a=dimensionless spin (float or mpmath), s=spin (integer or mpmath), m angular momentum projection (integer or mpmath). 
    separation constant A (complex number of mpmath). The next parameter is the error manager eps. If eps<1e-16 
    it will use mpmath to evaluate the function with the required accuracy. It thus supports arbitrary precision. The last parameter is session.
    It defaults to None but one can insert a wolframmathematicasession here. If one does this, the HeunC function is evaluated using 128dps mathematica."""
    #from positive import HeunC
    if eps<1e-16:
        #for high accuracy we implement mpmath compatibility and define all the parameters as such. This is probably not needed (in the sense that
        #mpf(2) and those kind of things are probably overkill but we need to make sure).
        mpaccurate=True
        from mpmath import sqrt, mp, mpf,mpc
        mp.dps=int(-mp.log10(eps)+2) #setting accuracy with guard digits
        r=mpc(r)
        omega=mpc(omega)
        a=mpf(a)
        s=mpf(s)
        m=mpf(m)
        A=mpc(A)
        rp=mpf(1)+sqrt(mpf(1)-a**2)
        rm=mpf(1)-sqrt(mpf(1)-a**2)
        alpha=mpf(2)*mpc(1j)*omega*(rp-rm)
        beta=-s-(mpf(2)*mpc(1j)*omega*(rp**2+a**2)-mpf(2)*mpc(1j)*a*m)/(rp-rm)
        gamma=s-(mpf(2)*mpc(1j)*omega*(rm**2+a**2)-mpf(2)*mpc(1j)*a*m)/(rp-rm)
        delta=mpf(2)*(rm-rp)*omega*(s*mpc(1j)+(rm+rp)*omega)
        eta=mpf(2)*mpc(1j)*s*omega*rp-mpf(1)/mpf(2)*s**2-s-A-a**2*omega**2+mpf(2)*a*m*omega-mpf(2)*(omega*(rp**2+a**2)-a*m)*((a**2+mpf(2)*rm*rp-rp**2)*omega-a*m)/(rp-rm)**2
        q=(mpf(1)+beta)*alpha/mpf(2)-(mpf(1)+gamma)*beta/mpf(2)-gamma/mpf(2)-eta
        alphamat=(mpf(2)+beta+gamma)*alpha/mpf(2)+delta
    else:
        mpaccurate=False
        from math import sqrt
        rp=1+sqrt(1-a**2)
        rm=1-sqrt(1-a**2)
        alpha=2*1j*omega*(rp-rm)
        beta=-s-(2*1j*omega*(rp**2+a**2)-2*1j*a*m)/(rp-rm)
        gamma=s-(2*1j*omega*(rm**2+a**2)-2*1j*a*m)/(rp-rm)
        delta=2*(rm-rp)*omega*(s*1j+(rm+rp)*omega)
        eta=2*1j*s*omega*rp-1/2*s**2-s-A-a**2*omega**2+2*a*m*omega-2*(omega*(rp**2+a**2)-a*m)*((a**2+2*rm*rp-rp**2)*omega-a*m)/(rp-rm)**2
        q=(1+beta)*alpha/2-(1+gamma)*beta/2-gamma/2-eta
        alphamat=(2+beta+gamma)*alpha/2+delta
    x=-(r-rp)/(rp-rm)
    if mpaccurate:
        #After calculating the parameters we calculate the HeunC evaluation and the Binc value.
        heun,_=HeunC(q,alphamat,mpf(1)+beta,mpf(1)+gamma,alpha,x,eps=eps,session=session)
        Binc=heun/(x**(-(beta+gamma+mpf(2))/mpf(2)-delta/alpha))
    else:
        #After calculating the parameters we calculate the HeunC evaluation and the Binc value.
        heun,_=HeunC(q,alphamat,1+beta,1+gamma,alpha,x,eps=eps)
        Binc=heun/(x**(-(beta+gamma+2)/2-delta/alpha))
    return Binc





def Zerofunction(omega,a,s,m,l,guess=None,epsilon=10**(-16),amp=30,eps=1e-16,session=None):
    """This function calculates the B incoming at radial infinity parameter corresponding to a certain frequency. It solves the wronskian condition first
   to determine A and then calculates the B value with the correct analytic continuation. Its zeroes determine the QNM frequencies. Its input parameters
   are in the correct order: omega (2-element tuple with real part and imaginary part) frequency, a (mpf or float) dimensionless spin, s (integer or mpf) spin,
   m (integer or mpf) angular momentum projection, l (mpf or integer) angular momentum, guess (mpc or complex) a guess for separation constant, epsilon (mpf or float)
   the analytic continuation parameter, amp (mpf or float) the amplitude of the r that is evaluated, the larger the better. The next parameter is the error manager eps. 
   If eps<1e-16 it will use mpmath to evaluate the function with the required accuracy. It thus supports arbitrary precision. The last parameter is session.
   It defaults to None but one can insert a wolframmathematicasession here. If one does this, the HeunC function is evaluated using 128dps mathematica."""
    if eps<1e-16:
        #for high accuracy we implement mpmath compatibility and define all the parameters as such. This is probably not needed (in the sense that
        #mpf(2) and those kind of things are probably overkill but we need to make sure).
        from mpmath import mp,mpf,exp,arg,pi,findroot,mpc
        mp.dps=int(-mp.log10(eps)+2) #setting accuracy with guard digits
        a=mpf(a)
        s=mpf(s)
        m=mpf(m)
        l=mpf(l)
        omega=mpf(omega[0])+mpf(omega[1])*mpc(1j)
        if a==0: #in Schwarzschild case there is no need to calculate the A because we know it
            A=l*(l+mpf(1))-s*(s+mpf(1))
        else:
            if guess==None: #if no guess is given one starts from Schwarzschild
                guess=l*(l+mpf(1))-s*(s+mpf(1))
            #finding the actual zero of the wronskian to solve for A
            f=lambda Areal, Aimag: W((Areal,Aimag),omega,a,s,m,eps,session)
            A=findroot(f,(guess.real, guess.imag),tol=eps)
            A=mpf(A[0])+mpf(A[1])*mpc(1j)
        #evaluation of B parameter
        zerofunction=B(mpf(amp)*exp(mpc(1j)*(pi/mpf(2)*(mpf(1)-mpf(epsilon))-arg(omega))),omega,a,s,m,A,eps=eps,session=session)
    else:
        from numpy import exp, angle
        from math import pi
        from scipy.optimize import root
        omega=omega[0]+omega[1]*1j
        if a==0: #in Schwarzschild case there is no need to calculate the A because we know it
            A=l*(l+1)-s*(s+1)
        else:
            if guess==None:  #if no guess is given one starts from Schwarzschild
                guess=l*(l+1)-s*(s+1)
            data=(omega,a,s,m)
            #finding the actual zero of the wronskian to solve for A
            A=root(W,[guess.real, guess.imag],args=data,tol=eps)
            A=A.x[0]+A.x[1]*1j
        #evaluation of B parameter
        zerofunction=B(amp*exp(1j*(pi/2*(1-epsilon)-angle(omega))),omega,a,s,m,A,eps=eps)
    return zerofunction.real,zerofunction.imag


def Radialevaluation(r,omega,a,s,m,A,eps=1e-32,verbose=False):
    """This function evaluates the radial wave equation and more specifically its asymptotic behaviour with respect to the expected asymptotic behaviour.
    It can do either asymptotic infinity (dividing away the expected behaviour) or asymptotic horizon (dividing away the expected behaviour) and it chooses automatically.
    The first input gives the radial function output and the second input gives the asymptotic behaviour divided away from this. This means the second output 
    should become a constant near the horizon or infinity. It only works for mpmath precisions!"""
    from mpmath import sqrt, mp, mpf,mpc,exp
    mp.dps=int(-mp.log10(eps)+2) #setting accuracy with guard digits
    r=mpc(r)
    omega=mpc(omega)
    a=mpf(a)
    s=mpf(s)
    m=mpf(m)
    A=mpc(A)
    rp=mpf(1)+sqrt(mpf(1)-a**2)
    rm=mpf(1)-sqrt(mpf(1)-a**2)
    alpha=mpf(2)*mpc(1j)*omega*(rp-rm)
    beta=-s-(mpf(2)*mpc(1j)*omega*(rp**2+a**2)-mpf(2)*mpc(1j)*a*m)/(rp-rm)
    gamma=s-(mpf(2)*mpc(1j)*omega*(rm**2+a**2)-mpf(2)*mpc(1j)*a*m)/(rp-rm)
    delta=mpf(2)*(rm-rp)*omega*(s*mpc(1j)+(rm+rp)*omega)
    eta=mpf(2)*mpc(1j)*s*omega*rp-mpf(1)/mpf(2)*s**2-s-A-a**2*omega**2+mpf(2)*a*m*omega-mpf(2)*(omega*(rp**2+a**2)-a*m)*((a**2+mpf(2)*rm*rp-rp**2)*omega-a*m)/(rp-rm)**2
    q=(mpf(1)+beta)*alpha/mpf(2)-(mpf(1)+gamma)*beta/mpf(2)-gamma/mpf(2)-eta
    alphamat=(mpf(2)+beta+gamma)*alpha/mpf(2)+delta
    x=-(r-rp)/(rp-rm)
    heun,_=HeunC(q,alphamat,mpf(1)+beta,mpf(1)+gamma,alpha,x,eps=eps)
    S=(-x)**((beta-s)/2)*(1-x)**((gamma-s)/2)*exp(alpha/2*x)
    functionvalue=heun*S
    if abs(r-rp)>1:
        if verbose:
            print('looking asymptotically near infinity')
        result=heun*S*r**(1+2*s-2*1j*omega)*exp(-1j*omega*r)
    elif r.real>=rp.real:
        if verbose:
            print('looking asymptotically near horizon')
        result=heun*S*(r-rp)**(s+1j*(2*omega*rp-m*a)/(rp-rm))
    return functionvalue,result


def determinantpoly(omega,a,s,m,Aguess,mode=None,eps=1e-16):
    """This function gives the determinant that should vanish if you want to have a polynomial solution. The inputs are in the correct order:
    omega (mpc or complex) frequency, a (mpf or float) dimensionless spin, s (mpf or integer) spin, m (mpf or integer) angular momentum projection,
    Aguess (mpc or complex) initial guess for separation constant, mode (+/-1) determines whether you are dealing with an omega_+ or omega_- mode respectively.
    The last parameter is the error manager eps. If eps<1e-16 it will use mpmath to evaluate the function with the required accuracy. It thus supports arbitrary precision."""
    from mpmath import mp
    if eps<1e-16:
        #for high accuracy we implement mpmath compatibility and define all the parameters as such. This is probably not needed (in the sense that
        #mpf(2) and those kind of things are probably overkill but we need to make sure).
        mpaccurate=True
        from mpmath import findroot,sqrt,zeros,mpf,mpc
        mp.dps=int(-mp.log10(eps)+2) #setting accuracy with guard digits
        omega=mpc(omega)
        a=mpf(a)
        s=mpf(s)
        m=mpf(m)
        Aguess=mpc(Aguess)
    else:
        mpaccurate=False
        from scipy.optimize import root
        from math import sqrt
        from numpy import zeros
        from numpy.linalg import det
    if mode==None: #if one doesnt tell what mode it is, we calculate it ourselves
        if round((4*1j*omega).real)-(4*1j*omega).real>1e-6: #not that important to be accurate because just a choice of omega_+ and omega_-.
            mode=1
        else:
            mode=-1
    data=(omega,a,s,m)
    if mpaccurate:
        #solving for the separation constant A
        f=lambda Areal, Aimag: W((Areal,Aimag),omega,a,s,m,eps)
        A=findroot(f,(Aguess.real, Aguess.imag),tol=eps)
        A=mpf(A[0])+mpf(A[1])*mpc(1j)
        #defining all parameters
        rp=mpf(1)+sqrt(mpf(1)-a**2)
        rm=mpf(1)-sqrt(mpf(1)-a**2)
        xi=-s-mpc(1j)*(mpf(2)*omega*rp-m*a)/(rp-rm)
        p=(rp-rm)*mpc(1j)*omega/mpf(2)
        if mode==1:
            eta=-mpc(1j)*(mpf(2)*omega*rm-m*a)/(rp-rm)
            Alpha=mpf(1)+mpf(2)*s+xi+eta-mpf(2)*mpc(1j)*omega
            Gamma=mpf(1)+s+mpf(2)*eta
            Delta=mpf(1)+s+mpf(2)*xi
            Sigma=A+a**2*omega**2-mpf(8)*omega**2+p*(mpf(2)*Alpha+Gamma-Delta)+(mpf(1)+s-(Gamma+Delta)/mpf(2))*(s+(Gamma+Delta)/mpf(2))
            q=round((mpf(2)*mpc(1j)*((mpf(2)*omega-m*a)/(rp-rm)+omega)-s-mpf(1)).real)
            if (Alpha+q).real>10**(-2): #in this case the values are too far of to meaningfully speak of a polynomial
                result=mp.nan
            else:
                #building the matrix of which we need to calculate the determinant
                matr=zeros(q+1)
                matr[0,0]=-Sigma
                matr[0,1]=-Gamma
                for i in range(2,q+1):
                    matr[i-1,i-1]=(mpf(i-1))*(mpf(i-2)-mpf(4)*p+Gamma+Delta)-Sigma
                    matr[i-1,i]=-mpf(i)*(mpf(i-1)+Gamma)
                    matr[i-1,i-2]=mpf(4)*p*(mpf(i-2)+Alpha)
                matr[q,q]=(mpf(q))*(mpf(q)-mpf(1)-mpf(4)*p+Gamma+Delta)-Sigma
                matr[q,q-1]=mpf(4)*p*(mpf(q)-mpf(1)+Alpha)
                #calculating the determinant
                result=mp.det(matr)
        elif mode==-1:
            eta=-s+mpc(1j)*(mpf(2)*omega*rm-m*a)/(rp-rm)
            Alpha=mpf(1)+mpf(2)*s+xi+eta-mpf(2)*mpc(1j)*omega
            Gamma=mpf(1)+s+mpf(2)*eta
            Delta=mpf(1)+s+mpf(2)*xi
            Sigma=A+a**2*omega**2-mpf(8)*omega**2+p*(mpf(2)*Alpha+Gamma-Delta)+(mpf(1)+s-(Gamma+Delta)/mpf(2))*(s+(Gamma+Delta)/mpf(2))
            q=round((mpf(4)*mpc(1j)*omega-mpf(1)).real)
            matr=zeros(q+1)
            #building the matrix of which we need to calculate the determinant
            matr[0,0]=-Sigma
            matr[0,1]=-Gamma
            for i in range(2,q+1):
                matr[i-1,i-1]=(mpf(i-1))*(mpf(i-2)-mpf(4)*p+Gamma+Delta)-Sigma
                matr[i-1,i]=-mpf(i)*(mpf(i-1)+Gamma)
                matr[i-1,i-2]=mpf(4)*p*(mpf(i-2)+Alpha)
            matr[q,q]=(mpf(q))*(mpf(q-1)-mpf(4)*p+Gamma+Delta)-Sigma
            matr[q,q-1]=mpf(4)*p*(mpf(q-1)+Alpha)
            #calculating the determinant
            result=mp.det(matr)
        else:
            print('mode must be +/-1')
    else:
        #solving for the separation constant
        A=root(W,(Aguess.real, Aguess.imag),args=data,tol=eps)
        A=A.x[0]+A.x[1]*1j
        #defining all parameters
        rp=1+sqrt(1-a**2)
        rm=1-sqrt(1-a**2)
        xi=-s-1j*(2*omega*rp-m*a)/(rp-rm)
        p=(rp-rm)*1j*omega/2
        if mode==1:
            eta=-1j*(2*omega*rm-m*a)/(rp-rm)
            Alpha=1+2*s+xi+eta-2*1j*omega
            Gamma=1+s+2*eta
            Delta=1+s+2*xi
            Sigma=A+a**2*omega**2-8*omega**2+p*(2*Alpha+Gamma-Delta)+(1+s-(Gamma+Delta)/2)*(s+(Gamma+Delta)/2)
            q=round((2*1j*((2*omega-m*a)/(rp-rm)+omega)-s-1).real)
            if (Alpha+q).real>10**(-2):
                result=mp.nan
            else:
                #building the matrix of which we need to calculate the determinant
                matr=zeros((q+1,q+1),dtype=complex)
                matr[0,0]=-Sigma
                matr[0,1]=-Gamma
                for i in range(2,q+1):
                    matr[i-1,i-1]=(i-1)*(i-2-4*p+Gamma+Delta)-Sigma
                    matr[i-1,i]=-i*(i-1+Gamma)
                    matr[i-1,i-2]=4*p*(i-2+Alpha)
                matr[q,q]=(q)*(q-1-4*p+Gamma+Delta)-Sigma
                matr[q,q-1]=4*p*(q-1+Alpha)
                #calculating the determinant
                result=det(matr)
        elif mode==-1:
            eta=-s+1j*(2*omega*rm-m*a)/(rp-rm)
            Alpha=1+2*s+xi+eta-2*1j*omega
            Gamma=1+s+2*eta
            Delta=1+s+2*xi
            Sigma=A+a**2*omega**2-8*omega**2+p*(2*Alpha+Gamma-Delta)+(1+s-(Gamma+Delta)/2)*(s+(Gamma+Delta)/2)
            q=round((4*1j*omega-1).real)
            #building the matrix of which we need to calculate the determinant
            matr=zeros((q+1,q+1),dtype=complex)
            matr[0,0]=-Sigma
            matr[0,1]=-Gamma
            for i in range(2,q+1):
                matr[i-1,i-1]=(i-1)*(i-2-4*p+Gamma+Delta)-Sigma
                matr[i-1,i]=-i*(i-1+Gamma)
                matr[i-1,i-2]=4*p*(i-2+Alpha)
            matr[q,q]=(q)*(q-1-4*p+Gamma+Delta)-Sigma
            matr[q,q-1]=4*p*(q-1+Alpha)
            #calculating the determinant
            result=det(matr)
        else:
            print('mode must be +/-1')
            result=mp.nan
    return result




def importing(accuracy=64):
    """This function imports the QNMs that have already been calculated with 60-65 digits accuracy and those calculated within floating point precision. 
    Note that there is NO AS mode but there is an unconventional mode. It gives us the first 21 QNMs of l=2 Schwarzschild. It does so in a list of mpc-elements."""
    from mpmath import mp,mpc,mpf
    mp.dps=accuracy
    from importlib import resources
    SBH_64 = []
    # Correct way to open bundled data. THE NEXT 15 LINES ARE AI GENERATED CODE!
    with resources.files("CHE_QNM.data").joinpath("qnm_frequencies.txt").open("r") as f:
        for line in f:
            real_str, imag_str = line.strip().split("\t")
            SBH_64.append(mpc(real_str, imag_str))
    loaded_qnms={}
    for l in range(2,4):
        for m in range(-l,l+1):
            for n in range(0,3):
                filename=f'qnm_rough_l{l}_m{m}_n{n}.txt'
                qnm_list=[]
                with resources.files("CHE_QNM.data").joinpath(filename).open("r") as f:
                    for line in f:
                        real_str,imag_str=line.strip().split('\t')
                        qnm_list.append(mpc(real_str,imag_str))
                    loaded_qnms[(l,m,n)]=qnm_list
    coefficients={}
    for n in range(42):
        filename=f'coefficients_n{n}.txt'
        coefs=[]
        with resources.files("CHE_QNM.data").joinpath(filename).open("r") as f:
            for line in f:
                real_str,imag_str=line.strip().split('\t')
                coefs.append(mpc(real_str,imag_str))
            coefficients[(2,2,n)]=coefs
    return SBH_64,loaded_qnms,coefficients



def QNM_Solver_HeunC(omega,a,s,m,l,guess=None,amp=30,epsilon=1e-16,eps=1e-16,session=None,start=1e-4):
    """This function explicitely calculates a QNM with required precision. One needs to give an initial guess as a starting point. The correct input parameters are
    in the correct order: omega (mpc or complex) the initial guess frequency. One finds a QNM closeby. a (mpf or float) dimensionless spin, s (mpf or integer) spin parameter,
    m (mpf or integer) angular momentum projection, l (mpf or integer) angular momentum, guess (mpc or complex) the initial guess for separation constant, if not
    given it automizes to Schwarzschild case. amp (mpf or float) how far in the complex r-plane one will evaluate asymptotic behaviour, epsilon (mpf or float)
    the analytic continuation parameter.  The next parameter is the error manager eps. If eps<1e-16 it will use mpmath to evaluate the function with the required accuracy. 
    It thus supports arbitrary precision. Furthermore there is the session parameter (if one wants to evaluate using mathematica. This does not work yet!!) and 
    has an wolframmathematicasession as input. The last parameter is start and determines basically how good you assume your starting guess is. It determines the second
    point in the secant method. Make it small for well approximating starting points (float or mpf)."""
    if eps<1e-16:
        from mpmath import findroot, mp,mpc,mpf
        mp.dps=int(-mp.log10(eps)+2)
        omega=mpc(omega)
        a=mpf(a)
        s=mpf(s)
        m=mpf(m)
        l=mpf(l)
        f=lambda omegareal, omegaimag: Zerofunction((omegareal,omegaimag),a,s,m,l,guess=guess,amp=amp,epsilon=epsilon,eps=eps,session=session)
        omega=findroot(f,(omega.real,omega.imag),(omega.real+start,omega.imag+start),tol=eps)
        residual=Zerofunction(omega,a,s,m,l,amp=amp,guess=guess,epsilon=epsilon,eps=eps,session=session)
        omega=omega[0,0]+mpc(1j)*omega[1,0]
    else:
        from scipy.optimize import root
        data=(a,s,m,l,guess,epsilon,amp,eps)
        omega=(omega.real,omega.imag)
        sol=root(Zerofunction,omega,data,tol=eps)
        omega=sol.x[0]+1j*sol.x[1]
        residual=Zerofunction(sol.x,a,s,m,l,guess=guess,amp=amp,epsilon=epsilon,eps=eps)
    return omega,residual



def py2mma(x,DPS=128):
    """This function takes an mpmath number and converts it to a string that can serve as input for mathematica."""
    from mpmath import mp,mpf,mpc
    mp.dps=128
    if isinstance(x,mpf):
        text=mp.nstr(x,DPS)
        return f"{text}`{DPS}"
    else:
        re=mp.nstr(x.real,DPS)
        im=mp.nstr(x.imag,DPS)
        return f"{re}`{DPS}+{im}`{DPS} I"




def Heunwrapper(q,alpha,gamma,delta,epsilon,x,session=None,DPS=128):
    """This function evaluates the confluent heun function in python by calling it in mathematica. You can give in an existing session if 
    you don't want to restart the kernel everytime."""
    from mpmath import mpc,mp,mpf
    from decimal import Decimal
    mp.dps=128
    q=py2mma(q,DPS)
    alpha=py2mma(alpha,DPS)
    gamma=py2mma(gamma,DPS)
    delta=py2mma(delta,DPS)
    epsilon=py2mma(epsilon,DPS)
    x=py2mma(x,DPS)
    if session==None:
        temp=None
        from wolframclient.evaluation import WolframLanguageSession
        from wolframclient.language import wl,wlexpr
        session=WolframLanguageSession()
    else:
        temp='exists'
        from wolframclient.language import wl,wlexpr
    expr1=wlexpr(f"N[HeunC[{q},{alpha},{gamma},{delta},{epsilon},{x}],{DPS}]")
    expr2=wlexpr(f"N[HeunCPrime[{q},{alpha},{gamma},{delta},{epsilon},{x}],{DPS}]")
    result1=session.evaluate(expr1)
    result2=session.evaluate(expr2)
    if isinstance(result1,Decimal):
        result1=mpf(str(result1))
    else:
        re,im=result1.args
        result1=mpc(str(re),str(im))
    if isinstance(result2,Decimal):
        result2=mpf(str(result2))
    else:
        re,im=result2.args
        result2=mpc(str(re),str(im))
    if temp==None:
        session.terminate()
    return result1,result2




#----------------------------------------#
#Here the Leaver code starts.


        #import matplotlib.pyplot as plt
from scipy.optimize import root #IMPORTANT NOTE. It would be more elegant to use mpmath.findroot as it directly works with complex numbers instead of modelling it as a 2D plane.
                                #For speed Scipy is faster and for accuracy it might be better to use mpmath (According to ChatGPT)
import math

#This part of the code defines the necessary functions that we will need to solve the Continued fraction problem from Leaver. It first imports the needed packages. Then makes a solver for schwarzschild and then for kerr
#code to calculate quasinormal modes of Black holes. We start with Schwartzschild. Based on Leaver 1985.

def CFinversion(RHO,eps,l,N,n_omega):
  """It calculates the Continued fraction residual (see Leaver 1985) for the Schwarzschild case, more specifically the residual of the n_omega'th inversion of it. This quantity should be zero for QNM's.
  Your inputs are in the correct order rho=-i\omega as a 2D-vector (you see your complex plane as a 2D vector space with real part = x-axis and imaginary part= y-axis),
   eps=s^2-1 an integer with s the spin of the field, the l parameter (integer), N the amount of elements in your continued fraction (integer) and n_omega the amount of inversions (integer and preferably equal to your root number)"""
  #In this part we calculate the Delta value of interest
  rho=RHO[0]+1j*RHO[1] #make your 2D vector a complex number again
  alpha=[n**2+(2*rho+2)*n+2*rho+1 for n in range(N+1)] #expansion coefficients like Leaver 1985, makes alpha_0 until alpha_N
  beta=[-(2*n**2+(8*rho+2)*n+8*rho**2+4*rho+l*(l+1)-eps) for n in range(N+1)] # same but beta
  gamma=[n**2+4*rho*n+4*rho**2-eps-1 for n in range(N+1)] #same but gamma
  #R=[-alpha[N]] # an expression taking the limit of the behaviour of R as indicated by (9) in Leaver
  intermediate=(-2*rho)**(1/2)
  if intermediate.real>0:
    R=alpha[N]*(-1+N**(-1/2)*(-2*rho)**(1/2)+(2*rho+3/4)*N**(-1)) #this initial value does not really matter, it will not really change the result that much.
  else:
    R=alpha[N]*(-1-N**(-1/2)*(-2*rho)**(1/2)+(2*rho+3/4)*N**(-1)) #this initial value does not really matter, it will not really change the result that much.
  G=beta[0] #for the inversion method
  for n in range(N-n_omega):
    #R.append(alpha[m-n-1]*gamma[m-n]/(beta[m-n]-R[-1])) #creates R_0 until R_m in reverse order (building the continued fraction bottom up)
    R=alpha[N-n-1]*gamma[N-n]/(beta[N-n]-R) #this is the infinite part of the continued fraction
  for n in range(n_omega):
    G=beta[n+1]-alpha[n]*gamma[n+1]/G #this is the n-th inversion of the continued fraction. The finite part
  Delta=G-R #This is the crucial quantity. This has to be zero as we know that if rho is an QNM that then it has to hold that beta_0=R_0
  return [Delta.real, Delta.imag]

def QNM_Solver_SBH_inversion(s,l,N,n,omega_0):
  """A solver for quasinormal modes, specified for the Schwarzschild black hole. It uses the n-inversion continued fraction method as it was first proposed by Leaver 1985.
  Your inputs are in the correct order the spin of the field (integer), the l parameter (integer), N the amount of elements in your continued fraction (integer), n the amount of inversions (integer) and your initial guess of the zero (complex number)."""
  if type(s) != int:
    raise TypeError("s must be an integer") #we do a little input validation
  elif type(l) != int:
    raise TypeError("l must be an integer")
  elif type(N) != int:
    raise TypeError("N must be an integer")
  elif type(n) != int:
    raise TypeError("n must be an integer")
  #elif type(omega_0) != complex and type(omega_0) !=float and type(omega_0) !=int:
    #raise TypeError("omega_0 must be a complex number, float or integer")
  else:
    rho_0=[omega_0.imag, -omega_0.real] #this is the frequency rho=-i\omega and will be used to find the QNM's
    eps=s**2-1 #spin parameter
    sol=root(CFinversion,rho_0,args=(eps,l,N,n)) #here we use the pretty much optimized root finder from scipi.optimize. It searches for the zero points on a 2D plane (thats how we look at our complex plane) in this case.
    #This is the reason we split it a 2D vector. This is because of the efficiency of scipy. You can also not do this decomposition and work directly in the complex plane using mpmath.findroot
    return -sol.x[1]+1j*sol.x[0] #It must return omega and not rho so we retransform our solution to omega



def CFKerrangular_inversion(A,omega,a,s,l,m,N):
  """It calculates the Continued fraction residual (see Leaver 1985) for the angular equation of the Kerr case. This quantity should be zero for QNM's.
  Your inputs are in the correct order A as a 2D-vector (you see your complex plane as a 2D vector space with real part = x-axis and imaginary part= y-axis),
  omega your guess of the QNM frequency (complex), a the spin of the field according to a=J/m (float),
   s an integer the spin of the field, the l parameter (integer), the m parameter (integer), N the amount of elements in your continued fraction (integer)."""
  #In this part we calculate the Delta value of interest for the angular continued fraction
  A=A[0]+1j*A[1] #make your 2D vector of A a complex number again
  k_1=1/2*abs(m-s) #numbers needed in the calculation
  k_2=1/2*abs(m+s)
  alpha=[-2*(n+1)*(n+2*k_1+1) for n in range(N+1)] #expansion coefficients like Leaver 1985, makes alpha_0 until alpha_N
  beta=[n*(n-1)+2*n*(k_1+k_2+1-2*a*omega)-(2*a*omega*(2*k_1+s+1)-(k_1+k_2)*(k_1+k_2+1))-(a**2*omega**2+s*(s+1)+A) for n in range(N+1)] # same but beta
  gamma=[2*a*omega*(n+k_1+k_2+s) for n in range(N+1)] #same but gamma
  R=-alpha[N]/2 #does not really matter that much i guess as taking R=0 or R=10^5 as starting value doesnt change anything, it is important for highly damped modes
  for n in range(N):
    #creates R_0 until R_m in reverse order (building the continued fraction bottom up)
    R=alpha[N-n-1]*gamma[N-n]/(beta[N-n]-R)
  Delta_angular=beta[0]-R #This is the crucial quantity. This has to be zero as we know that if omega is an QNM that then it has to hold that beta_0=R_0. this has to hold for both angular and radial part
  return [Delta_angular.real, Delta_angular.imag]

def CFKerrradial_inversion(A,omega,a,s,l,m,N,n_omega):
  """It calculates the n-th inverted Continued fraction residual th(see Leaver 1985) for the radial equation of the Kerr case. This quantity should be zero for QNM's.
  Your inputs are in the correct order the A parameter (complex), the omega parameter (complex), a the spin of the field according to a=J/m (float),
   s an integer the spin of the field, the l parameter (integer), the m parameter (integer), N the amount of elements in your continued fraction (integer) and n the amount of inversions of your continued fraction (integer)."""
  #In this part we calculate the Delta value of interest for the radial continued fraction using inversion
  b=math.sqrt(1-4*a**2) #numbers needed in the calculation
  c_0= 1-s-1j*omega-2*1j/b*(omega/2-a*m)
  c_1=-4+2*1j*omega*(2+b)+4*1j/b*(omega/2-a*m)
  c_2=s+3-3*1j*omega-2*1j/b*(omega/2-a*m)
  c_3=omega**2*(4+2*b-a**2)-2*a*m*omega-s-1+(2+b)*1j*omega-A+(4*omega+2*1j)/b*(omega/2-a*m)
  c_4=s+1-2*omega**2-(2*s+3)*1j*omega-(4*omega+2*1j)/b*(omega/2-a*m)
  alpha=[n**2+(c_0+1)*n+c_0 for n in range(N+1)] #expansion coefficients like Leaver 1985, makes alpha_0 until alpha_N
  beta=[-2*n**2+(c_1+2)*n+c_3 for n in range(N+1)] # same but beta
  gamma=[n**2+(c_2-3)*n+c_4-c_2+2 for n in range(N+1)] #same but gamma
  R=-alpha[N] #does not really matter that much i guess as taking R=0 or R=10^5 as starting value doesnt change anything, only for highly damped modes
  G=beta[0] #for the inversion method
  for n in range(N-n_omega):
    R=alpha[N-n-1]*gamma[N-n]/(beta[N-n]-R) #this is the infinite part of the continued fraction
  for n in range(n_omega):
    G=beta[n+1]-alpha[n]*gamma[n+1]/G #this is the n-th inversion of the continued fraction. The finite part
  Delta_radial=G-R #This is the crucial quantity. This has to be zero as we know that if omega is an QNM that then it has to hold that G=R. So this delta has to be zero
  return [Delta_radial.real, Delta_radial.imag]

def CFKerr_inversion(omega,A,a,s,l,m,N,n_omega):
  """This function calculates the n-th inverted continued fraction residual for the radial and angular part and puts the result into one 4D vector. The inputs are in the correct order
  omega as a 2D-vector (you see your complex plane as a 2D vector space with real part = x-axis and imaginary part= y-axis) containing the real and imaginary part of omega,
  A the 2D vector containing the real and complex value of A, a the spin of the field according to a=J/m (float),
   s an integer the spin of the field, the l parameter (integer), the m parameter (integer), N the amount of elements in your continued fraction (integer) and n the amount of inversions of your continued fraction (integer)."""
  #make your 2D vector of A a complex number again
  omega=omega[0]+1j*omega[1] #make your 2D vector of omega a complex number again
  SOL_INTER=root(CFKerrangular_inversion,A,args=(omega,a,s,l,m,N)) #this solves for A for the angular part as a function of omega
  A_inter=SOL_INTER.x[0]+1j*SOL_INTER.x[1] #so we see the angular part as an implicit function between A and omega and use it to solve for A as a function of omega
  delta_radial=CFKerrradial_inversion(A_inter,omega,a,s,l,m,N,n_omega) #this calculates the continued fraction residual for the radial part
  return [delta_radial[0], delta_radial[1]] #this puts it together into one end result. This 2D vector needs to be zero to have QNM's. This is a necessary and sufficient requirement

def QNM_Solver_Kerr_inversion(a,s,l,m,N,n,omega_0,A_0):
  """A solver for quasinormal modes, specified for the Kerr black hole. It uses the inverted continued fraction method as it was first proposed by Leaver 1985.
  Your inputs are in the correct order the spin of the field a=J/M (float), the spin of the field (integer), the l parameter (integer), the m parameter (integer),
   N the amount of elements in your continued fraction (integer), n the amount of inversions (integer) and your initial guess of the zero frequency and of the A seperation constant ( both complex number)."""
  if type(s) != int:
    raise TypeError("s must be an integer") #we do a little input validation
  elif type(a) !=float and type(a) !=int:
    raise TypeError("a must be a float (or an integer)")
  elif type(l) != int:
    raise TypeError("l must be an integer")
  elif type(N) != int:
    raise TypeError("N must be an integer")
  elif type(n) != int:
    raise TypeError("n must be an integer")
  #elif type(omega_0) != complex and type(omega_0) !=float and type(omega_0) !=int:
  #  raise TypeError("omega_0 must be a complex number, float or integer")
  #elif type(A_0) != complex and type(A_0) !=float and type(A_0) !=int:
  #  raise TypeError("A_0 must be a complex number, float or integer")
  else:
    omega=[omega_0.real,omega_0.imag] #this is the 2D vector describing omega used in calculating your continued fraction residual and will be used to find the QNM's
    A=[A_0.real,A_0.imag] #this is the 2D vector describing A used in calculating your continued fraction residual and will be used to find the QNM's
    sol=root(CFKerr_inversion,omega,args=(A,a,s,l,m,N,n)) #here we use the pretty much optimized root finder from scipi.optimize. It searches for the zero points on a 2D plane (thats how we look at our complex plane) in this case.
    #This is the reason we split it a 2D vector. This is because of the efficiency of scipy. You can also not do this decomposition and work directly in the complex plane using mpmath.findroot
    return sol.x[0]+1j*sol.x[1] #It must return omega and not A because we are not interested in the seperation constant here.

