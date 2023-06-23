import seaborn.objects as so
import matplotlib.pyplot as plt
import numpy as np

from exchelp.exception_helper import *
import aistudio.runtime.runtime_utils as ru
import aistudio.statistics.stats_utils as su
from aistudio.abstraction.base_types import *
from inspect import currentframe, getframeinfo

######################
## Plot Types
######################

# plot
# argskwargsbase
class PlotParam(argskwargssbase):
    def __init__(self,*args, **kwargs):
        argsbase.__init__(self,*args)
        kwargsbase.__init__(self,**kwargs)
            
# design,
# layer params
# argskwargsbase
class TransformParam(argskwargssbase):
    def __init__(self,*args,**kwargs):
        argsbase.__init__(self,*args)
        kwargsbase.__init__(self,**kwargs)

##update params
## kwargsbase
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
# argsbase
class ThemeParam(argsbase):
    def __init__(self,*args):
        super().__init__(*args) 

#Plotter class
class SoPlot():

    def __init__(self,plotparam:PlotParam):
        self.__plotparam__ = plotparam

    def design (self,
        transformparam:TransformParam =TransformParam(),
        scaleparam:ScaleParam = ScaleParam(),
        facetparam:FacetParam = FacetParam(),
        pairparam:PairParam = PairParam(),
        layoutparam:LayoutParam = LayoutParam(),
        labelparam:LabelParam = LabelParam(),
        limitparam:LimitParam = LimitParam(),
        shareparam:ShareParam = ShareParam(),
        themeparam:ThemeParam=ThemeParam(())):
        
        self.__plot__ = so.Plot(**self.__plotparam__.kwargs)
        self.__plot__ = self.__plot__.add(*transformparam.args,**transformparam.kwargs)
        self.__plot__ = self.__plot__.scale(**scaleparam.kwargs)
        self.__plot__ = self.__plot__.facet(**facetparam.kwargs)  
        self.__plot__ = self.__plot__.pair(**pairparam.kwargs)
        self.__plot__ = self.__plot__.layout(**layoutparam.kwargs)
        self.__plot__ = self.__plot__.label(**labelparam.kwargs)
        self.__plot__ = self.__plot__.limit(**limitparam.kwargs)
        self.__plot__ = self.__plot__.share(**shareparam.kwargs)
        self.__plot__ = self.__plot__.theme(*themeparam.args)

        return self 
       
    def update(self,*args:kwargsbase|argsbase|kwargsbase):

        for arg in args:
            if not check_type(arg,(argsbase,kwargsbase,argskwargssbase),typecheckmode=TypeCheckMode.SUBTYPE):
                CoreException(
                    message='Update arguments must be of base types, argsbase, kwargsbase, argskwargssbase',
                    cause=None,
                    logIt=True).act()
            if (check_type(arg,ScaleParam,typecheckmode=TypeCheckMode.SUBTYPE)):
                self.__plot__ = self.__plot__.scale(**arg.kwargs)
            elif (check_type(arg,FacetParam,typecheckmode=TypeCheckMode.SUBTYPE)):
                self.__plot__ = self.__plot__.facet(**arg.kwargs)
            elif (check_type(arg,PairParam,typecheckmode=TypeCheckMode.SUBTYPE)):
                self.__plot__ = self.__plot__.pair(**arg.kwargs)
            elif (check_type(arg,LayoutParam,typecheckmode=TypeCheckMode.SUBTYPE)):
                self.__plot__ = self.__plot__.layout(**arg.kwargs)
            elif (check_type(arg,LabelParam,typecheckmode=TypeCheckMode.SUBTYPE)):
                self.__plot__ = self.__plot__.label(**arg.kwargs)
            elif (check_type(arg,LimitParam,typecheckmode=TypeCheckMode.SUBTYPE)):
                self.__plot__ = self.__plot__.limit(**arg.kwargs)
            elif (check_type(arg,ShareParam,typecheckmode=TypeCheckMode.SUBTYPE)):
                self.__plot__ = self.__plot__.share(**arg.kwargs)
            elif (check_type(arg,ThemeParam,typecheckmode=TypeCheckMode.SUBTYPE)):
                self.__plot__ = self.__plot__.theme(*arg.args)
            else:
                 (
                 CoreException(message='Given update parameter is not one of the expected ones',logIt= True,)
                 .adddata('expected_types','ScaleParam,FacetParam,PairParam,LayoutParam,LabelParam,LimitParam,ShareParam,ThemeParam')
                 .adddata('file',getframeinfo(currentframe()).filename)
                 .adddata('lineno',getframeinfo(currentframe()).lineno)
                 .act()
                 )
               
        return self

    def addLayer(self,transformparam:TransformParam):
        self.__plot__ = self.__plot__.add(*transformparam.args,**transformparam.kwargs)
        return self

    def plot(self,pyplot=False,target = None):
        self.__plot__ = self.__plot__.on(target) if target else self.__plot__
        self.__plotter__ = self.__plot__.plot(pyplot=pyplot)
        return self
    
    def get_plotter(self,pyplot = False):
         if(self.__plotter__ ):   
            return self.__plotter__
         
         self.__plotter__ = self.__plot__.plot(pyplot=pyplot)
         return self.__plotter__

