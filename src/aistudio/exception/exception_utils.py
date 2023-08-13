import sys
import json
from json import JSONEncoder
import copy
import numpy as np

from aistudio.abstraction.base_types import *

class JsonEncoders():
    def __init__(self) -> None:
        pass
    
    class DefaultJsonEncoder(JSONEncoder):
        def default(self,o):
            try:
                if is_jsondumpable(o) :return o 
                if isinstance(o,bytes):
                    return self.default(o=str(o))
                if isinstance(o,bytearray):
                    return self.default(o=str(bytes(o)))
                if isinstance(o,set):
                    return self.default(o=list(o))
                #
                if isinstance(o, JSNode):
                    return self.default(o = o.__data__)
                #
                if isinstance(o,dictargs):
                    return self.default(o = o.kwargs)
                #
                if isinstance(o,tuplargs):
                    return self.default(o=list(o.args))
                
                if hasattr(o,'__dict__'):
                    if isinstance(o,BaseException):
                        o.__dict__['_repr']=repr(o)
                    return self.default(o=o.__dict__)
                if isinstance(o,tuple):
                    return self.default(o=list(o))
                if isinstance(o,np.ndarray):
                    return self.default(o = list(o))
                ## try iterate
                try:
                    for idx, el in enumerate(o):
                        isDict = isinstance(o,dict)
                        val = o[el] if isDict else o[idx]
                        val = self.default(o=val)
                        o[el if isDict else idx] = val
                    o = self.default(o=o)
                except Exception as e:## not iterable meaning unguessed type
                    o = self.default(o='<not-serializable>')
                return o
            except Exception as e:
                raise TypeError('dictionarize_data failed',e)
            


def is_jsondumpable(data)->bool:
    try:
        json.dumps(data)
        return True
    except:
        return False


def jsonize(data,verbose = False,fullsavename = None, encoder =JsonEncoders.DefaultJsonEncoder,indent = 2):
        js = json.dumps(data,cls = encoder,indent=indent)
        if verbose:
            print(js)
        if fullsavename:
            with open(fullsavename, 'w') as f:
                f.write(js)
        return js

def is_array(variable):
    return isinstance(variable, list)  or isinstance(variable,np.ndarray)

def parametize_tuplargs(
        param_arg:tuplargs,
        defaultvalue,
        numofreplication=0,
        metavals = tuplargs('_masterparam','masterparam','__masterparam__','__masterparam'),
        )-> tuplargs:

    #None case
    result = []
    if not param_arg:
        [result.append(defaultvalue) for i in range(numofreplication)]
        return tuplargs(*result)

    if  isinstance(param_arg,argsbase):
        if any(param_arg.isin(*metavals.args)):
            if is_subtypeof(param_arg,tuplargs):
                param_arg.rmvelms(*metavals.args)
            if is_subtypeof(param_arg,dictargs):
                param_arg.popvals(*metavals.args)

            [result.append(param_arg) for i in range(numofreplication)]
            return tuplargs(*result)
    else:
        [result.append(param_arg) for i in range(numofreplication)]
        return tuplargs(*result)
    
    lenargs = len(param_arg)

    # replace Nones with default
    (
        [result.append(param_arg[j] if param_arg[j] else defaultvalue)
          if j < lenargs else result.append(defaultvalue)
            for j in range(numofreplication)]
    )
    
    return tuplargs(*result)
    

def is_typeof (instance, *types)->bool:
    """
    Checks the type of given instance is among the types provided.
    Does not check inner element types.
    
    Args:
        instance (Any): Instance variable
        *types (Type): a series of types i.e str,int,list

    Returns:
        bool: True if the instance type in types
    """
    for typ in types:
        if type(instance) == typ:
            return True
    return False

def is_subtypeof(instance, *types)->bool:
    """
    Checks given instance type is type or a subtype of the given types

    Args:
        instance (Any): Instance variable
        *types (Type): a series of types i.e. str, int, dict

    Returns:
        bool: True if given instance type is among the given type args, or instance type is a subtype of given types
    """
    for typ in types:
        if isinstance(instance,typ):
            return True
    return False



class JSNode():
    def __init__(self, **kwargs) -> None:
        self.__data__ = dictargs(**kwargs)
    def update(self,**kwargs):
        #self.__dict__ = self.__dict__ | kwargs
        self.__data__.addkvps(**kwargs)
        #for k,v in kwargs.items():
        #    self.__data__[k] = v if is_typeof(Reporter) else v.__dict__ if hasattr(v,'__dict__') else v
        return self
    def get_property(self, key):
        if key not in self.__data__:
            raise KeyError('Given key {} does not exists in the Reporter object'.format(key))
        return self.__data__[key]

    def del_property(self,key):
        if key not in self.__data__:
            raise KeyError('Given key {} does not exists in the Reporter object'.format(key))
        self.__data__.popkvps(key)
        return self
    
    def toJson(self,verbose = True):
        
        data = copy.deepcopy(self)
        js = json.dumps(data,cls = JsonEncoders.DefaultJsonEncoder,indent=2)
        if verbose:
            print(js)
        else:return js


class Interrupter(dictuplargs,Exception,BaseException):

    def __init__(self, *args, **kwargs):
        """
            Thrown in try block when an exception case caught.
        
            kwargs:
            log: logs exception as serialized json
            exit: exits app before throwing actual exception
            throw: throws actual exception
        """
        super().__init__(*args, **kwargs)

    def act(self, innerexception=None):
        """Orders final action of the exception according to previously given kwargs.

        Returns:
            None: Depending on given kwargs, perform log, exit, throw actions
        """
        acceptedactions = ('True','true','TRUE', True)

        if 'log' in self.kwargs:
            if  self.kwargs['log'] in acceptedactions:
                print(json.dumps(self,cls=JsonEncoders.DefaultJsonEncoder,indent=2))
        if 'exit' in self.kwargs:
            if self.kwargs['exit'] in acceptedactions:
                sys.exit('System is interrupted with a raised interruption object. Program is ended by user before raising the actual exception.')
        if 'throw' in self.kwargs:
            if self.kwargs['throw'] in acceptedactions:
                raise (innerexception if innerexception else self)

class InterruptPatcher(Interrupter):
    def __init__(self, *args, **kwargs):
        """
            Thrown in catch block to control the caught exceptions further.
        
            kwargs:
            log: logs exception as serialized json
            exit: exits app before throwing actual exception
            throw: throws actual exception
        """
        super().__init__(*args, **kwargs)

    def act(self,innerexception):
        """Orders final action of the exception according to previously given kwargs.

        Args:
            innerexception (BaseException): Inner exception caught in catch block

        Returns:
            None: Depending on given kwargs, perform log, exit, throw actions
        """
        self.innerexception = innerexception
        return super().act(innerexception=innerexception)


