import seaborn as sns
import seaborn.objects as so
import matplotlib.pyplot as plt
from matplotlib.colors import is_color_like
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

class Share(paramatizable):
    def __init__(self,**shares):
        super().__init__(**shares)

class Layer():
    def __init__(self,mark,*transforms, orient = None, legend=True, data=None,**variables):
        self.mark = mark
        self.transforms = transforms    
        self.orient = orient,
        self.legend = legend
        self.data = data
        self.variables = variables   

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
        griddimensions,
        numeric = None,
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
        settheme = None,
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
        griddimensions = griddimensions if all(griddimensions) else (1,1) 
        
        facets = ru.param_itemize(param_s=facets,maxlength = len(categoricals),expectedtypes = Facet, defaultvalue = Facet())
    
        if(emptybackground):
            sns.set_theme (style= 'white' , palette= 'muted' )
        else:
            sns.set_theme (**settheme if settheme else{} ) 
        """
        fig = plt.figure(figsize=figsize,layout = 'tight')
        fig, axessorsubfigs = plt.subplots(nrows=griddimensions[0],ncols=griddimensions[1],figsize=figsize) if griddimensions else plt.subplots(figsize=figsize)    
        axess = axessorsubfigs.flatten() if hasattr(axessorsubfigs,'flatten') else axessorsubfigs if ru.is_array(axessorsubfigs) else [axessorsubfigs]
        """        
        
        fig = plt.figure(figsize=figsize,layout='tight')   
        subfigs = fig.subfigures(griddimensions[0],griddimensions[1]) 
        subfigs = subfigs.flatten() if hasattr(subfigs,'flatten') else subfigs if ru.is_array(subfigs) else [subfigs]
        
        for i, (_cat,_subfig) in enumerate(zip(categoricals,subfigs)):
            p = so.Plot(
                data=data,
                x=_cat,
                y=numeric,
                color=colors[i],
                linestyle=linestyles[i],
                alpha = alphas[i]
                ) 
            
            p = p.add(markobjects[i],statobjects[i],moveobjects[i],legend=masterlegend) if moveobjects[i] else p.add(markobjects[i],statobjects[i],legend=masterlegend)
            p = p.scale(**scaleobjects[i].__dict__) if scaleobjects[i] else p.scale(x = so.Nominal(),y=so.Continuous())
            p = p.limit(**limitobjects[i].__dict__) if limitobjects[i] else p
            p = p.label(x = _cat,row = facets[i].row if facets[i].row else None)
            p = p.facet(col=facets[i].col,row=facets[i].row,wrap=facets[i].wrap,order=facets[i].order)
            p = p.share(x=sharex,y=sharey)
            p= p.label(x=xlabel if xlabel else _cat,y=ylabel if ylabel else numeric,color='',col=rowlabel if rowlabel else facets[i].col,row=collabel if collabel else facets[i].row,title=title)
            p= p.on(_subfig)
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