####################
## Globals
####################

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

################################
## Functs
################################

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
            CoverException('Barlabel could not be added to the barplot',cause=e,logIt=True)
            .adddata('plotobject', figure)
            .adddata('__WARN__','Check number of (sub)figures and the number of axes. Make sure that the used Mark object is Bar() instead of Bars()')
            .act()
        )

def boxplot(plotparam:PlotParam,
            percentiles = [25.0,75.0],
            dotvars : kwargsbase = kwargsbase(pointsize=0.5),
            jittervars : kwargsbase = kwargsbase(width=0.5),
            dashvars:kwargsbase = kwargsbase(alpha=0.1),
            dodgevars:kwargsbase = kwargsbase(),
            percboxvars : kwargsbase = kwargsbase(color='k',linewidth=15),
            outlierrangevars : kwargsbase = kwargsbase(color='r',linewidth=5),
            meanvars:kwargsbase = kwargsbase(color='red',linestyle='--'),
            medianvars:kwargsbase = kwargsbase(color='k',linestyle = ':'),
            segmentvars:kwargsbase = kwargsbase(),
            dotview = False
            ):
    #validate
    if(len(plotparam.kwargs)!= 2 or 'data' not in plotparam.kwargs):
        (
            CoreException(message='Along with data parameter, only one of x or y variable required with any value, to determine the orientation.',logIt= True,)
            .adddata('file',getframeinfo(currentframe()).filename)
            .adddata('lineno',getframeinfo(currentframe()).lineno)
            .act()
        )
    #data
    temp_plotparam = kwargsbase(**plotparam.kwargs)
    #data = temp_plotparam.kwargs['data']    
    data = temp_plotparam.rmv('data')
    axis,feature = temp_plotparam.kwargs.popitem()
    otheraxis = 'y' if axis == 'x' else 'x'
    temp_plotparam.kwargs[axis] = feature
    temp_plotparam.kwargs[otheraxis] = np.full(data.shape[0],'obs')
    temp_plotparam.kwargs['data'] = data
    #plot
    designtransform = (
        TransformParam(so.Dot(**dotvars.kwargs),so.Jitter(**jittervars.kwargs),**segmentvars.kwargs) 
            if  dotview else
        TransformParam(so.Dash(**dashvars.kwargs),so.Dodge(**dodgevars.kwargs),**segmentvars.kwargs) 
    )
    sp =  SoPlot(
              plotparam=temp_plotparam
        ).design(
            designtransform
        ).addLayer(## percentile box
            TransformParam(
            so.Range(**percboxvars.kwargs),so.Perc(percentiles)
            )
        ).addLayer( ## outlier range
            TransformParam(
            so.Range(**outlierrangevars.kwargs), so.Perc(su.get_outlier_percentileofscore(data[feature],percentiles))
            )
        ).addLayer(## outlier range ends
            TransformParam(
            so.Dash(**outlierrangevars.kwargs),so.Perc(su.get_outlier_percentileofscore(data[feature],percentiles))
            )
        ).addLayer(## meanline
            TransformParam(
                so.Dash(**meanvars.kwargs),so.Agg('mean')
            )
        ).addLayer(## medianline
            TransformParam(
                so.Dash(**medianvars.kwargs),so.Agg('median')
            ) 
        )
    return sp

