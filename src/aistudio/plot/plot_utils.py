import seaborn.objects as so
import matplotlib.pyplot as plt
import numpy as np

from aistudio.exception.exception_utils import Interrupter,InterruptPatcher
from aistudio.exception.exception_utils import is_subtypeof,is_typeof,parametize_tuplargs,is_array
from aistudio.statistics.stats_utils import get_outlier_percentileofscores,get_outlier_boundpairs,agg_upper_outlierbound,agg_lower_outlierbound,get_outlier_bounds
from aistudio.abstraction.base_types import *
from inspect import currentframe, getframeinfo

######################
## Plot Types
######################

# plot
# argskwargsbase
class PlotParam(dictuplargs):
    def __init__(self,*args, **kwargs):
        dictuplargs.__init__(self,*args,**kwargs)
        #tupleargs.__init__(self,*args)
        #kwargs.__init__(self,**kwargs)
            
# design,
# layer params
# argskwargsbase
class TransformParam(dictuplargs):
    def __init__(self,*args,**kwargs):
        dictuplargs.__init__(self,*args,**kwargs)
        #tupleargs.__init__(self,*args)
        #kwargs.__init__(self,**kwargs)

##update params
## kwargsbase
class ScaleParam(dictargs):
    def __init__(self,**kwargs):    
        super().__init__(**kwargs)

class FacetParam(dictargs):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)   

class PairParam(dictargs):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)   

class LayoutParam(dictargs):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)  

class LabelParam(dictargs):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)  

class LimitParam(dictargs):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)  

class ShareParam(dictargs):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)  
# argsbase
class ThemeParam(tuplargs):
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
       
    def update(self,*args:dictargs|tuplargs|dictargs):

        for arg in args:
            if not is_subtypeof(arg,tuplargs,dictargs,dictuplargs):
                Interrupter(
                    'Update arguments must be of base types, argsbase, kwargsbase, argskwargssbase',log=True,throw = True).act()
            if  is_typeof(arg,ScaleParam):
                self.__plot__ = self.__plot__.scale(**arg.kwargs)
            elif is_typeof(arg,FacetParam):
                self.__plot__ = self.__plot__.facet(**arg.kwargs)
            elif is_typeof(arg,PairParam):
                self.__plot__ = self.__plot__.pair(**arg.kwargs)
            elif is_typeof(arg,LayoutParam):
                self.__plot__ = self.__plot__.layout(**arg.kwargs)
            elif is_typeof(arg,LabelParam):
                self.__plot__ = self.__plot__.label(**arg.kwargs)
            elif is_typeof(arg,LimitParam):
                self.__plot__ = self.__plot__.limit(**arg.kwargs)
            elif is_typeof(arg,ShareParam):
                self.__plot__ = self.__plot__.share(**arg.kwargs)
            elif is_typeof(arg,ThemeParam):
                self.__plot__ = self.__plot__.theme(*arg.args)
            else:
                 (
                 Interrupter('Given update parameter is not one of the expected ones',log= True,throw = True)
                 .addkvps(expected_types = 'ScaleParam,FacetParam,PairParam,LayoutParam,LabelParam,LimitParam,ShareParam,ThemeParam')
                 .addkvps(file = getframeinfo(currentframe()).filename)
                 .addkvps(lineno = getframeinfo(currentframe()).lineno)
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

class GLOBALS:
    @classmethod
    def MONTH_NAMES(cls):
        """
        returns a dict of sorted month names
        """
        return {1:'January', 2:'February', 3:'March', 4:'April', 5:'May', 6:'June', 7:'July', 8:'August', 9:'September', 10:'October', 11:'November', 12:'December'}
    @classmethod
    def WEEK_DAYS(cls):
        """
        returns a dict of weekdays
        """
        return {1:'Monday', 2:'Tuesday', 3:'Wednesday', 4:'Thursday', 5:'Friday', 6:'Saturday', 7:'Sunday'}
    @classmethod
    def encoder_function(cls,keyOrValue,encoder_dict):
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
            InterruptPatcher('Barlabel could not be added to the barplot',log=True,throw = True)
            .adddata(HINT = 'Check number of (sub)figures and the number of axes. Make sure that the used Mark object is Bar() instead of Bars()')
            .act(e)
        )

