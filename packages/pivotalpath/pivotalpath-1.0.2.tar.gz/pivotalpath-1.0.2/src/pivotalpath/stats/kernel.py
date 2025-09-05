import pandas as pd
import numpy as np
import pdb


def _zeroInsert(df):
    if "date" in df.columns.tolist():
        df=df.set_index("date")
        df.index.name="date"
        un_indexify=True
    else:
        un_indexify=False
    newrow=pd.DataFrame({k:[0] for k in df.columns},index=["0000-00"])
    df=pd.concat([newrow,df],axis=0)
    if un_indexify:
        df=df.reset_index().rename(columns={'index':'date'})
    return df

def _outputNull(df,title='stat'):
    return pd.DataFrame(pd.Series(index=df.columns,name=title))


    
def _nanAlign(df,base):
    try:
        base=pd.concat([base] * (df.shape[1]), axis=1, ignore_index=True)
        base.columns=df.columns    
        base[df.isnull()] = df.copy()
        df[base.isnull()] = base.copy()
        return df,base
    except:
        pass

    
def totret(df,**kwargs):
    return (1+df).prod(axis=0)-1

def annret(df,**kwargs):
    return 12*df.mean(axis=0)

def annretc(df,**kwargs):
    A=(1+df).prod(axis=0)
    B=df.notna().sum(axis=0)
    B[B==0]=np.nan
    return (A**(12/B))-1

def annvol(df,**kwargs):
    return np.sqrt(12)*df.std(axis=0,ddof=1)

def maxdd(df,**kwargs):
    nav=_zeroInsert(df).cumsum()
    peak=nav.expanding(1).max()
    return (nav-peak).iloc[1:].min(axis=0)

def maxddc(df,**kwargs):
    nav=(1+_zeroInsert(df)).cumprod()
    peak=nav.expanding(1).max()
    return ((nav/peak)-1.0).iloc[1:].min(axis=0)


def skewness(df,**kwargs):
    #scistats.skew(df,nan_policy='omit')
    sigma=df.std(axis=0,ddof=0)
    sigma[sigma==0]=np.nan
    df0=(df-df.mean(axis=0))/sigma
    return (df0**3).mean(axis=0)
    


def exckurt(df,**kwargs):
    # scistats.kurtosis(df,nan_policy='omit')
    sigma=df.std(axis=0,ddof=0)
    sigma[sigma==0]=np.nan
    df0=(df-df.mean(axis=0))/sigma
    return (df0**4).mean(axis=0)-3

def sharpe(df,**kwargs):
    R=12*df.mean(axis=0)
    V=np.sqrt(12)*df.std(axis=0,ddof=1)
    return R/V

def sharpec(df,**kwargs):
    A=(1+df).prod(axis=0)
    B=df.notna().sum(axis=0)
    B[B==0]=np.nan
    R=(A**(12/B))-1
    V=np.sqrt(12)*df.std(axis=0,ddof=1)
    return R/V

def sharperf(df,riskfree=None,**kwargs):
    if riskfree is None:
        riskfree=0
    if isinstance(riskfree,pd.DataFrame) and not riskfree.empty:
        riskfree=riskfree[riskfree.columns[0]]
    df=df.sub(riskfree,axis=0)
    R=12*df.mean(axis=0)
    V=np.sqrt(12)*df.std(axis=0,ddof=1)
    return R/V

def sharpeadj(df,base=None,**kwargs):
    R=12*df.mean(axis=0)
    V=np.sqrt(12)*df.std(axis=0,ddof=1)
    SR=R/V
    lambda_1=(1/6)*skewness(df)
    lambda_2=(1/24)*exckurt(df)
    adjustment_factor=1 + (lambda_1* SR) - (lambda_2* (SR**2))
    return SR * adjustment_factor

