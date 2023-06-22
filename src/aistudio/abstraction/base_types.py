################################

class baseall(object):
    def __init__(self) -> None:
        self.masterparam = False
    def masterparam(self,ismasterparam:bool):
        self.masterparam = ismasterparam
        return self


class kwargsbase(baseall):
    def __init__(self,**kwargs):
        self.kwargs = kwargs

    def rmv(self,*keys):
        for key in keys:
            if key in self.kwargs:
                self.kwargs.pop(key)

class argsbase(baseall):
    def __init__(self,*args):
        self.args = args

class argskwargssbase(argsbase,kwargsbase):
    def __init__(self,*args,**kwargs):
        argsbase.__init__(self,*args)
        kwargsbase.__init__(self,**kwargs)  

# plot
# argskwargsbase
class PlotParam(argskwargssbase):
    def __init__(self,*args, **kwargs):
        argsbase.__init__(self,*args)
        kwargsbase.__init__(self,**kwargs)
            
# Design
# Layer
# argskwargsbase
class TransformParam(argskwargssbase):
    def __init__(self,*args,**kwargs):
        argsbase.__init__(self,*args)
        kwargsbase.__init__(self,**kwargs)

##Update
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
# update
# argsbase
class ThemeParam(argsbase):
    def __init__(self,*args):
        super().__init__(*args) 

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
                print('TODO line 158 ',__file__)
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

### Parametization

def parametize_argsbase(
        param_arg:argsbase,
        defaultvalue,
        maxlength=-1,
        numofreplication=0,
        filllast = False
        )-> argsbase:

    #None case
    result = []
    if not param_arg:
        for i in range(numofreplication):
            result[i] = defaultvalue
        return argsbase(*result)
    
    lenargs = len (param_arg.args)

    # replace Nones with default
    for j in range(numofreplication):
        arg = param_arg.args[j] if j < lenargs else defaultvalue
        arg = arg if arg else defaultvalue
        result[j] = arg

    return argsbase(*result)
        