def boxplot(plotparam:PlotParam,
            percentiles = [25.0,75.0],
            dotvars : dictargs = dictargs(pointsize=0.5),
            jittervars : dictargs = dictargs(width=0.5),
            dashvars:dictargs = dictargs(alpha=0.1),
            dodgevars:dictargs = dictargs(),
            percboxvars : dictargs = dictargs(color='k',linewidth=15),
            outlierrangevars : dictargs = dictargs(color='r',linewidth=5),
            meanvars:dictargs = dictargs(color='red',linestyle='--'),
            medianvars:dictargs = dictargs(color='k',linestyle = ':'),
            segmentvars:dictargs = dictargs(),
            dotview = True,
            **kwargs
            ):
    #validate
   
    #data
    temp_plotparam = dictargs(**plotparam.kwargs)
    data = temp_plotparam.popvals('data')
    xval,yval = temp_plotparam.popvals('x','y')
    if xval and yval:
        (
            Interrupter(message='Along with data parameter, only one of x or y variable required with any value, to determine the orientation.',log= True,throw=True)
            .addkvps(file = getframeinfo(currentframe()).filename)
            .addkvps(lineno = getframeinfo(currentframe()).lineno)
            .act()
        )
    axis = 'x' if xval else 'y'
    feature = xval if xval else yval
    #axis,feature = None,None
    #axis,feature = temp_plotparam.kwargs.popitem()
    #todo allow other variables in plotparam
    otheraxis = 'y' if axis == 'x' else 'x'
    temp_plotparam.kwargs[axis] = feature
    temp_plotparam.kwargs[otheraxis] = np.full(data.shape[0],' ')
    temp_plotparam.kwargs['data'] = data
    #plot
    designtransform = (
        TransformParam(so.Dot(**dotvars.kwargs),so.Jitter(**jittervars.kwargs),**segmentvars.kwargs) 
            if  dotview else
        TransformParam(so.Dash(**dashvars.kwargs),so.Dodge(**dodgevars.kwargs),**segmentvars.kwargs) 
    )
      # .addLayer(TransformParam(so.Range(**outlierrangevars.kwargs), so.Est(func=get_outlier_bounds,errorbar=('ci',90))))
    sp = SoPlot(plotparam=temp_plotparam).design(designtransform)\
        .addLayer(TransformParam(so.Range(**percboxvars.kwargs),so.Perc(percentiles)))\
        .addLayer(TransformParam(so.Dash(**outlierrangevars.kwargs),so.Agg(agg_upper_outlierbound)))\
        .addLayer(TransformParam(so.Dash(**outlierrangevars.kwargs),so.Agg(agg_lower_outlierbound)))\
        .addLayer(TransformParam(so.Dash(**meanvars.kwargs),so.Agg('mean')))\
        .addLayer(TransformParam(so.Dash(**medianvars.kwargs),so.Agg('median')))
        
    return sp

