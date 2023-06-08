import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def boxplot_vs_hist(feature,figsize=(12,8),bins=None,showstatsline=False):
    """
    Plots a boxplot and histogram of a feature in a column.
    
    Parameters
    feature : str 
    figsize : tuple, optional
    bins : int, optional 
    showstats : bool, optional  
    ----------
    """
    f, (ax_box2, ax_hist2) = plt.subplots(nrows=2,sharex=True,figsize=figsize,gridspec_kw = {"height_ratios": (.25, .75)})
    sns.boxplot(x=feature,ax=ax_box2,showmeans=True,color='r')
    sns.histplot(x=feature,ax=ax_hist2,bins=bins) if bins else sns.histplot(x=feature,ax=ax_hist2)
    if(showstatsline):
        ax_hist2.axvline(x=np.mean(feature),color='g',linestyle='--')
        ax_hist2.axvline(x=np.median(feature),color='r',linestyle=':')

def boxplots_vs_hists(df,nrow,ncol,features,figsize=(12,8),bins=None,showstatsline=False):
    """
    Plots a boxplot with given number of rows and columns and given columns of features in a dataframe.

    Parameters
    df : dataframe
    nrow : int
    ncol : int
    features : list
    figsize : tuple, optional
    bins : int, optional 
    showstats : bool, optional  
    ----------  
    """
    fig = plt.figure(figsize=figsize)
    fig.subplots_adjust(hspace=0.3)
    subfigs = fig.subfigures(nrow,ncol) 
    for i in range(nrow):
        for j in range(ncol):  
            subfigs[i,j].subplots(2,1,sharex=True, gridspec_kw = {"height_ratios": (.25, .75)})  
    
    for idx,subfig in enumerate(subfigs.flatten()) :
        sns.boxplot(x=df[features[idx]],showmeans=True,color='red',ax=subfig.axes[0])   
        sns.histplot(x=df[features[idx]],color='black',ax=subfig.axes[1],bins=bins) if bins else sns.histplot(x=df[features[idx]],color='black',ax=subfig.axes[1])
        subfig.axes[1].axvline(np.mean(df[features[idx]]),color='g',linestyle='--') 
        subfig.axes[1].axvline(np.median(df[features[idx]]),color='orange',linestyle='-')    



def encoder_function(keyOrValue,encoder_dict):
    """
    This function retursns key or value depending is which one is passed. Otherwise it returns given keyOrValue parameter.
    Dictionary keys and values must be unique.

    Parameters

    keyOrValue : str
    encoder_dict : dict
    """
    for (k,v) in encoder_dict.items():
        if(k==keyOrValue):
            return v
        if(v==keyOrValue):
            return k
    return keyOrValue

def add_barlabel(plotobject):
    """
    This function adds bar labels to a barplot.
    designed for plots created with seaborn objects interface
    make sure that the used Mark object is Bar() instead of Bars() 
    Parameters

    plotobject : barplot
    numberoflayers : int
    """
    axes = plotobject._figure.axes
    for j in range(len(axes)):
        ax0 = axes[j]
        ax0_containers = ax0.containers
        for i in range(len(ax0_containers)):
            cnt = ax0_containers[i]
            ax0.bar_label(cnt)