def so_boxplots(
        data,
        numerics,
        griddimensions,
        #axes=None,
        percentiles = [20.0,75.0],
        colors=None,
        markers=None,
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
        settheme = None,
        masterlegend = False,
        vertical = False,
        showmeans = 'cyan',
        showmedians = 'gold',
        showhistogram = False):
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
        
        master_length = len(numerics) if ru.is_array(numerics)  else 1

        numerics = ru.param_itemize(param_s=numerics,maxlength = master_length,expectedtypes = str, defaultvalue = None)
        #axes = ru.param_itemize(param_s=axes,maxlength = len_numerics,expectedtypes = plt.axes, defaultvalue = None)
        percentiles = ru.param_itemize(param_s=percentiles,maxlength = master_length,expectedtypes = (list,np.ndarray), defaultvalue = [25,75])
        viewmodes = ru.param_itemize(param_s=viewmodes,maxlength = master_length,expectedtypes = str, defaultvalue = 'sparse')
        verticals = ru.param_itemize(param_s=verticals,maxlength = master_length,expectedtypes = bool, defaultvalue = False)
        dotcolors = ru.param_itemize(param_s=dotcolors,maxlength = master_length,expectedtypes = str, defaultvalue = None)    
        boxcolors = ru.param_itemize(param_s=boxcolors,maxlength = master_length,expectedtypes = str, defaultvalue = 'red')
        boxwidths = ru.param_itemize(param_s=boxwidths,maxlength = master_length,expectedtypes = (int,float), defaultvalue = 15)
        linecolors= ru.param_itemize(param_s=linecolors,maxlength = master_length,expectedtypes = str, defaultvalue ='k')
        linewidths = ru.param_itemize(param_s=linewidths,maxlength = master_length,expectedtypes = float, defaultvalue = 5)
        viewmodes = ru.param_itemize(param_s=viewmodes,maxlength = master_length,expectedtypes = str, defaultvalue = 'sparse')
        facets = ru.param_itemize(param_s=facets,maxlength = master_length,expectedtypes = Facet, defaultvalue = Facet())
        colors = ru.param_itemize(param_s=colors,maxlength = len(numerics),expectedtypes = str, defaultvalue = None) 
        markers = ru.param_itemize(param_s=markers,maxlength = len(numerics),expectedtypes = str, defaultvalue = None)  
        griddimensions = griddimensions if all(griddimensions) else (1,1)

        dotobjects = []
        moveobjects = []

        for _numeric in numerics:
            for viewmode in viewmodes:
                match viewmode:
                    case 'classic':
                        dotobjects.append(so.Dots(alpha=0.1))
                        moveobjects.append(so.Dodge(1)) 
                    case 'sparse':
                        dotobjects.append(so.Dots(alpha=0.1))    
                        moveobjects.append(so.Jitter(1))        
                    case 'band':
                        dotobjects.append(so.Dash(alpha=0.01))  
                        moveobjects.append(so.Jitter(1))    
                    case _: 
                        CoreException('viewmode must be one of classic, sparse, band',
                                None,logIt=True,shouldExit=True).act()
        
        
        
        if(emptybackground):
            sns.set_theme (style= 'white' , palette= 'muted' )
        else:
            sns.set_theme(**settheme if settheme else {})
        
        #########
        fig = None,
        subfigs = []
        if(showhistogram):
            grid_row = griddimensions[0] 
            grid_col = griddimensions[1] 

            grid_row = 2 * grid_row
            fig = plt.figure(figsize=figsize,layout='tight')
            grid_subfigs= fig.subfigures(grid_row,grid_col)

            for k in range(0,grid_row,2):
                for j in range(0,grid_col):
                    subfigs.append([grid_subfigs[k],grid_subfigs[k+1]]) if len(grid_subfigs.shape)==1 else subfigs.append([grid_subfigs[k,j],grid_subfigs[k+1,j]])

        else:
            fig = plt.figure(figsize=figsize,layout='tight')   
            subfigs = fig.subfigures(griddimensions[0],griddimensions[1]) 
            subfigs =  subfigs.flatten() if hasattr(subfigs,'flatten') else subfigs if ru.is_array(subfigs) else [subfigs]

        #########       
        dummy_feature = 'observations (upview)' 
        plot_data = data.copy()
        plot_data[dummy_feature]=np.full(plot_data.shape[0],'')
        
        for i, (_numeric,_subfig) in enumerate(zip(numerics,subfigs)):
            
            p_box = so.Plot(
                data=plot_data,
                x=dummy_feature,
                y=_numeric)\
                 if vertical else\
                so.Plot(
                data=plot_data,
                x=_numeric,
                y= dummy_feature)
            p_box = p_box.add(dotobjects[i],moveobjects[i],legend=masterlegend,color = colors[i],marker = markers[i]) 
            p_box = p_box.add(so.Range(color = boxcolors[i],linewidth=boxwidths[i]), so.Perc(percentiles[i]),legend=masterlegend)
            p_box = p_box.add(so.Range(color = linecolors[i],linewidth=linewidths[i]),so.Perc(su.get_outlier_range(plot_data[_numeric])), legend=masterlegend)
            p_box = p_box.add(so.Dash(color = linecolors[i],linewidth=linewidths[i]),so.Perc(su.get_outlier_range(plot_data[_numeric])), orient = 'x' if vertical else 'y' , legend=masterlegend)
            #p = p.add(so.Line(color=showmeans if is_color_like(showmeans) else 'cyan'),x=np.full(data.shape[0],np.mean(data[numeric])), y =np.linspace(0,np.histogram(data[numeric],bins='auto')[0].max(),data[numeric].shape[0]),orient='x' if vertical else 'y') if showmeans else p
            #p = p.add(so.Line(color =showmedians if is_color_like(showmedians) else 'gold'),x=np.full(data.shape[0],np.median(data[numeric])), y =np.linspace(0,np.histogram(data[numeric],bins='auto')[0].max(),data[numeric].shape[0]),orient='x' if vertical else 'y') if showmedians else p

            p_box = p_box.add(so.Dash(color=showmeans if is_color_like(showmeans) else 'cyan'),so.Agg('mean'),orient='x' if vertical else 'y') if showmeans else p_box
            p_box = p_box.add(so.Dash(color=showmedians if is_color_like(showmedians) else 'gold'),so.Agg('median'),orient='x' if vertical else 'y') if showmedians else p_box
            p_box = p_box.facet(col=facets[i].col,row=facets[i].row,wrap=facets[i].wrap,order=facets[i].order)
            p_box = p_box.share(x=sharex,y=sharey)
            p_box= p_box.label(x=xlabel if xlabel else _numeric,y=ylabel if ylabel else _numeric,color='',col=rowlabel if rowlabel else facets[i].col,row=collabel if collabel else facets[i].row,title=title)
            p_box = p_box.layout(size = size)
            p_box= p_box.on(_subfig[0] if showhistogram else _subfig)
            p_box = p_box.plot()

            if(showhistogram):
                mean_line = np.full(plot_data.shape[0],np.mean(plot_data[_numeric]))
                bins_axis = np.linspace(0,np.histogram(plot_data[_numeric],bins='auto')[0].max(),plot_data[_numeric].shape[0]) 
                median_line = np.full(plot_data.shape[0],np.median(plot_data[_numeric]))

                p_hist = (so.Plot(data=plot_data,y=_numeric)) if vertical else (so.Plot(data=plot_data,x=_numeric)) 
                #p_hist = so.Plot(data=plot_data,x=_numeric)
                p_hist = p_hist.add(so.Bars(),so.Hist(),so.Stack(),color=colors[i])
                p_hist = ( p_hist.add(so.Line(color = showmeans if is_color_like(showmeans) else 'cyan'), x = mean_line , y = bins_axis) if showmeans else p_hist ) if not vertical else p_hist
               # ..( p_hist.add(so.Line(color = showmeans if is_color_like(showmeans) else 'cyan'),y = mean_line) if showmeans else p_hist )
                #p_hist
                p_hist = ( p_hist.add(so.Line(color = showmedians if is_color_like(showmedians) else 'gold'), x = median_line , y = bins_axis) if showmedians else p_hist ) if not vertical else p_hist 
                p_hist = p_hist.share(x=sharex,y=sharey)
                p_hist = p_hist.label(x=xlabel if xlabel else _numeric,y=ylabel if ylabel else 'count',color='',col=rowlabel if rowlabel else facets[i].col,row=collabel if collabel else facets[i].row,title=title)
                p_hist = p_hist.layout(size = size)
                p_hist = p_hist.facet(col=facets[i].col,row=facets[i].row,wrap=facets[i].wrap,order=facets[i].order)
                p_hist = p_hist.on(_subfig[1])
                p_hist = p_hist.plot()
                 
        return p_box,fig   
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
        


