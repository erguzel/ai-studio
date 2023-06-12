import seaborn as sns
import seaborn.objects as so
import matplotlib.pyplot as plt
import numpy as np
from exchelp.exception_helper import *

import aistudio.runtime.runtime_utils as ru
import aistudio.statistics.stats_utils as su

class paramatizable:
    def __init__(self,**params):
        for k,v in params.items():
            self.__dict__[k]=v            

    def __str__(self) -> str:
        return str(self.__dict__)

    def __repr__(self) -> str:
        return str(self.__dict__)

class MarkParam(paramatizable):
    def __init__(self,**params):
        super().__init__(**params)  



class Scale(paramatizable):
    def __init__(self,**params):
        super().__init__(**params)  

class Limit(paramatizable):
    def __init__(self,**params):
        super().__init__(**params)  

class Pair(paramatizable):
    def __init__(self,x=None, y=None, wrap=None, cross=True):
        self.x=x
        self.y=y
        self.wrap=wrap
        self.cross=cross
        super().__init__(x=x, y=y, wrap=wrap, cross=cross)

class Facet(paramatizable):
    """
    Equavalent of seaborn.objects.Plot.facet
    """
    def __init__(self, col = None,row=None,order = None,wrap = None):
        self.col = col
        self.row = row
        self.order = order
        self.wrap = wrap   
        super().__init__(col = col,row=row,order = order,wrap = wrap)   

def MONTH_NAMES():
    """
    returns a dict of sorted month names
    """
    return {1:'January', 2:'February', 3:'March', 4:'April', 5:'May', 6:'June', 7:'July', 8:'August', 9:'September', 10:'October', 11:'November', 12:'December'}
    

def WEEK_DAYS():
    """
    returns a dict of weekdays
    """
    return {1:'Monday', 2:'Tuesday', 3:'Wednesday', 4:'Thursday', 5:'Friday', 6:'Saturday', 7:'Sunday'}

