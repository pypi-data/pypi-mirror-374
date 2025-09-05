import numpy as np
from numpy.matlib import repmat,randn

def addnoise(yinp,ysiginp,nmc=10000,distrib='normal'):

	#      function ymc = createmcdata(y,ysig,nmc,distrib)
	#
	# Creates a matrix ymc of nmc vectors with the mean values of y but with
	# added random noise of standard deviation ysig. 
	#
	#     y       data vector
	#     ysig    standard deviation vector (same length as y)
	#     nmc     number of Monte Carlo copies
	#     distrib 'norm'/'normal' gives normal distribution
	#             'lognorm'/'lognormal' give lognormal distribution (useful for example 
	#             if negative results are unphysical)
	#
	#
	#  You might want to initialize the random number generator in forehand.
	#

	yinp = np.asarray(yinp)
	ysiginp = np.asarray(ysiginp)
	if np.ndim(yinp)>1 or np.ndim(ysiginp)>1:
		raise Exception('y and ysig must not have higher dimension than 1.')
	if np.size(ysiginp) == 1:
		ysiginp = ysiginp*np.ones(np.size(yinp))  #If ysiginp is a scalar, turn it into a vector with identical elements
	if np.size(yinp) != np.size(ysiginp):
		raise Exception('y and ysig must have the same length.')

	n=np.size(yinp)
	y=yinp.reshape((1,n))
	ysig=ysiginp.reshape((1,n))
	if distrib.lower() in ('norm' ,'normal'):
		
		return np.array(repmat(y,nmc,1)) + np.array(repmat(ysig,nmc,1))*np.array(randn(nmc,n))
	elif  distrib.lower() in ('lognorm','lognormal'):
			mu = np.log(y**2/np.sqrt(ysig**2+y**2))  # mu of lognormal dist
			sigma = np.sqrt(np.log(ysig**2/y**2+1))  # sigma of lognormal dist
			return np.exp(np.array(randn(nmc,n))*np.array(repmat(sigma,nmc,1)) + np.array(repmat(mu,nmc,1)))
	else:
		raise Exception('Distribution named "' + distrib + '" is not recognized.')


def linreg(xinp, yinp, plot = False):
	#This is the new (2024) weighted-fit version (similar to MATLAB linregmc) that only handles linear fits
	#and does NOT do confidence intervals, as these can be done by mcerrconf
	
    #Performs linear fitting ax+b=y with error analysis 
    #using a Monte Carlo approach.
    
    #Input arguments:
    #  x : a NX x N matrix: the NX data sets of x values (N data points)
    #  y : a NY x N matrix: the NY data sets of y values (N data points)
    #      NX and NY need not be the same. In particular one may use a
    #      single data set (without added noise) for one of them.
    #      The number of fits equals max(NX,NY) and if there are less data
    #      sets for one of x or y, they are just cyclically reused.
    #Return values:
    #  pp    (2 elements): single-fit value of each parameter (can be used as the result)
    #  psig  (2 elements): standard deviation of each parameter
    #  pchi  : probability of chi>chi0
    #  pmc   : a NX x (n+1) maxtrix, the fitted parameters for all data sets
	

    if np.ndim(xinp) == 1:
        x=xinp.reshape((1,np.size(xinp)))
    else:
        x= xinp
    if np.ndim(yinp) == 1:
        y=yinp.reshape((1,np.size(yinp)))
    else:
        y=yinp
    if np.size(x,1) != np.size(y,1):
        raise Exception('Number of columns in x and y must be equal')
    N=np.size(x,1)
    n=1 #always linear fit

	#Perform single fit to get the base chi2 value
    xs=np.median(x, axis=0)
    ys=np.median(y, axis=0)   #Reproduces original data points independent of distribution
    sig=np.std(x, axis=0)+np.std(y, axis=0)  #This only makes sense if either x or y is a single set

    Xt=np.stack((xs, np.ones(N)), axis=1)
    X=np.stack((xs/sig, np.ones(N)/sig), axis=1)
    Y=ys/sig
    pp=np.linalg.lstsq(X,Y, rcond=None)[0]    
    chi2 = sum((Y - np.matmul(X,pp))**2)
    subtract=ys - np.matmul(Xt,pp)


    xn=np.size(x,0)
    yn=np.size(y,0)
    nmc = max(xn,yn)
    pmc = np.zeros((nmc,n+1)) 
    chi2mc = np.zeros(nmc)
    for i in range(nmc):
        X=np.stack((x[i%xn,:]/sig,np.ones(N)/sig),axis=1)
        Y=(y[i%yn,:]-subtract)/sig
        p=np.linalg.lstsq(X,Y, rcond=None)[0] 
        pmc[i,:]=p
        chi2mc[i] = sum((Y - np.matmul(X,p))**2)

    pmean = np.mean(pmc,0)    #This is not used, as the single fit (pp) is returned for compatibility with the MATLAB script
    psig = np.std(pmc,0)
    
    #Compute pchi2
    pchi2=sum(chi2mc>chi2)/nmc

    if plot:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 1, figsize=(4, 2))
        counts,*_=ax.hist(chi2mc,bins=50)
        ycent=0.5*max(counts)
        ax.plot([chi2,chi2],[0,ycent],'r-')
        ax.set_yticks([])
        ax.set_xlabel(r"$\chi^2$")
        plt.show()
        
    return (pp,psig,pchi2,pmc)



