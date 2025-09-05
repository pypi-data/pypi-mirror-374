stats_catalog=[
    dict(
        ticker='totret',
        name='Total Return',
        shortname='TotRet',
        description="full sample return",
        latex_expression='$\prod_{i=1}^N(1+r_i)-1$',
    ),
    dict(
        ticker='annret',
        name="Annualized Return",
        shortname='AnnRet',
        description="annualized mean return",
        latex_expression='$(12/N)\sum_{i=1}^Nr_i$',        
    ),
    
    dict(
        ticker='annretc',
        name="Compounded Annualized Return",
        shortname='AnnRet(c)',
        description="compounded annualized return",
        latex_expression='$(\prod_{i=1}^N(1+r_i))^{12/N}-1$',        
    ),

    dict(
        ticker='annvol',
        name='Annualized Volatility',
        shortname='AnnVol',
        description="annualized volatily",
        latex_expression="$\sqrt{12}\\times\mathbb E[(r_i-\\bar{r_i})^2]^{1/2}$",
    ),

    dict(
        ticker='maxddc',
        name='Max Drawdown',
        shortname='MaxDD',
        description='max loss (peak to trough)',
        latex_expression="$\\min_{1\leq s\leq t\leq N}\prod_{i=s}^t(1+r_i)-1$",
    ),

    dict(
        ticker='skewness',
        name='Skewness',
        shortname='Skewness',
        description="skewness",
        latex_expression='$\mathbb E[(\\frac{r_i-\mu}{\sigma})^3]$',
    ),

    dict(
        ticker='exckurt',
        name='Excess Kurtosis',
        shortname='Kurt(exc)',
        description="excess kurtosis",
        latex_expression='$\mathbb E[(\\frac{r_i-\mu}{\sigma})^4]-3$',
    ),

    dict(
        ticker='sharpe',
        name='Sharpe Ratio',
        shortname='Sharpe',
        latex_expression='AnnReturn/AnnVol'
    ),

    dict(
        ticker='sharpec',
        name='Sharpe Ratio (compounded)',
        shortname='SR(c)',
        latex_expression='AnnReturn(c)/AnnVol'
    ),


    dict(
        ticker='sharperf',
        name='Sharpe Ratio (riskfree)',
        shortname='SR(rf)',
        latex_expression='Sharpe(return-TBill3M)'
    ),

    dict(
        ticker="sharpeadj",
        name="Adjusted Sharpe Ratio",
        shortname="SR(adj)",
        latex_expression='$\operatorname{SR}(1 + (1/6) \cdot \operatorname{Skewness} \cdot \operatorname{SR} - (1/24)\operatorname{ExcKurt}\cdot \operatorname{SR}^2)$',
    ),

    
    dict(
        ticker='calmar',
        name='Calmar',
        shortname='Calmar',
        description="calmar ratio (36M)",
        latex_expression='AnnReturn(c)/MDD',
    ),
  
    dict(
        ticker='omega',
        name='Omega',
        shortname='Omega',
        description="omega ratio",
        latex_expression='$\mathbb E[r_i|r_i>0]/\mathbb E[|r_i||r_i<0]$ '
    ),

    dict(
        ticker='sortino',
        name='Sortino Ratio',
        shortname='Sortino',
        latex_expression='AnnRet/($\sqrt{12}\\times$DDEV)'
    ),

    dict(
        ticker='ddev',
        name='Downside Deviation',
        shortname='DDEV',
        latex_expression='$\mathbb E[\\min(0,r_i)^2]^{1/2}$',
    ),

    dict(
        ticker='hitratio',
        name='Hit Ratio',
        shortname='HR',
        description='proportion of positive returns',
        latex_expression="Prob(r_i≥0)",  
    ),

    dict(
        ticker='alpha',
        name='Annualized Alpha',
        shortname='Alpha',
        description="annualized alpha",
        latex_expression='$12\\times(\mathbb E[r_i]-\\beta\mathbb E[f_i])$',
    ),

    dict(
        ticker='beta',
        name='Beta',
        shortname='Beta',
        description="beta",
        latex_expression='$\operatorname{cov}(r_i,f_i)/\operatorname{var}(f_i)$',
    ),
    
    dict(
        ticker='corr',
        name='Correlation',
        shortname='Corr',
        description='Pearson correlation coefficient',
        latex_expression='$\operatorname{cov}(r_i,f_i)/(\operatorname{std}(r_i)\operatorname{std}(f_i))$',
    ),

    dict(
        ticker='r2',
        name='RSquared',
        shortname='R2',
        description='r squared',
        latex_expression='$\operatorname{var}[\epsilon_i]$',
    ),
    
]

stat_dict={
    item['ticker']:item 
    for item in stats_catalog
}