def multi_boxplot(
            plotparam:PlotParam,
            features:tuplargs,
            updateparams:tuplargs = tuplargs(),
            globalupdates:tuplargs = tuplargs(),
            histvars:tuplargs = tuplargs(TransformParam(so.Bars(),so.Hist())),
            kdevars:tuplargs=tuplargs(TransformParam(so.Line(),so.KDE())),
            meanvars:tuplargs = tuplargs(dictargs(color='red',linestyle='--')),
            medianvars:tuplargs = tuplargs(dictargs(color='k',linestyle = ':')),
            figsize = (6.4,4.8),
            layout = 'tight',
            wrap = 3,
            showhistogram=False,
            showstatslines = True,
            showkde = False,

            boxplotvars:tuplargs = tuplargs(dictargs())
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

    #param
    max_length = len(features.args)
    features = parametize_tuplargs(features,None,max_length)
    updateparams = parametize_tuplargs(updateparams,tuplargs(),max_length)
    histvars = parametize_tuplargs(histvars,TransformParam(so.Bars(),so.Hist()),max_length)
    kdevars = parametize_tuplargs(kdevars,TransformParam(so.Line(),so.KDE()),max_length)
    meanvars = parametize_tuplargs(meanvars,dictargs(color='red',linestyle='--'),max_length)
    medianvars = parametize_tuplargs(medianvars,dictargs(color='k',linestyle = ':'),max_length)
    boxplotvars = parametize_tuplargs(boxplotvars,dictargs(),max_length)
    #data
    temp_plotparam = dictargs(**plotparam.kwargs)
    data = temp_plotparam.popvals('data')
    xval,yval = temp_plotparam.popvals('x','y')
    if xval and yval:
        (
            Interrupter(message='Along with data parameter, only one of x or y variable required with any value, to determine the orientation.',log= True,throw=True)
            .addkvps(file = getframeinfo(currentframe()).filename)
            .addkvps(lineno = getframeinfo(currentframe()).lineno)
            .act()
        )
    axis = 'x' if xval else 'y'
    feature = xval if xval else yval
    #otheraxis = 'y' if axis == 'x' else 'x'

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
        subfigs =  subfigs.flatten() if hasattr(subfigs,'flatten') else subfigs if is_array(subfigs) else [subfigs]
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
            features : tuplargs,
            histvars:tuplargs = tuplargs(TransformParam(so.Bars(),so.Hist())),
            kdevars:tuplargs=tuplargs(TransformParam(so.Line(),so.KDE())),
            percentiles:tuplargs = tuplargs([25.0,75.0]),
            percboxvars : tuplargs = tuplargs(dictargs(color='cyan',linewidth=2)),
            outlierrangevars : tuplargs = tuplargs(dictargs(color='magenta',linewidth=2,linestyle = '-.')),
            meanvars:tuplargs = tuplargs(dictargs(color='red',linestyle='--')),
            medianvars:tuplargs = tuplargs(dictargs(color='k',linestyle =':')),
            updateparams:tuplargs = tuplargs(),
            globalupdates:tuplargs = tuplargs(),
            showkde = tuplargs(False),
            showpercbox = tuplargs(False),
            showoutlierrange = tuplargs(False),
            showstatlines = tuplargs(False),
            figsize = (6.4,4.8),
            layout = 'tight',
            wrap = 3,
            ):
    
    #validate
    if(len(plotparam.kwargs)!= 2 or 'data' not in plotparam.kwargs):
        (
            Interrupter('Along with data parameter, only one of x or y variable required with any value, to determine the orientation.',log= True,throw=True)
            .adddata(file = getframeinfo(currentframe()).filename)
            .adddata(lineno = getframeinfo(currentframe()).lineno)
            .act()
        )
    #param
    max_length = len(features.args)
    features = parametize_tuplargs(features,None,max_length)
    histvars = parametize_tuplargs(histvars,TransformParam(so.Bars(),so.Hist()),max_length)
    kdevars = parametize_tuplargs(kdevars,TransformParam(so.Line(),so.KDE()),max_length)
    percentiles = parametize_tuplargs(percentiles,[25.0,75.0],max_length)
    percboxvars = parametize_tuplargs(percboxvars,dictargs(color='cyan',linewidth=2),max_length)
    outlierrangevars = parametize_tuplargs(outlierrangevars,dictargs(color='magenta',linewidth=2,linestyle = '-.'),max_length)
    meanvars = parametize_tuplargs(meanvars,dictargs(color='red',linestyle='--'),max_length)
    medianvars = parametize_tuplargs(medianvars,dictargs(color='k',linestyle = ':'),max_length)
    updateparams = parametize_tuplargs(updateparams,tuplargs(),max_length)
    showkde = parametize_tuplargs(showkde,False,max_length)
    showpercbox = parametize_tuplargs(showpercbox,False,max_length)
    showoutlierrange = parametize_tuplargs(showoutlierrange,False,max_length)
    showstatlines = parametize_tuplargs(showstatlines,False,max_length)
    #data
    #temp_plotparam = kwargsbase(**plotparam.kwargs)
    #data = temp_plotparam.popval('data')
    #axis,feature = temp_plotparam.kwargs.popitem()
    #otheraxis = 'y' if axis == 'x' else 'x'
    #temp_plotparam.kwargs[axis] = feature
    #temp_plotparam.kwargs[otheraxis] = np.full(data.shape[0],'obs')
    #temp_plotparam.kwargs['data'] = data


    temp_plotparam = dictargs(**plotparam.kwargs)
    data = temp_plotparam.popvals('data')
    xval,yval = temp_plotparam.popvals('x','y')
    if xval and yval:
        (
            Interrupter(message='Along with data parameter, only one of x or y variable required with any value, to determine the orientation.',log= True,throw=True)
            .addkvps(file = getframeinfo(currentframe()).filename)
            .addkvps(lineno = getframeinfo(currentframe()).lineno)
            .act()
        )
    axis = 'x' if xval else 'y'
    feature = xval if xval else yval

    #grid
    nrows = 1
    ncols = ncols=wrap if max_length > wrap else max_length
    for i in range(0,max_length):
        if(i>= wrap and i % wrap == 0):
            nrows+=1 
    fig = plt.figure(figsize=figsize,layout = layout)
    subfigs = fig.subfigures(nrows,ncols)    
    subfigs =  subfigs.flatten() if hasattr(subfigs,'flatten') else subfigs if is_array(subfigs) else [subfigs] 
    #plot
    for _i, (_feature, _subfig) in enumerate(zip(features,subfigs)):
        plotparam.kwargs[axis] = _feature
        hst = SoPlot(plotparam=plotparam)
        hst = hst.design(histvars[_i])
        if showkde[_i]:
            hst = hst.addLayer(kdevars[_i])
        hst = hst.update(*globalupdates)
        hst = hst.update(*updateparams[_i])
        hst = hst.plot(target=_subfig)
       #lines
        for ax in _subfig.axes:
            if showstatlines[_i]:
                ax.axvline(np.mean(data[_feature]),**meanvars[_i]) if axis == 'x' else\
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
                lower,upper = get_outlier_boundpairs(data[_feature],tuplargs(percs)).args[0]
                ax.axvline(lower,**outlierrangevars.args[_i].kwargs) if axis == 'x' else\
                ax.axhline(lower,**outlierrangevars.args[_i].kwargs)
                ax.axvline(upper,**outlierrangevars.args[_i].kwargs) if axis == 'x' else\
                ax.axhline(upper,**outlierrangevars.args[_i].kwargs)
    
    return fig

def multi_plot(
        plotparam:PlotParam,
        features:tuplargs,
        designparams:tuplargs,
        layerparams:tuplargs = None,
        updateparams:tuplargs = tuplargs(),
        globalupdates:tuplargs = tuplargs(),
        figsize = None,
        layout = 'tight',
        wrap = 3,
        ):
    
    #param
    max_length = len(features.args)
    features = parametize_tuplargs(features,None,max_length)
    layerparams = parametize_tuplargs(layerparams,tuplargs(),max_length)
    designparams = parametize_tuplargs(designparams,None,max_length)
    updateparams = parametize_tuplargs(updateparams,tuplargs(),max_length)
    #data
    temp_plotparam = dictargs(**plotparam.kwargs)    
    temp_plotparam.popkvps('data')
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
    subfigs =  subfigs.flatten() if hasattr(subfigs,'flatten') else subfigs if is_array(subfigs) else [subfigs]
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