def multi_boxplot(
            plotparam:PlotParam,
            features:argsbase,
            updateparams:argsbase = argsbase(),
            globalupdates:argsbase = argsbase(),
            histvars:argsbase = argsbase(TransformParam(so.Bars(),so.Hist())),
            kdevars:argsbase=argsbase(TransformParam(so.Line(),so.KDE())),
            meanvars:argsbase = argsbase(kwargsbase(color='red',linestyle='--')),
            medianvars:argsbase = argsbase(kwargsbase(color='k',linestyle = ':')),
            figsize = (6.4,4.8),
            layout = 'tight',
            wrap = 3,
            showhistogram=False,
            showstatslines = True,
            showkde = False,

            boxplotvars:argsbase = argsbase(kwargsbase())
            ):
    """
    boxplotvars = argsbase(kwargsbase()),
    percentiles:argsbase = argsbase([25,75]),
    dotvars:argsbase = argsbase(kwargsbase(pointsize=0.5)),
    jittervars:argsbase = argsbase(kwargsbase(width=0.5)),
    dashvars:argsbase = argsbase(kwargsbase()),
    dodgevars:argsbase = argsbase(kwargsbase()),
    percboxvars:argsbase = argsbase(kwargsbase(color='k',linewidth=15)),
    outlierrangevars:argsbase = argsbase(kwargsbase(color='r',linewidth=5)),
   
    segmentvars:argsbase = argsbase(kwargsbase()),
    dotview = argsbase(False),
    """
    #validate
    if(len(plotparam.kwargs)!= 2 or 'data' not in plotparam.kwargs):
        (
        CoreException(message='Along with data parameter, only one of x or y variable required with any value, to determine the orientation.',logIt= True,)
        .adddata('file',getframeinfo(currentframe()).filename)
        .adddata('lineno',getframeinfo(currentframe()).lineno)
        .act()
        )
    #param
    max_length = len(features.args)
    features = ru.parametize_argsbase(features,None,max_length)
    updateparams = ru.parametize_argsbase(updateparams,argsbase(),max_length)
    histvars = ru.parametize_argsbase(histvars,TransformParam(so.Bars(),so.Hist()),max_length)
    kdevars = ru.parametize_argsbase(kdevars,TransformParam(so.Line(),so.KDE()),max_length)
    meanvars = ru.parametize_argsbase(meanvars,kwargsbase(color='red',linestyle='--'),max_length)
    medianvars = ru.parametize_argsbase(medianvars,kwargsbase(color='k',linestyle = ':'),max_length)
    boxplotvars = ru.parametize_argsbase(boxplotvars,kwargsbase(),max_length)
    #data
    temp_plotparam = kwargsbase(**plotparam.kwargs)    
   # data = temp_plotparam.kwargs['data']
    data = temp_plotparam.rmv('data')
    axis,feature = temp_plotparam.kwargs.popitem()
    #grid
    nrows = 1
    ncols = ncols=wrap if max_length > wrap else max_length
    for i in range(0,max_length):
        if(i>= wrap and i % wrap == 0):
            nrows+=1 
    fig,subfigs = plt.figure(figsize=figsize,layout=layout),[]
    if(showhistogram):
        nrows *= 2
        grid_subfigs = fig.subfigures(nrows,ncols)
        for k in range(0,nrows,2):
                for j in range(0,ncols):
                    subfigs.append([grid_subfigs[k],grid_subfigs[k+1]]) if len(grid_subfigs.shape)==1 else subfigs.append([grid_subfigs[k,j],grid_subfigs[k+1,j]])
    else:
        subfigs = fig.subfigures(nrows,ncols)    
        subfigs =  subfigs.flatten() if hasattr(subfigs,'flatten') else subfigs if ru.is_array(subfigs) else [subfigs]
    #plot
    for _i, (_feature, _subfig) in enumerate(zip(features.args,subfigs)):
        plotparam.kwargs[axis] = _feature
        #Histogram
        if(showhistogram):
            hst = SoPlot(plotparam=plotparam)
            hst = hst.design(histvars.args[_i])
            if showkde:
                hst = hst.addLayer(kdevars.args[_i])
            hst = hst.update(*globalupdates.args)
            hst = hst.update(*updateparams.args[_i].args)
            hst = hst.plot(target=_subfig[1])
            #lines
            if showstatslines:
                for ax in _subfig[1].axes:
                    ax.axvline(np.mean(data[_feature]),**meanvars.args[_i].kwargs) if axis == 'x' else\
                    ax.axhline(np.mean(data[_feature]),**meanvars.args[_i].kwargs)
                    ax.axvline(np.median(data[_feature]),**medianvars.args[_i].kwargs) if axis == 'x' else\
                    ax.axhline(np.median(data[_feature]),**medianvars.args[_i].kwargs)
        #boxplot
        # override mean median vars
        boxplotvars.args[_i].kwargs['meanvars'] = meanvars.args[_i]
        boxplotvars.args[_i].kwargs['medianvars'] = medianvars.args[_i]
        box = boxplot(
            plotparam=plotparam,
            **boxplotvars.args[_i].kwargs
        )     
        box = box.update(*globalupdates.args)
        box = box.update(*updateparams.args[_i].args)
        box = box.plot(target = _subfig[0] if showhistogram else _subfig)
    
    return fig