def encoder_function(keyOrValue,encoder_dict):
    """
    This function retursns key or value depending is which one is passed. Otherwise it returns given keyOrValue parameter.  Dictionary keys and values must be unique.

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
    
    return fig

def add_barlabel(figure):
    """
    This function adds bar labels to a barplot.
    designed for plots created with seaborn objects api interface
    make sure that the used Mark object is Bar() instead of Bars() 
    Parameters

    plotobject : barplot
    numberoflayers : int
    """
    try:
        axes = figure.figure.axes
        for j in range(len(axes)):
            ax0 = axes[j]
            ax0_containers = ax0.containers
            for i in range(len(ax0_containers)):
                cnt = ax0_containers[i]
                ax0.bar_label(cnt)
        return figure
    except Exception as e:
        (
            CoverException(
            'Barlabel could not be added to the barplot',
            cause=e,
            logIt=True,
            shouldExit=True,
            dontThrow=True
            )
            .adddata('plotobject', figure)
            .adddata('__WARN__','Check number of (sub)figures and the number of axes. Make sure that the used Mark object is Bar() instead of Bars()')
            .act()
        )

def so_categoricals_vs_numeric(
        data,
        categoricals,
        numeric=None,
        griddimensions=None,
        markobjects=so.Bar(),
        statobjects=so.Agg(),
        moveobjects = None,
        scaleobjects = None,
        limitobjects = None,
        colors=None,
        linestyles=None,
        alphas = None,
        xlabel = None,
        ylabel=None,
        rowlabel = None,
        collabel=None,
        title=None,
        sharex = False,
        sharey = False,
        emptybackground=False,
        figsize=(12,12),
        addbarlabels = False,
        facets=Facet(row=None,col=None,order= None,wrap=None),
        masterlegend = True):
    """
    this function creates a continuous target variable versus given categories in a subplot grid. If no target variable is given, the target variable will be the mean of the categoricals.
    Funtion creates histogram(s) if given parameters are correct.

    Parameters
    dframe : dataframe of data
    categories : arraylike of category names in dataframe
    targetvar : str of target variable name in dataframe
    grid_dimensions : tuple of ints 
    nobackground : bool, optional False fue
    figsize : tuple, optional       
    mark_object : seaborn mark object, optional
    agg : str, optional

    """
    try:
        
        if(ru.is_array(numeric)):
            CoreException('This function accepts only one numeric feature',
                          None,logIt=True,shouldExit=True).act()
            
        categoricals = ru.param_itemize(param_s=categoricals,maxlength = len(categoricals),expectedtypes = str, defaultvalue = None)

        markobjects = ru.param_itemize(param_s=markobjects,maxlength = len(categoricals),expectedtypes = so.Mark, defaultvalue = so.Bar())
        statobjects = ru.param_itemize(param_s=statobjects,maxlength = len(categoricals),expectedtypes = so.Stat, defaultvalue = so.Agg())
        moveobjects = ru.param_itemize(param_s=moveobjects,maxlength = len(categoricals),expectedtypes = so.Move, defaultvalue = None)
        scaleobjects = ru.param_itemize(param_s=scaleobjects,maxlength = len(categoricals),expectedtypes = Scale, defaultvalue = None)
        limitobjects = ru.param_itemize(param_s=limitobjects,maxlength = len(categoricals),expectedtypes = Limit, defaultvalue = None)
        
        colors = ru.param_itemize(param_s=colors,maxlength = len(categoricals),expectedtypes = str, defaultvalue = None)
        linestyles = ru.param_itemize(param_s=linestyles,maxlength = len(categoricals),expectedtypes = str, defaultvalue = None)
        alphas = ru.param_itemize(param_s=alphas,maxlength = len(categoricals),expectedtypes = str, defaultvalue = None)
        
        
        facets = ru.param_itemize(param_s=facets,maxlength = len(categoricals),expectedtypes = Facet, defaultvalue = Facet())
    
        axessorsubfigs = None
        if(emptybackground):
            fig, axessorsubfigs = plt.subplots(nrows=griddimensions[0],ncols=griddimensions[1],figsize=figsize) if griddimensions else plt.subplots(figsize=figsize)    
        else:
            fig = plt.figure(figsize=figsize)
            axessorsubfigs = fig.subfigures(nrows=griddimensions[0],ncols=griddimensions[1]) if griddimensions else fig.subfigures()
        
        axess = axessorsubfigs.flatten() if hasattr(axessorsubfigs,'flatten') else axessorsubfigs if ru.is_array(axessorsubfigs) else [axessorsubfigs]
        
        
        for i, (cat,axes) in enumerate(zip(categoricals,axess)):
            p = so.Plot(
                data=data,
                x=cat,
                y=numeric,
                color=colors[i],
                linestyle=linestyles[i],
                alpha = alphas[i]
                ) 
            p = p.add(markobjects[i],statobjects[i],moveobjects[i],legend=masterlegend) if moveobjects[i] else p.add(markobjects[i],statobjects[i],legend=masterlegend)
            p = p.scale(**scaleobjects[i].__dict__) if scaleobjects[i] else p
            p = p.limit(**limitobjects[i].__dict__) if limitobjects[i] else p
            p = p.label(x = cat,row = facets[i].row if facets[i].row else None)
            p = p.facet(col=facets[i].col,row=facets[i].row,wrap=facets[i].wrap,order=facets[i].order)
            p = p.share(x=sharex,y=sharey)
            p= p.label(x=xlabel if xlabel else cat,y=ylabel if ylabel else numeric,color='',col=rowlabel if rowlabel else facets[i].col,row=collabel if collabel else facets[i].row,title=title)
            p= p.on(axes)
            p = p.plot()
            
        """
        for i, (cat,axes) in enumerate(zip(categoricals,axess)):
            (
                so.Plot(data=data,x=cat,y=numeric, color = color[i],linestyle=linestyle)
                .add(markobject[i],statobject[i],legend=masterlegend)
                .label(x = cat,row = facets[i].row if facets[i].row else None)
                #.facet(row=facets[i][0],col=facets[i][1],wrap=facets[i][2])
                .facet(col=facets[i].col,row=facets[i].row,wrap=facets[i].wrap,order=facets[i].order)
                .share(x=sharex,y=sharey)
                .label(x=xlabel if xlabel else cat,y=ylabel if ylabel else numeric,color='',col=rowlabel if rowlabel else facets[i].col,row=collabel if collabel else facets[i].row,title=title)
                .on(axes)
                .plot()
            )
        """
        if(addbarlabels):
            fig = add_barlabel(fig)
        return p,fig
        
    except Exception as e:
        (
            CoverException(
                    message='plot could not be created',
                    cause=e,
                    logIt=True,
                    shouldExit=True,
                    dontThrow=True)
                    .adddata('griddimensions', griddimensions)
                    .adddata('__WARN__','Check mark object suits with concept, check grid_dimensions, check feature names correct. targget var is required for non-histogram plots. Bar labels only can be added to Bar() object')
                    .act()         
        )   

"""
def so_boxplot(
        data,
        feature_name,
        size=(12,5),
        facets=(None,None,None)):
    """"""
    Boxplot creates a boxplot of a given feature in a dataframe.

    Parameters
    data : dataframe
    feature_name : str
    size : tuple, optional
    facets : tuple, optional    
    """"""
    data['origin']=np.zeros(data.shape[0])
    (
         so.Plot(data=data, y='origin',x=feature_name)
        .add(so.Dots(pointsize=1, alpha=.3),so.Jitter(0.3))
        .add(so.Range(color="k",linewidth=1), so.Perc([10,90]))
        .add(so.Range(color="red",linewidth=5), so.Perc([25, 75]))
        .add(so.Dash(color='orange'),so.Agg('median'))
        .add(so.Dash(color='green'),so.Agg('mean'))
        .scale(y=so.Nominal(),x=so.Continuous())
        .layout(size=size)
        .facet(row=facets[0],col=facets[1],wrap=facets[2])   
        .plot()
    )