def so_boxplot1(
        data,
        feature,
        percentiles = [25.0,75.0],
        facet:Facet = Facet(),
        size = (4,6),
        showmean = {'color':'cyan'},
        showmedian = {'color':'gold'},
        histogram = False,
        theme = {},
        observationslayer = Layer(so.Band(alpha=0.1),so.Jitter(1)),
        share = {'x':False,'y':False},
        boxrangevars={'color':'red','linewidth':15},
        lineranvevars = {'color':'k','linewidth':5},

):
    try:
        dummy_feature = 'origin' 
        plot_data = data.copy()
        plot_data[dummy_feature]=np.full(plot_data.shape[0],'') 
        p_box = so.Plot(
            data = plot_data,
            x=feature,
            y=dummy_feature
        )
        p_box = p_box.add(
            observationslayer.mark,
            *observationslayer.transforms,
            orient=observationslayer.orient,
            legend=observationslayer.legend,
            data=observationslayer.data,
            **observationslayer.variables
        )
        p_box = p_box.add(
            so.Range(),so.Perc(percentiles)
        )
        p_box = p_box.add(
            so.Range(),so.Perc(su.get_outlier_range(plot_data[feature]))
        )
        p_box = p_box.add(
            so.Dash(),so.Perc(su.get_outlier_range(plot_data[feature]))
        )
        p_box = p_box.facet(facet)
        p_box = p_box.share()
        p_box = p_box.plot()


    except Exception as e:
        (
            CoverException(
                    message='plot could not be created',
                    cause=e,
                    logIt=True).act()
        )