def confidence(X, level=0.683, plot=False):
    #
    # Statistical analysis of the data in matrix X.
    # It is assumed that the number of data points are large; all properties
    # are calculated from the data itself. 
    #
    #     X       data matrix. Data in columns. For example, if X contains data
    #             from two measurements, data for measurement 1 is in column 1
    #             and measurement 2 in columns 2.
    #             If only one column, a 1d-array is also acceptable
    #     level   confidence limit of error in err. If not specified, level =
    #             0.683 is default.
	#     plot    an optional boolean specifying whether to plot histograms for each column
	#             where a general statistic is shown as a red errorbar (median +/- stdev)
    #             and the confidence intervals are shown with black lines.
	#             The red markers at the bottom show the simpler (median +/- err) 
	#             interval which should normally coincide with the confidence interval
	#             unless the distribution is skew (in which case the confidence interval is more reliable).
	#             If X has exactly two columns, a scatter plot showing possible correlation between
	#             the two columns is also produced.
    #
    # Returns a tuple (err, confint) where
    #     err            Error in the columns based on selected confidence limit.
    #     confint        A list of tuples (low, high), the confidence interval for each input column
	#                    (pconf*100% of values are found within this interval around median) 
	#                    If the input X was a 1d-array, a single tuple is returned instead of a list

    onedim = (np.ndim(X) == 1)
    
    if onedim:  #convert to matrix, then convert back to onedim at the end
        X=X.reshape((np.size(X),1))

    if level <= 0 or level >= 1:
        raise Exception("levvel must be 0 < level < 1.")

    if np.size(X,1) > np.size(X,0):
        print("Warning. It appears that your data is not placed column-wise.")

    N = np.size(X,0) #number of data points
    n = np.size(X,1)  #number of dimensions (columns)
    
    # GUM recommendation. ncut is the complement to pconf, ie the 1-pconf
    # fraction of points.
    #ncut = floor((N - floor(level*N+0.5) + 1)/2);   
    
    median = np.median(X,0)
    sig = np.std(X,0)
    absdiff = abs(X-np.mean(X,0)) #Absolute difference to mean value
    plow = np.zeros(n)
    phigh = np.zeros(n)
    err = np.zeros(n)
    for j in range(n):
        tmp=np.sort(X[:,j])
        plow[j]=tmp[round(max(1,0.5*(1-level)*N))-1]
        phigh[j]=tmp[round(min(N,1-0.5*(1-level)*N))-1]
        tmp=np.sort(absdiff[:,j])
        err[j]=tmp[round(min(N,level*N))-1]

    if plot:
        import matplotlib.pyplot as plt
        import matplotlib.gridspec as gridspec
        nvar=np.size(X,1)
        if nvar==2: #Exactly two parameters so produce a scatter plot and histograms
            fig = plt.figure(figsize=(8, 4.8))
            gs = gridspec.GridSpec(2, 2, width_ratios=[1.5, 1], height_ratios=[1, 1])
            # Left square spans both rows
            ax_left = fig.add_subplot(gs[:, 0])
            axes = [fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, 1])]
            ax_left.set_aspect('equal')
            ax_left.scatter(X[:,0],X[:,1],s=0.1)
            ax_left.set_xlabel('a')
            ax_left.set_ylabel('b')
            ax_left.plot([plow[0],plow[0]],[np.min(X[:,1]),np.max(X[:,1])],'k--')
            ax_left.plot([phigh[0],phigh[0]],[np.min(X[:,1]),np.max(X[:,1])],'k--')
            ax_left.plot([np.min(X[:,0]),np.max(X[:,0])],[plow[1],plow[1]], 'k--')
            ax_left.plot([np.min(X[:,0]),np.max(X[:,0])],[phigh[1],phigh[1]], 'k--')
            
            ax_left.set_aspect(1.0/ax_left.get_data_ratio(), adjustable='box')
        else:  #only produce histograms
            fig, axes = plt.subplots(nrows=nvar, ncols=1, figsize=(4, 2*nvar))
            if nvar==1: axes=[axes] # fix stupid inconsistency in plt.subplots so that axes is always a list
        
        for i,ax in enumerate(axes):
            counts,*_=ax.hist(X[:,i], bins=50)
            ycent=0.5*max(counts)
            ax.errorbar(median[i],ycent,xerr=sig[i],fmt='ro',capsize=5)
            ax.plot([plow[i],plow[i]]  ,[0,0.8*ycent],'k--')
            ax.plot([phigh[i],phigh[i]],[0,0.8*ycent],'k--')
            ax.plot([median[i]-err[i], median[i]-err[i]], [0,0.1*ycent],'r-')
            ax.plot([median[i]+err[i], median[i]+err[i]], [0,0.1*ycent],'r-')
            ax.set_xlabel(chr(ord('a')+i))  #Name the variables a,b,c...
            ax.set_yticks([])

        plt.tight_layout()
        plt.show()
    
    if onedim:
        return (err[0], (plow[0], phigh[0])) #simply return scalars
    else:
        return (err, list(zip(plow, phigh)))


def linconf(xinp, yinp, ysig, nmc=10000, distrib='normal', level=0.683, ytransform=None, restransform=None):
	#
	#Performs the full Monte Carlo linear regression with confidence calculation.
	#by applying the following 5 steps in succession:
	#   addnoise to y values
	#   transform y values (skipped if ytransform==None)
	#   linreg (x,y)
	#   calculates a tuple of results from a,b   (skipped if restransform==None)
	#   confidence for each result

	#   For detailed description of parameters, see previous functions
	#   Returns (reslist, pchi2) where reslist is a list of (result, error, confidenceinterval) for each calculated result
	
	ymc=addnoise(yinp, ysig, nmc, distrib)
	if ytransform!=None:
		ymc = ytransform(ymc)
	pp,psig,pchi2,pmc=linreg(xinp,ymc)
	if restransform!=None:
		results=restransform(pp[0],pp[1])
		results_mc=restransform(pmc[:,0],pmc[:,1])
	else:
		results=(pp[0],pp[1])
		results_mc=(pmc[:,0],pmc[:,1])
	rlist=[]
	for r,rmc in zip(results,results_mc):
		perr,confint=confidence(rmc, level)
		rlist.append((r,perr,confint))
	return (rlist,pchi2)