"""

def so_boxplots(
        data,
        numerics,
        percentiles = [20.0,75.0],
        griddimensions=None,
        viewmodes= 'sparse',#classic-sparse-band
        verticals = False,
        dotcolors = None,
        boxcolors = 'red',
        boxwidths =15.0,
        linecolors = 'k',
        linewidths = 5.0,
        xlabel = None,
        ylabel=None,
        rowlabel = None,
        collabel=None,
        title=None,
        sharex = False,
        sharey = False,
        emptybackground=False,
        facets=Facet(),
        size = (12.0,5.0),
        figsize=(12.0,5.0),
        masterlegend = False,
        horizontal = True
):
    """
    Make a boxplot of numerical data.

    Parameters
    data : dataframe
    numerics : list of str as numerical variables
    percentiles : list of float, optional e.g. [25,75]
    griddimensions : tuple, optional    
    viewmodes : str, optional e.g. 'classic-sparse-band'
    verticals : bool, optional true for vertical boxplots, false for horizontal boxplots
    dotcolors : list of str, optional as color of observations
    boxcolors : str, optional  color of percentile box 
    boxwidths : float, optional as width of percentile box 
    linecolors : str, optional  as line color of outliler line
    linewidths : float, optional  as line width of outliler line
    xlabel : str, optional  
    ylabel : str, optional  
    rowlabel : str, optional  
    collabel : str, optional    
    title : str, optional   
    sharex : bool, optional 
    sharey : bool, optional 
    emptybackground : bool, optional    
    facets : Facet, optional    
    figsize : tuple, optional   
    masterlegend : bool, optional   
    """

    try:
        
        len_numerics = len(numerics) if ru.is_array(numerics) else 1

        numerics = ru.param_itemize(param_s=numerics,maxlength = len_numerics,expectedtypes = str, defaultvalue = None)
        percentiles = ru.param_itemize(param_s=percentiles,maxlength = len_numerics,expectedtypes = (list,np.ndarray), defaultvalue = [25,75])
        viewmodes = ru.param_itemize(param_s=viewmodes,maxlength = len_numerics,expectedtypes = str, defaultvalue = 'sparse')
        verticals = ru.param_itemize(param_s=verticals,maxlength = len_numerics,expectedtypes = bool, defaultvalue = False)
        dotcolors = ru.param_itemize(param_s=dotcolors,maxlength = len_numerics,expectedtypes = str, defaultvalue = None)    
        boxcolors = ru.param_itemize(param_s=boxcolors,maxlength = len_numerics,expectedtypes = str, defaultvalue = 'red')
        boxwidths = ru.param_itemize(param_s=boxwidths,maxlength = len_numerics,expectedtypes = (int,float), defaultvalue = 15)
        linecolors= ru.param_itemize(param_s=linecolors,maxlength = len_numerics,expectedtypes = str, defaultvalue ='k')
        linewidths = ru.param_itemize(param_s=linewidths,maxlength = len_numerics,expectedtypes = float, defaultvalue = 5)
        viewmodes = ru.param_itemize(param_s=viewmodes,maxlength = len_numerics,expectedtypes = str, defaultvalue = 'sparse')
        facets = ru.param_itemize(param_s=facets,maxlength = len_numerics,expectedtypes = Facet, defaultvalue = Facet())
        
        dotobjects = []
        moveobjects = []

        for numeric in numerics:
            for viewmode in viewmodes:
                match viewmode:
                    case 'classic':
                        dotobjects.append(so.Dot(alpha=0.1))
                        moveobjects.append(so.Dodge(1)) 
                    case 'sparse':
                        dotobjects.append(so.Dot(alpha=0.1))    
                        moveobjects.append(so.Jitter(1))        
                    case 'band':
                        dotobjects.append(so.Dash(alpha=0.01))  
                        moveobjects.append(so.Jitter(1))    
                    case _: 
                        CoreException('viewmode must be one of classic, sparse, band',
                                None,logIt=True,shouldExit=True).act()
        
        
        axessorsubfigs = None
        if(emptybackground):
            fig, axessorsubfigs = plt.subplots(nrows=griddimensions[0],ncols=griddimensions[1],figsize=figsize) if griddimensions else plt.subplots(figsize=figsize)    
        else:
            fig = plt.figure(figsize=figsize)
            axessorsubfigs = fig.subfigures(nrows=griddimensions[0],ncols=griddimensions[1]) if griddimensions else fig.subfigures()
        
        axess = axessorsubfigs.flatten() if hasattr(axessorsubfigs,'flatten') else axessorsubfigs if ru.is_array(axessorsubfigs) else [axessorsubfigs]
        
        dummy_feature = 'observations (upview)' 
        plot_data = data.copy()
        plot_data[dummy_feature]=np.full(plot_data.shape[0],'')
        
        for i, (numeric,axes) in enumerate(zip(numerics,axess)):
            p = so.Plot(
                data=plot_data,
                x=numeric,
                y=dummy_feature)\
                 if horizontal else\
                so.Plot(
                data=plot_data,
                x=dummy_feature,
                y= numeric)
            p = p.add(dotobjects[i],moveobjects[i],legend=masterlegend) 
            p = p.add(so.Range(color = boxcolors[i],linewidth=boxwidths[i]), so.Perc(percentiles[i]),legend=masterlegend) 
            p = p.add(so.Range(color = linecolors[i],linewidth=linewidths[i]),so.Perc(su.get_outlier_range(plot_data[numeric])), legend=masterlegend)
            p = p.add(so.Dash(color = linecolors[i],linewidth=linewidths[i]),so.Perc(su.get_outlier_range(plot_data[numeric])), orient = 'y', legend=masterlegend)
            p = p.facet(col=facets[i].col,row=facets[i].row,wrap=facets[i].wrap,order=facets[i].order)
            p = p.share(x=sharex,y=sharey)
            p= p.label(x=xlabel if xlabel else numeric,y=ylabel if ylabel else numeric,color='',col=rowlabel if rowlabel else facets[i].col,row=collabel if collabel else facets[i].row,title=title)
            p = p.layout(size = size)
            p= p.on(axes)
            p = p.plot()

        return p,fig   
    except Exception as e:
        (
            CoverException(
                    message='plot could not be created',
                    cause=e,
                    logIt=True,
                    shouldExit=True,
                    dontThrow=False)
                    .adddata('griddimensions', griddimensions)
                    .adddata('__WARN__','Check mark object suits with concept, check grid_dimensions, check feature names correct. targget var is required for non-histogram plots. Bar labels only can be added to Bar() object')
                    .act()         
        ) 
        