def calmar(df,lookback=36,**kwargs):
    # compute maxdd
    if len(df)>36:
        df=df.iloc[-lookback:]
    nav=(1+_zeroInsert(df)).cumprod()
    peak=nav.expanding(1).max()
    currDD=(nav/peak)-1.0
    maxDD=-currDD.iloc[1:].min(axis=0)
    maxDD[maxDD==0]=np.nan
    numPts=df.notna().sum()
    annRet=(((1+df).prod(min_count=1))**(12/numPts))-1
    out=annRet/maxDD
    #out[:]="n/d"
    #out[maxDD.isna()]="n/a (no drawdown)"
    return out

def omega(df,**kwargs):
    ypos=df.copy()
    ypos[ypos<=0]=np.nan
    yneg=df.copy()
    yneg[yneg>=0]=np.nan
    A=ypos.mean(axis=0)
    B=-yneg.mean(axis=0)
    return A/B

def sortino(df,**kwargs):
    # as on pivotalbase
    MAR=0
    ye=df-MAR
    yn=ye.clip(upper=0)
    exrt=ye.mean(axis=0)
    ddev=np.sqrt((yn**2).mean(axis=0))
    ddev[ddev==0]=np.nan
    return np.sqrt(12)*exrt/ddev


def ddev(df,**kwargs):
    yn=df.clip(upper=0)
    return np.sqrt((yn**2).mean(axis=0))

def hitratio(df,**kwargs): 
    A=(df>=0).sum(axis=0)
    B=df.notna().sum(axis=0)
    B[B==0]=np.nan
    return A/B

#=========================================

def alpha(df,base=None,**kwargs):
    if base is None:
        return _outputNull(df,title='alpha')    
    df,base=_nanAlign(df,base)
    ex=base.mean()
    ey=df.mean()
    base=base-ex
    df=df-ey
    exy=(base*df).mean()
    exx=(base**2).mean()
    exx[exx.abs()<1e-17]=np.nan
    beta=exy/exx
    alpha=ey-beta*ex
    return 12*alpha

def beta(df,base=None,**kwargs):
    if base is None:
        return _outputNull(df,title='beta')        
    df,base=_nanAlign(df,base)
    base=base-base.mean()
    df=df-df.mean()
    exy=(base*df).mean()
    exx=(base**2).mean()
    beta=exy/exx
    return beta

def corr(df, base=None, **kwargs):
    if base is None:
        return _outputNull(df, title='corr')
    if isinstance(base, pd.DataFrame):
        base = base[base.columns[0]]
    
    # Handle case where base is a scalar (float, int, etc.)
    if not isinstance(base, pd.Series):
        # If base is a scalar, we can't compute meaningful correlation
        return _outputNull(df, title='corr')
    
    # Convert to numeric if needed (handle object dtype)
    if df.dtypes.eq('object').any():
        df = df.apply(pd.to_numeric, errors='coerce')
    if base.dtype == 'object':
        base = pd.to_numeric(base, errors='coerce')
    
    # Ensure base has the same index as df
    aligned_base = base.reindex(df.index)
    
    # If aligned_base is all NaN, return null output
    if aligned_base.isnull().all():
        return _outputNull(df, title='corr')
    
    return df.corrwith(aligned_base)
       

def r2(df, base=None, **kwargs):
    if base is None:
        return _outputNull(df, title='r2')
    if isinstance(base, pd.DataFrame):
        base = base[base.columns[0]]
    
    # Handle case where base is a scalar (float, int, etc.)
    if not isinstance(base, pd.Series):
        return _outputNull(df, title='r2')
    
    # Convert to numeric if needed (handle object dtype)
    if df.dtypes.eq('object').any():
        df = df.apply(pd.to_numeric, errors='coerce')
    if base.dtype == 'object':
        base = pd.to_numeric(base, errors='coerce')
    
    # Use corrwith and square the result
    correlations = df.corrwith(base.reindex(df.index))
    return correlations**2

def numpts(df, **kwargs):
    return df.notna().sum(axis=0)

def currentvalue(df, **kwargs):
    return df.iloc[-1]

 