def multi_histogram(plotparam:PlotParam,
            features : argsbase,
            histvars:argsbase = argsbase(TransformParam(so.Bars(),so.Hist())),
            kdevars:argsbase=argsbase(TransformParam(so.Line(),so.KDE())),
            percentiles:argsbase = argsbase([25.0,75.0]),
            percboxvars : argsbase = argsbase(kwargsbase(color='cyan',linewidth=2)),
            outlierrangevars : argsbase = argsbase(kwargsbase(color='magenta',linewidth=2,linestyle = '-.')),
            meanvars:argsbase = argsbase(kwargsbase(color='red',linestyle='--')),
            medianvars:argsbase = argsbase(kwargsbase(color='k',linestyle =':')),
            updateparams:argsbase = argsbase(),
            globalupdates:argsbase = argsbase(),
            showkde = argsbase(False),
            showpercbox = argsbase(False),
            showoutlierrange = argsbase(False), 
            figsize = (6.4,4.8),
            layout = 'tight',
            wrap = 3,
            ):
    
    #validate
    if(len(plotparam.kwargs)!= 2 or 'data' not in plotparam.kwargs):
        (
            CoreException(message='Along with data parameter, only one of x or y variable required with any value, to determine the orientation.',logIt= True,)
            .adddata('file',getframeinfo(currentframe()).filename)
            .adddata('lineno',getframeinfo(currentframe()).lineno)
            .act()
        )
    #param
    max_length = len(features.args)
    features = ru.parametize_argsbase(features,None,max_length)
    histvars = ru.parametize_argsbase(histvars,TransformParam(so.Bars(),so.Hist()),max_length)
    kdevars = ru.parametize_argsbase(kdevars,TransformParam(so.Line(),so.KDE()),max_length)
    percentiles = ru.parametize_argsbase(percentiles,[25.0,75.0],max_length)
    percboxvars = ru.parametize_argsbase(percboxvars,kwargsbase(color='cyan',linewidth=2),max_length)
    outlierrangevars = ru.parametize_argsbase(outlierrangevars,kwargsbase(color='magenta',linewidth=2,linestyle = '-.'),max_length)
    meanvars = ru.parametize_argsbase(meanvars,kwargsbase(color='red',linestyle='--'),max_length)
    medianvars = ru.parametize_argsbase(medianvars,kwargsbase(color='k',linestyle = ':'),max_length)
    updateparams = ru.parametize_argsbase(updateparams,argsbase(),max_length)
    showkde = ru.parametize_argsbase(showkde,False,max_length)
    showpercbox = ru.parametize_argsbase(showpercbox,False,max_length)
    showoutlierrange = ru.parametize_argsbase(showoutlierrange,False,max_length)
    #data
    temp_plotparam = kwargsbase(**plotparam.kwargs)
    #data = temp_plotparam.kwargs['data']    
    data = temp_plotparam.rmv('data')
    axis,feature = temp_plotparam.kwargs.popitem()
    otheraxis = 'y' if axis == 'x' else 'x'
    temp_plotparam.kwargs[axis] = feature
    temp_plotparam.kwargs[otheraxis] = np.full(data.shape[0],'obs')
    temp_plotparam.kwargs['data'] = data
    #grid
    nrows = 1
    ncols = ncols=wrap if max_length > wrap else max_length
    for i in range(0,max_length):
        if(i>= wrap and i % wrap == 0):
            nrows+=1 
    fig = plt.figure(figsize=figsize,layout = layout)
    subfigs = fig.subfigures(nrows,ncols)    
    subfigs =  subfigs.flatten() if hasattr(subfigs,'flatten') else subfigs if ru.is_array(subfigs) else [subfigs] 
    #plot
    for _i, (_feature, _subfig) in enumerate(zip(features.args,subfigs)):
        plotparam.kwargs[axis] = _feature
        hst = SoPlot(plotparam=plotparam)
        hst = hst.design(histvars.args[_i])
        if showkde.args[_i]:
            hst = hst.addLayer(kdevars.args[_i])
        hst = hst.update(*globalupdates.args)
        hst = hst.update(*updateparams.args[_i].args)
        hst = hst.plot(target=_subfig)
       #lines
        for ax in _subfig.axes:
            ax.axvline(np.mean(data[_feature]),**meanvars.args[_i].kwargs) if axis == 'x' else\
            ax.axhline(np.mean(data[_feature]),**meanvars.args[_i].kwargs)
            ax.axvline(np.median(data[_feature]),**medianvars.args[_i].kwargs) if axis == 'x' else\
            ax.axhline(np.median(data[_feature]),**medianvars.args[_i].kwargs)
            if showpercbox.args[_i]:
                percs = percentiles.args[_i]
                percs = np.percentile(data[_feature],percs)
                ax.axvline(percs[0],**percboxvars.args[_i].kwargs) if axis == 'x' else\
                ax.axhline(percs[0],**percboxvars.args[_i].kwargs)
                ax.axvline(percs[1],**percboxvars.args[_i].kwargs) if axis == 'x' else\
                ax.axhline(percs[1],**percboxvars.args[_i].kwargs)
            if showoutlierrange.args[_i]:
                percs = percentiles.args[_i]
                lower,upper = su.get_outlier_bounds(data[_feature],percs)
                ax.axvline(lower,**outlierrangevars.args[_i].kwargs) if axis == 'x' else\
                ax.axhline(lower,**outlierrangevars.args[_i].kwargs)
                ax.axvline(upper,**outlierrangevars.args[_i].kwargs) if axis == 'x' else\
                ax.axhline(upper,**outlierrangevars.args[_i].kwargs)


    
    return fig