################################
################################

class kwargsbase(object):
    def __init__(self,**kwargs):
        self.kwargs = kwargs
            

class argsbase(object):
    def __init__(self,*args):
        self.args = args

class argskwargssbase(argsbase,kwargsbase):
    def __init__(self,*args,**kwargs):
        argsbase.__init__(self,*args)
        kwargsbase.__init__(self,**kwargs)  

class PlotParam(kwargsbase):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)   

class TransformParam(argskwargssbase):
    def __init__(self,*args,**kwargs):
        argsbase.__init__(self,*args)
        kwargsbase.__init__(self,**kwargs)

class ScaleParam(kwargsbase):
    def __init__(self,**kwargs):    
        super().__init__(**kwargs)

class FacetParam(kwargsbase):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)   

class PairParam(kwargsbase):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)   

class LayoutParam(kwargsbase):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)  

class LabelParam(kwargsbase):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)  

class LimitParam(kwargsbase):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)  

class ShareParam(kwargsbase):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)  

class ThemeParam(argsbase):
    def __init__(self,*args):
        super().__init__(*args) 

class SoPlotter():
    __plotparam__ = None
    __plot__ = None
    __plotter__ = None
    __figure__ = None
    __axes__ = None

    def __init__(self,plotparam:PlotParam):
        self.__plot__ = so.Plot(**plotparam.kwargs)

    def design (self,
        #plotparam:PlotParam,
        transformparam:TransformParam =TransformParam(),
        scaleparam:ScaleParam = ScaleParam(),
        facetparam:FacetParam = FacetParam(),
        pairparam:PairParam = PairParam(),
        layoutparam:LayoutParam = LayoutParam(),
        labelparam:LabelParam = LabelParam(),
        limitparam:LimitParam = LimitParam(),
        shareparam:ShareParam = ShareParam(),
        themeparam:ThemeParam=ThemeParam(()),
        target = None):
        
        #self.__plot__ = so.Plot(*self.__plotparam__.kwargs)
        self.__plot__ = self.__plot__.add(*transformparam.args,**transformparam.kwargs)
        self.__plot__ = self.__plot__.scale(**scaleparam.kwargs)
        self.__plot__ = self.__plot__.facet(**facetparam.kwargs)  
        self.__plot__ = self.__plot__.pair(**pairparam.kwargs)
        self.__plot__ = self.__plot__.layout(**layoutparam.kwargs)
        self.__plot__ = self.__plot__.label(**labelparam.kwargs)
        self.__plot__ = self.__plot__.limit(**limitparam.kwargs)
        self.__plot__ = self.__plot__.share(**shareparam.kwargs)
        self.__plot__ = self.__plot__.theme(*themeparam.args)
        self.__plot__ = self.__plot__.on(target=target) if target else self.__plot__

        return self 
       
    def update(self,*args):
        for arg in args:
            if not check_type(arg,(argsbase,kwargsbase,argskwargssbase),typecheckmode=TypeCheckMode.SUBTYPE):
                CoreException(
                    message='Update arguments must be of base types, argsbase, kwargsbase, argskwargssbase',
                    cause=None,
                    logIt=True).act()
        if (check_type(arg,ScaleParam,typecheckmode=TypeCheckMode.SUBTYPE)):
            self.__plot__ = self.__plot__.scale(**arg.kwargs)
        if (check_type(arg,FacetParam,typecheckmode=TypeCheckMode.SUBTYPE)):
            self.__plot__ = self.__plot__.facet(**arg.kwargs)
        if (check_type(arg,PairParam,typecheckmode=TypeCheckMode.SUBTYPE)):
            self.__plot__ = self.__plot__.pair(**arg.kwargs)
        if (check_type(arg,LayoutParam,typecheckmode=TypeCheckMode.SUBTYPE)):
            self.__plot__ = self.__plot__.layout(**arg.kwargs)
        if (check_type(arg,LabelParam,typecheckmode=TypeCheckMode.SUBTYPE)):
            self.__plot__ = self.__plot__.label(**arg.kwargs)
        if (check_type(arg,LimitParam,typecheckmode=TypeCheckMode.SUBTYPE)):
            self.__plot__ = self.__plot__.limit(**arg.kwargs)
        if (check_type(arg,ShareParam,typecheckmode=TypeCheckMode.SUBTYPE)):
            self.__plot__ = self.__plot__.share(**arg.kwargs)
        if (check_type(arg,ThemeParam,typecheckmode=TypeCheckMode.SUBTYPE)):
            self.__plot__ = self.__plot__.theme(*arg.args)
        
        return self

    def addLayer(self,transformparam:TransformParam):
        self.__plot__ = self.__plot__.add(*transformparam.args,**transformparam.kwargs)
        return self

    def plot(self,pyplot=False):
        self.__plotter__ = self.__plot__.plot(pyplot=pyplot)
        return self
    
    def get_plotter(self,pyplot = False):
         if(self.__plotter__ ):   
            return self.__plotter__
         
         self.__plotter__ = self.__plot__.plot(pyplot=pyplot)
         return self.__plotter__
       
    def get_figure(self,pyplot = False):
        if(self.__figure__ ):   
            return self.__figure__
        self.__plotter__ = self.get_plotter(pyplot=pyplot)
        self.__figure__ = self.__plotter__._figure
        return self.__figure__

    def get_axes(self,pyplot = False):
        if(self.__axes__ ):   
            return self.__axes__
        self.__figure__ = self.get_figure(pyplot=pyplot)
        self.__axes__ = self.__figure__.axes
        return self.__axes__
    
########################################################################

def plot_stg(
    plotparam:PlotParam,
    transformparam:TransformParam =(),
    scaleparam:ScaleParam = ScaleParam(),
    facetparam:FacetParam = FacetParam(),
    pairparam:PairParam = PairParam(),
    layoutparam:LayoutParam = LayoutParam(),
    labelparam:LabelParam = LabelParam(),
    limitparam:LimitParam = LimitParam(),
    shareparam:ShareParam = ShareParam(),
    themeparam:ThemeParam=ThemeParam(())
    ,pyplot = False,target = None,plot=True):
 

  p= so.Plot(**plotparam.kwargs)
  p = p.add(*transformparam.args,**transformparam.kwargs)
  p = p.scale(**scaleparam.kwargs)
  p = p.facet(**facetparam.kwargs)  
  p = p.pair(**pairparam.kwargs)
  p = p.layout(**layoutparam.kwargs)
  p = p.label(**labelparam.kwargs)
  p = p.limit(**limitparam.kwargs)
  p = p.share(**shareparam.kwargs)
  p = p.theme(*themeparam.args)
  p = p.on(target=target) if target else p
  p = p.plot(pyplot=pyplot) if plot else p
  return p