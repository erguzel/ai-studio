import seaborn as sns
import seaborn.objects as so
import matplotlib.pyplot as plt
from matplotlib.colors import is_color_like
import numpy as np
from exchelp.exception_helper import *

import aistudio.runtime.runtime_utils as ru
import aistudio.statistics.stats_utils as su




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

################################
################################

class kwargsbase(object):
    def __init__(self,**kwargs):
        self.kwargs = kwargs

    def rmv(self,*keys):
        for key in keys:
            if key in self.kwargs:
                self.kwargs.pop(key)


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

# TODO: check overriding params in add behaves

class SoPlotter():
    #__plotparam__ = None
    #__plot__ = None
    #__plotter__ = None
    #__figure__ = None
    #__axes__ = None

    def __init__(self,plotparam:PlotParam):
        self.__plotparam__ = plotparam
        #self.__plot__ = so.Plot(**plotparam.kwargs)

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
                pass# TODO
        
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

def boxplot(plotparam:PlotParam,
            percentile = [25.0,75.0],
            **boxplotvariables:kwargsbase ):
    """
    obsvars:kwargsbase = kwargsbase(pointsize=0.5),
    jittervars:kwargsbase = kwargsbase(width=0.5),
    boxvars : kwargsbase = kwargsbase(color='k',linewidth=15),
    outliervars:kwargsbase = kwargsbase(color='r',linewidth=5),
    meanvars :kwargsbase = kwargsbase(color='green',linestyle='--'),
    medianvars:kwargsbase = kwargsbase(color='gold'),
    segmentvars:kwargsbase = kwargsbase()):
    """

    ##TODO check only x or y provided

    temp_plotparam = kwargsbase(**plotparam.kwargs)
    data = temp_plotparam.kwargs['data']    
    temp_plotparam.rmv('data')
    axis,feature = temp_plotparam.kwargs.popitem()
    otheraxis = 'y' if axis == 'x' else 'x'
    plotparam.kwargs[otheraxis] = np.full(data.shape[0],'obs')

    obsvars = boxplotvariables['obsvars'] if 'obsvars' in boxplotvariables else  kwargsbase(pointsize=0.5)
    jittervars = boxplotvariables['jittervars'] if 'jittervars' in boxplotvariables else  kwargsbase(width=0.5)
    boxvars= boxplotvariables['boxvars'] if 'boxvars' in boxplotvariables else  kwargsbase(color='k',linewidth=15)
    outliervars= boxplotvariables['outliervars'] if 'outliervars' in boxplotvariables else  kwargsbase(color='r',linewidth=5)
    meanvars= boxplotvariables['meanvars'] if 'meanvars' in boxplotvariables else  kwargsbase(color='red',linestyle='--')
    medianvars= boxplotvariables['medianvars'] if 'medianvars' in boxplotvariables else  kwargsbase(color='k')
    segmentvars= boxplotvariables['segmentvars'] if 'segmentvars' in boxplotvariables else  kwargsbase()


    sp =  SoPlotter(
              plotparam=plotparam
                      ).design(
            TransformParam( ## observation points
            so.Dot(**obsvars.kwargs),so.Jitter(**jittervars.kwargs),**segmentvars.kwargs,
            )
        ).addLayer(## percentile box
            TransformParam(
            so.Range(**boxvars.kwargs),so.Perc(percentile)
            )
        ).addLayer( ## outlier range
            TransformParam(
            so.Range(**outliervars.kwargs), so.Perc(su.get_outlier_range(data[feature],percentile))
            )
        ).addLayer(## outlier range ends
            TransformParam(
            so.Dash(**outliervars.kwargs),so.Perc(su.get_outlier_range(data[feature],percentile))
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
    
def boxplot_hist(
        plotparam:PlotParam,
        *updateparams:kwargsbase,
        percentile=[25,75],
        figsize = (6.4,4.8), 
        **boxplotvariables:kwargsbase
        ):
    """
    updateparams: kwargsbase i.e LayoutParam(), ScaleParam() etc

    boxplot variables :
    obsvars:kwargsbase = kwargsbase(pointsize=0.5),
    jittervars:kwargsbase = kwargsbase(width=0.5),
    boxvars : kwargsbase = kwargsbase(color='k',linewidth=15),
    outliervars:kwargsbase = kwargsbase(color='r',linewidth=5),
    meanvars :kwargsbase = kwargsbase(color='green',linestyle='--'),
    medianvars:kwargsbase = kwargsbase(color='gold'),
    segmentvars:kwargsbase = kwargsbase()):
    """

    ## TODO check only x or y allowed

    fig = plt.figure(figsize=figsize)
    sfigs = fig.subfigures(2,1)
    linedata = kwargsbase(**plotparam.kwargs)    
    data = linedata.kwargs['data']
    linedata.rmv('data')
    axis,feature = linedata.kwargs.popitem()

    hst = SoPlotter(plotparam=plotparam)
    hst = hst.design(TransformParam(so.Bars(),so.Hist()))
    hst = hst.update(*updateparams) if len(updateparams) > 0 else hst
    hst = hst.plot(target=sfigs[1],pyplot=True)
    for ax in sfigs[1].axes:
        ax.axvline(np.mean(data[feature]),color='red',linestyle = '--') if axis == 'x' else\
        ax.axhline(np.mean(data[feature]),color='red',linestyle = '--')
        ax.axvline(np.median(data[feature]),color='k',linestyle = '-') if axis == 'x' else\
        ax.axhline(np.median(data[feature]),color='k',linestyle = '-')
 
    bp = boxplot(plotparam=plotparam,percentile=percentile,**boxplotvariables)
    bp = bp.update(*updateparams) if len(updateparams) > 0 else bp
    bp = bp.plot(target=sfigs[0],pyplot=True)
   
    return fig

def multi_boxplot_hist(
            plotparam:PlotParam,
            features:list[str],
            updateparams:list[kwargsbase],
            boxplotvariables:list[kwargsbase],
            percentile=[25,75],
            figsize = (6.4,4.8),
            wrap = 3,
            ):
    """
    updateparams: kwargsbase i.e LayoutParam(), ScaleParam() etc

    boxplot variables :
    obsvars:kwargsbase = kwargsbase(pointsize=0.5),
    jittervars:kwargsbase = kwargsbase(width=0.5),
    boxvars : kwargsbase = kwargsbase(color='k',linewidth=15),
    outliervars:kwargsbase = kwargsbase(color='r',linewidth=5),
    meanvars :kwargsbase = kwargsbase(color='green',linestyle='--'),
    medianvars:kwargsbase = kwargsbase(color='gold'),
    segmentvars:kwargsbase = kwargsbase()):
    """
    nrows = 1
    ncols = ncols=wrap if len(features) > wrap else len(features)
    for i in range(0,len(features)):
        if(i>= wrap and i % wrap == 0):
            nrows+=1 


    fig = plt.figure(figsize=figsize)
    sfigs = fig.subfigures(nrows,ncols)
    linedata = kwargsbase(**plotparam.kwargs)    
    data = linedata.kwargs['data']
    linedata.rmv('data')
    axis,feature = linedata.kwargs.popitem()
    
    for i in range(0,nrows):
        for j in range(0,ncols):
            sfig = sfigs[i,j]
            raise TypeError('Not implemented yet') ##TODO



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