def multi_plot(
        plotparam:PlotParam,
        features:argsbase,
        designparams:argsbase,
        layerparams:argsbase = None,
        updateparams:argsbase = argsbase(),
        globalupdates:argsbase = argsbase(),
        figsize = None,
        layout = 'tight',
        wrap = 3,
        ):
    
    #param
    max_length = len(features.args)
    features = ru.parametize_argsbase(features,None,max_length)
    layerparams = ru.parametize_argsbase(layerparams,argsbase(),max_length)
    designparams = ru.parametize_argsbase(designparams,None,max_length)
    updateparams = ru.parametize_argsbase(updateparams,argsbase(),max_length)
    #data
    temp_plotparam = kwargsbase(**plotparam.kwargs)    
    temp_plotparam.rmv('data')
    axis,feature = temp_plotparam.kwargs.popitem()
    otheraxis = 'y' if axis == 'x' else 'x'
    #grid
    nrows = 1
    ncols = ncols=wrap if max_length > wrap else max_length
    for i in range(0,max_length):
        if(i>= wrap and i % wrap == 0):
            nrows+=1 
    fig = plt.figure(figsize=figsize,layout=layout)
    subfigs = fig.subfigures(nrows,ncols)    
    subfigs =  subfigs.flatten() if hasattr(subfigs,'flatten') else subfigs if ru.is_array(subfigs) else [subfigs]
    #plot
    soplt = SoPlot(plotparam=plotparam)
    for _i, (_feature, _subfig) in enumerate(zip(features.args,subfigs)):
        plotparam.kwargs[otheraxis] = _feature   
        soplt = soplt.design(designparams.args[_i])
        for layer in layerparams.args[_i].args:
            soplt = soplt.addLayer(layer) 
        soplt = soplt.update(*globalupdates.args)
        soplt = soplt.update(*updateparams.args[_i].args)
        soplt = soplt.plot(target = _subfig)
        
    return fig
